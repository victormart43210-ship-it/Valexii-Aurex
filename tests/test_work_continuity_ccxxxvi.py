"""Recovery failure cases prevent silently unusable savepoints."""

import json
import runpy
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
validate = runpy.run_path(str(ROOT / "scripts/verification/ccxxxvi_resume_check.py"))["validate"]


@pytest.fixture
def recovery(tmp_path):
    source = ROOT / "docs/operations/WORK_CONTINUITY"
    shutil.copytree(source, tmp_path / "docs/operations/WORK_CONTINUITY")
    return tmp_path


def change(root, filename, mutate):
    path = root / "docs/operations/WORK_CONTINUITY" / filename
    value = json.loads(path.read_text())
    mutate(value)
    path.write_text(json.dumps(value))


def test_current_records_are_recoverable():
    assert validate(ROOT) == []


def test_missing_entrypoint_is_reported(recovery):
    (recovery / "docs/operations/WORK_CONTINUITY/RESUME.md").unlink()
    assert "missing recovery file: RESUME.md" in validate(recovery)


def test_task_cycle_is_rejected(recovery):
    change(
        recovery,
        "TASK_LEDGER.json",
        lambda d: d["tasks"][0].update(dependencies=[d["tasks"][0]["task_id"]]),
    )
    assert any("cyclic task dependencies" in e for e in validate(recovery))


def test_unsafe_authority_is_rejected(recovery):
    change(recovery, "CHECKPOINT.json", lambda d: d.update(financial_authority="GRANTED"))
    assert "authority constraint changed" in validate(recovery)


def test_unexecuted_test_cannot_be_pass(recovery):
    change(
        recovery,
        "VERIFICATION.json",
        lambda d: d["records"].append({"status": "PASS", "exit_code": None}),
    )
    assert "PASS record has nonzero or missing exit code" in validate(recovery)


def test_missing_evidence_is_reported(recovery):
    change(
        recovery,
        "VERIFICATION.json",
        lambda d: d["records"].append({"status": "FAIL", "evidence_location": "missing.log"}),
    )
    assert any("missing or outside evidence file: missing.log" == e for e in validate(recovery))


def test_unknown_next_task_dependency_is_reported(recovery):
    change(
        recovery, "TASK_LEDGER.json", lambda d: d["tasks"][0].update(dependencies=["NONEXISTENT"])
    )
    assert "unknown dependency: NONEXISTENT" in validate(recovery)


def test_pass_without_evidence_is_rejected(recovery):
    change(
        recovery,
        "VERIFICATION.json",
        lambda d: d["records"].append({"status": "PASS", "exit_code": 0}),
    )
    assert "PASS record requires evidence location" in validate(recovery)


def test_missing_ledger_cannot_look_complete(recovery):
    change(recovery, "TASK_LEDGER.json", lambda d: d.clear())
    assert "task ledger requires a nonempty tasks list" in validate(recovery)


def test_missing_verification_cannot_look_complete(recovery):
    change(recovery, "VERIFICATION.json", lambda d: d.clear())
    assert "verification requires records list (use empty with NOT_RUN)" in validate(recovery)


def test_wrong_remote_is_rejected_before_fetch(tmp_path):
    import subprocess

    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.invalid/other.git"],
        cwd=tmp_path,
        check=True,
    )
    check_checkout = runpy.run_path(str(ROOT / "scripts/verification/ccxxxvi_resume_check.py"))[
        "check_checkout"
    ]
    assert check_checkout(
        tmp_path,
        {"repository": "https://github.com/victormart43210-ship-it/Valexii-Aurex"},
        "a" * 40,
    ) == ["origin does not match canonical repository"]


def test_optimized_python_cannot_print_false_golden_pass():
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-O",
            str(ROOT / "scripts/verification/ccxxxvi_golden_files.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "do not use python -O" in result.stderr
    assert "PASS" not in result.stdout
