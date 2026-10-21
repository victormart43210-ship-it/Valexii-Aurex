"""Deterministic synthetic-only pilot admission tests."""
import copy
import json
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path

import pytest
from workstation.field_pilot_admission import GATES, SCHEMA, evaluate, load, main

NOW = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)


def sample():
    return {
        "schema": SCHEMA,
        "pilot_id": "synthetic-pilot-001",
        "model_mode": "deterministic_only",
        "owner": "founder",
        "implementer": "engineering-agent",
        "checks": [{
            "id": gate,
            "status": "PASS",
            "evidence_sha256": sha256(gate.encode()).hexdigest(),
            "evidence_ref": f"independent-audit://witness/{gate}",
            "reviewer": "independent-auditor",
            "reviewed_at": NOW.isoformat(),
        } for gate in GATES]
    }


def test_all_declared_pass_still_never_authorizes():
    result = evaluate(sample(), now=NOW)
    assert result["blocking_gates"] == []
    assert result["assessment"] == "INDEPENDENT_ADMISSION_REVIEW_REQUIRED"
    assert result["actual_customer_data_handling_authorized"] is False
    assert result["customer_contract_executed"] is False
    assert result["production_release"] == "HOLD"
    assert result["payment_or_billing_authority"] == "NONE"


def test_missing_ci_is_hold():
    data = sample()
    data["checks"][0]["status"] = "NOT_VERIFIED"
    result = evaluate(data, now=NOW)
    assert result["assessment"] == "HOLD"
    assert result["blocking_gates"][0] == {"gate": "EXACT_HEAD_CI", "reason": "NOT_VERIFIED"}


def test_unverified_security_stays_hold_even_if_other_checks_pass():
    data = sample()
    next(r for r in data["checks"] if r["id"] == "INDEPENDENT_SECURITY_REVIEW")["status"] = "HOLD"
    assert evaluate(data, now=NOW)["assessment"] == "HOLD"


def test_self_witness_is_rejected():
    data = sample()
    data["checks"][0]["reviewer"] = data["implementer"]
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "REVIEWER_NOT_SEPARATE"


def test_owner_cannot_approve_own_check():
    data = sample()
    data["checks"][0]["reviewer"] = data["owner"]
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "REVIEWER_NOT_SEPARATE"


def test_stale_ci_is_rejected():
    data = sample()
    data["checks"][0]["reviewed_at"] = (NOW - timedelta(days=8)).isoformat()
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "WITNESS_STALE"


def test_future_witness_rejected():
    data = sample()
    data["checks"][0]["reviewed_at"] = (NOW + timedelta(hours=1)).isoformat()
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "WITNESS_IN_FUTURE"


def test_naive_witness_rejected():
    data = sample()
    data["checks"][0]["reviewed_at"] = "2026-10-20T12:00:00"
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "WITNESS_TIME_NOT_AWARE"


def test_reject_missing_or_duplicate_checks():
    data = sample()
    data["checks"].pop()
    with pytest.raises(ValueError, match="statuses"):
        evaluate(data, now=NOW)
    data = sample()
    data["checks"][1] = copy.deepcopy(data["checks"][0])
    with pytest.raises(ValueError, match="repeated"):
        evaluate(data, now=NOW)


def test_reject_forbidden_model_mode():
    data = sample()
    data["model_mode"] = "autonomous_payments"
    with pytest.raises(ValueError, match="metadata"):
        evaluate(data, now=NOW)


def test_reject_blank_evidence():
    data = sample()
    data["checks"][0]["evidence_sha256"] = ""
    assert evaluate(data, now=NOW)["blocking_gates"][0]["reason"] == "MISSING_OR_INVALID_WITNESS"


def test_json_duplicate_keys_and_symlink_rejected(tmp_path: Path):
    src = tmp_path / "original.json"
    src.write_text('{"schema":"x","schema":"y"}')
    with pytest.raises(ValueError, match="duplicate"):
        load(src)
    link = tmp_path / "link.json"
    link.symlink_to(src)
    with pytest.raises(ValueError, match="symlink"):
        load(link)


def test_cli_never_authorizes_on_invalid_check(tmp_path: Path, capsys):
    src = tmp_path / "manifest.json"
    data = sample()
    data["checks"][0]["status"] = "FAIL"
    src.write_text(json.dumps(data))
    assert main(["--manifest", str(src)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["assessment"] == "HOLD"
    assert result["production_release"] == "HOLD"


def test_cli_broken_json_fail_closed(tmp_path: Path, capsys):
    src = tmp_path / "broken.json"
    src.write_text("not-json")
    assert main(["--manifest", str(src)]) == 2
    assert json.loads(capsys.readouterr().out)["assessment"] == "HOLD_INVALID_INPUT"


def test_all_authority_stays_none_when_deterministic():
    data = sample()
    data["model_mode"] = "qwen_advisory"
    out = evaluate(data, now=NOW)
    assert out["production_release"] == "HOLD"
    assert out["payment_or_billing_authority"] == "NONE"
    assert out["external_spend_usd"] == 0


def test_malformed_nested_status_fails_closed():
    data = sample()
    data["checks"][0]["status"] = ["PASS"]
    with pytest.raises(ValueError, match="gate/status"):
        evaluate(data, now=NOW)


def test_deep_nested_manifest_fails_closed_not_crash(tmp_path: Path, capsys):
    src = tmp_path / "deep.json"
    src.write_text("[" * 12000 + "0" + "]" * 12000)
    assert main(["--manifest", str(src)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["assessment"] == "HOLD_INVALID_INPUT"
    assert result["production_release"] == "HOLD"
