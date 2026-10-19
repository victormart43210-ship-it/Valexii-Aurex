"""The offline checker is source-bound and must never mint release authority."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def preflight():
    path = Path(__file__).resolve().parents[1] / "scripts" / "offline_preflight.py"
    spec = importlib.util.spec_from_file_location("_aurex_offline_preflight", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("step_state", "expected"), [("PASS", "PASS"), ("FAIL", "FAIL"), ("NOT RUN", "FAIL")]
)
def test_manifest_never_self_admits(preflight, step_state, expected):
    manifest = preflight.result_manifest(
        sha="a" * 40,
        tree="b" * 40,
        branch="test",
        steps=[{"status": step_state}],
        clean_after=True,
        docker_requested=False,
    )
    assert manifest["local_checks"] == expected
    assert manifest["release_gate"] == "HOLD"
    assert manifest["release_authority"] == "NONE"
    assert manifest["github_actions_verification"] == "NOT VERIFIED"
    assert manifest["independent_verification"] == "NOT VERIFIED"


def test_dirty_worktree_cannot_pass(preflight):
    manifest = preflight.result_manifest(
        sha="a" * 40,
        tree="b" * 40,
        branch="test",
        steps=[{"status": "PASS"}],
        clean_after=False,
        docker_requested=False,
    )
    assert manifest["local_checks"] == "FAIL"


def test_secret_scrubbing(preflight, monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "private-value")
    monkeypatch.setenv("OPENAI_API_KEY", "private-value")
    monkeypatch.setenv("RAILWAY_TOKEN", "private-value")
    env = preflight.safe_environment()
    assert "AUREX_SERVICE_TOKEN" not in env
    assert "OPENAI_API_KEY" not in env
    assert "RAILWAY_TOKEN" not in env
    assert env["AUREX_WORKER_DISABLED"] == "1"
    assert env["AUREX_ENABLE_OFFLINE_LAB"] == "0"


def test_local_check_records_log_hash_without_code_admission(preflight, tmp_path):
    result = preflight.run_check(
        label="smoke",
        command=[sys.executable, "-c", "print('test ok')"],
        root=tmp_path,
        output_dir=tmp_path,
        timeout=10,
        env=preflight.safe_environment(),
    )
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert len(result["log_sha256"]) == 64


def test_changed_git_file_is_detected(preflight, tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "tracked.txt").write_text("first", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.name=fixture",
         "-c", "user.email=fixture@example.invalid", "commit", "-qm", "first"],
        check=True,
    )
    assert preflight.clean_checkout(tmp_path) is True
    (tmp_path / "tracked.txt").write_text("second", encoding="utf-8")
    assert preflight.clean_checkout(tmp_path) is False
