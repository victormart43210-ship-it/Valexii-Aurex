"""Contract tests for the public, fictional industrial-audit demonstration."""
from app import industrial_audit_demo


def test_synthetic_towing_demo_is_fail_closed():
    data = industrial_audit_demo()
    assert data["synthetic"] is True
    assert data["dataClassification"] == "FICTIONAL"
    assert data["sourceVerified"] is False
    assert data["independentVerification"] == "NOT_VERIFIED"
    assert data["auditRuntimeConnected"] is False
    assert data["authority"] == "NONE"
    assert data["release"] == "HOLD"
    assert data["permittedEffects"] == []
    assert data["finding"]["candidateAmountUsd"] == 3850
    assert data["finding"]["confirmedRevenueUsd"] == 0
    assert sum(x["amountUsd"] for x in data["finding"]["charges"]) == 3850
    assert [x["stage"] for x in data["gates"]] == [
        "EVIDENCE", "QUALIFICATION", "REALITY", "AUTHORITY", "EFFECT"
    ]
