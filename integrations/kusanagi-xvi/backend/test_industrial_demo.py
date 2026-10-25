"""Contract tests for the public, fictional industrial-audit demonstration."""
from fastapi.testclient import TestClient

from app import app


def test_synthetic_towing_demo_is_fail_closed():
    response = TestClient(app).get("/v1/demo/industrial-audit")
    assert response.status_code == 200
    data = response.json()
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
