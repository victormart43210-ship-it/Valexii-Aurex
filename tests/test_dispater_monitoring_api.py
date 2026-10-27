"""
Unit tests for DISPATER Continuous Monitoring REST API Endpoints.
"""

from fastapi.testclient import TestClient
import pytest

from aurex.api import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")
    return TestClient(app)


def test_monitoring_api_workflow(client):
    headers = {"Authorization": "Bearer 12345678901234567890123456789012"}

    # 1. Ingest record with missing inspection log
    ingest_payload = {
        "record_id": "REC-API-101",
        "tenant_id": "TENANT-API-TEST",
        "source": "OILFIELD_FIELD_TICKET",
        "payload": {
            "equipment_id": "PUMP-UNIT-01",
            "operating_hours": 14.0,
            "has_inspection_record": False,
        },
    }
    res = client.post("/v1/dispater/monitoring/records", json=ingest_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["tenant_id"] == "TENANT-API-TEST"
    assert data["total_findings_count"] == 1
    assert data["findings"][0]["severity"] == "CRITICAL"
    f_id = data["findings"][0]["finding_id"]

    # 2. Get observations
    obs_res = client.get("/v1/dispater/monitoring/observations?tenant_id=TENANT-API-TEST", headers=headers)
    assert obs_res.status_code == 200
    assert obs_res.json()["total_observations_count"] == 1

    # 3. Get readiness assessment
    ready_res = client.get("/v1/dispater/monitoring/readiness?tenant_id=TENANT-API-TEST", headers=headers)
    assert ready_res.status_code == 200
    assert ready_res.json()["readiness_status"] == "CRITICAL_DEFICIT"

    # 4. Assign corrective action
    ca_payload = {
        "tenant_id": "TENANT-API-TEST",
        "finding_id": f_id,
        "assigned_to": "Supervisor Bob",
        "due_date": "2026-11-01",
    }
    ca_res = client.post("/v1/dispater/monitoring/corrective-actions", json=ca_payload, headers=headers)
    assert ca_res.status_code == 200
    ca_id = ca_res.json()["action_id"]

    # 5. Submit remediation
    rem_payload = {
        "tenant_id": "TENANT-API-TEST",
        "action_id": ca_id,
        "remediation_notes": "Inspection completed; unit cleared.",
        "evidence_payload": {"inspection_file": "LOG-1002.pdf"},
    }
    rem_res = client.post("/v1/dispater/monitoring/remediation", json=rem_payload, headers=headers)
    assert rem_res.status_code == 200
    assert rem_res.json()["retest_status"] == "INDEPENDENT_RETEST_REQUIRED"

    # 6. Retest attempt without human signature -> 403 Forbidden
    retest_unauth_payload = {
        "tenant_id": "TENANT-API-TEST",
        "action_id": ca_id,
        "closed_by_human": None,
        "retest_payload": {"passed": True},
    }
    retest_err_res = client.post("/v1/dispater/monitoring/retest", json=retest_unauth_payload, headers=headers)
    assert retest_err_res.status_code == 403

    # 7. Retest attempt WITH human signature -> 200 OK
    retest_auth_payload = {
        "tenant_id": "TENANT-API-TEST",
        "action_id": ca_id,
        "closed_by_human": "Auditor Sarah",
        "retest_payload": {"passed": True},
    }
    retest_ok_res = client.post("/v1/dispater/monitoring/retest", json=retest_auth_payload, headers=headers)
    assert retest_ok_res.status_code == 200
    assert retest_ok_res.json()["closed_by_human"] == "Auditor Sarah"

    # 8. Get receipt
    receipt_res = client.get("/v1/dispater/monitoring/receipt?tenant_id=TENANT-API-TEST", headers=headers)
    assert receipt_res.status_code == 200
    assert receipt_res.json()["scope_record_count"] == 1
    assert len(receipt_res.json()["receipt_sha256"]) == 64
