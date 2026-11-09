"""Negative and contract tests: standalone synthetic acceptance tool, no network."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from workstation.field_audit_beta_gate import (
    ALLOWED_FLAGS, RESULT_SCHEMA, load_candidate, main, oracle,
    score_candidate, suite, synthetic_cases,
)


def candidate() -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA,
        "synthetic": True,
        "suite_sha256": suite()["suite_sha256"],
        "results": [
            {"case_id": case_id, "flags": sorted(flags), "authority": "HOLD",
             "independent_verification": "NOT_VERIFIED", "effect": "NONE"}
            for case_id, flags in oracle().items()
        ],
    }


def test_suite_deterministic_counts_and_synthetic_only() -> None:
    cases = synthetic_cases()
    assert len(cases) == len({x["case_id"] for x in cases}) == 100
    assert all(x["synthetic"] is True for x in cases)
    assert sum(bool(flags) for flags in oracle().values()) == 60
    assert sum(len(flags) for flags in oracle().values()) == 70
    assert suite() == suite()
    assert len(suite()["suite_sha256"]) == 64


def test_reference_candidate_passes_synthetic_only() -> None:
    score, ok = score_candidate(candidate())
    assert ok
    assert score["exact_case_matches"] == 100
    assert score["true_positive_flags"] == 70
    assert score["status"] == "SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE"
    assert score["production_readiness"] == "HOLD"
    assert score["independent_verification"] == "NOT_VERIFIED"


def test_false_negative_never_passes() -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    rows[40]["flags"] = []
    report, ok = score_candidate(c)
    assert not ok and report["false_negative_flags"] == 1


def test_false_positive_never_passes() -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    rows[0]["flags"] = ["MISSING_RATE_APPROVAL"]
    report, ok = score_candidate(c)
    assert not ok and report["false_positive_flags"] == 1


def test_missing_case_hold() -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    rows.pop()
    report, ok = score_candidate(c)
    assert not ok and report["missing_cases"] == 1


@pytest.mark.parametrize("key,value", [
    ("authority", "PASS"), ("effect", "PAYMENT_SENT"),
    ("independent_verification", "VERIFIED"),
])
def test_authority_escalation_rejected(key: str, value: str) -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    rows[0][key] = value
    with pytest.raises(ValueError, match="authority or independent"):
        score_candidate(c)


def test_duplicate_case_rejected() -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    rows[1]["case_id"] = rows[0]["case_id"]
    with pytest.raises(ValueError, match="duplicated"):
        score_candidate(c)


def test_unrecognized_flag_and_duplicate_flags_rejected() -> None:
    c = candidate()
    rows = c["results"]
    assert isinstance(rows, list)
    assert "INVOICE_TICKET_VARIANCE" in ALLOWED_FLAGS
    rows[0]["flags"] = ["AUTO_APPROVE"]
    with pytest.raises(ValueError, match="flag"):
        score_candidate(c)
    rows[0]["flags"] = ["DUPLICATE_INVOICE_ID"] * 2
    with pytest.raises(ValueError, match="flag"):
        score_candidate(c)


def test_suite_digest_mismatch_rejected() -> None:
    c = candidate()
    c["suite_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest"):
        score_candidate(c)


def test_file_io_rejects_duplicate_json_keys_and_symlinks(tmp_path: Path) -> None:
    file = tmp_path / "bad.json"
    file.write_text('{"schema":"a", "schema":"b"}', encoding="utf-8")
    with pytest.raises(ValueError, match="invalid candidate JSON"):
        load_candidate(file)
    link = tmp_path / "alias.json"
    link.symlink_to(file)
    with pytest.raises(ValueError, match="non-symlink"):
        load_candidate(link)


def test_cli_no_cost_does_not_self_score_without_candidate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--cases"]) == 0
    exported = json.loads(capsys.readouterr().out)
    assert len(exported["cases"]) == 100
    assert "flags" not in exported["cases"][0]
    report_file = tmp_path / "result.json"
    report_file.write_text(json.dumps(candidate()), encoding="utf-8")
    assert main(["--score", str(report_file)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE"
    report_file.write_text("{}", encoding="utf-8")
    assert main(["--score", str(report_file)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "HOLD"
