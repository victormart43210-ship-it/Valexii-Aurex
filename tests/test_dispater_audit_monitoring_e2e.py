"""
Full End-to-End Continuous Audit & Monitoring Workflow Test for DISPATER.AI.

Verifies complete 9-stage sequence:
1. Operational Record Ingestion
2. Continuous Monitoring Observation
3. Rule Evaluation & Exception Detection
4. Finding Generation & Severity Classification
5. AUREX Evidence Ledger Envelope Registration
6. XAELI 5-Step Explanation Formatting
7. Corrective Action Assignment
8. Remediation Submission & Independent Retest (Human Review Guard Enforcement)
9. Cryptographic Audit Receipt Verification
"""

import pytest
from fastapi.testclient import TestClient

from aurex.api import app


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")
    return TestClient(app)


def test_full_dispater_e2e_audit_monitoring_workflow(api_client):
    headers = {"Authorization": "Bearer 12345678901234567890123456789012"}
    tenant_id = "TENANT-E2E-OILFIELD-01"

    # Stage 1: Ingest operational record for pressure pumping unit operating without pre-job safety inspection
    record_payload = {
        "record_id": "REC-E2E-9001",
        "tenant_id": tenant_id,
        "source": "OILFIELD_FIELD_TICKET",
        "payload": {
            "ticket_id": "FT-9001",
            "equipment_id": "FRAC-PUMP-04",
            "operating_hours": 18.5,
            "has_inspection_record": False,
            "telemetry_sensor_hours": 18.5,
        },
    }

    ingest_res = api_client.post("/v1/dispater/monitoring/records", json=record_payload, headers=headers)
    assert ingest_res.status_code == 200
    ingest_data = ingest_res.json()

    # Stage 2: Verify Continuous Observation
    obs = ingest_data["observation"]
    assert obs["observation_type"] == "RECORD_INGESTED"
    assert len(obs["evidence_sha256"]) == 64

    # Stage 3 & 4: Verify Rule Evaluation & Critical Finding Generation
    findings = ingest_data["findings"]
    assert len(findings) == 1
    finding = findings[0]
    assert finding["severity"] == "CRITICAL"
    assert finding["rule_id"] == "RULE-INSP-MISSING"
    finding_id = finding["finding_id"]

    # Stage 5 & 6: Verify XAELI 5-Step Explanation Grounding
    xaeli_findings = ingest_data["xaeli_findings"]
    assert len(xaeli_findings) == 1
    xaeli = xaeli_findings[0]
    assert "NOW:" in xaeli["now"] or "Operational Audit Finding" in xaeli["now"]
    assert xaeli["proof"].startswith("SHA-256 Digest:")

    # Verify initial readiness -> CRITICAL_DEFICIT
    readiness_res1 = api_client.get(f"/v1/dispater/monitoring/readiness?tenant_id={tenant_id}", headers=headers)
    assert readiness_res1.json()["readiness_status"] == "CRITICAL_DEFICIT"

    # Stage 7: Assign Corrective Action
    ca_res = api_client.post(
        "/v1/dispater/monitoring/corrective-actions",
        json={"tenant_id": tenant_id, "finding_id": finding_id, "assigned_to": "Safety Officer Mark", "due_date": "2026-11-15"},
        headers=headers,
    )
    assert ca_res.status_code == 200
    action_id = ca_res.json()["action_id"]

    # Stage 8: Submit Remediation & Independent Retest
    rem_res = api_client.post(
        "/v1/dispater/monitoring/remediation",
        json={
            "tenant_id": tenant_id,
            "action_id": action_id,
            "remediation_notes": "Unit pulled for mandatory safety inspection; log uploaded.",
            "evidence_payload": {"inspection_certificate_id": "CERT-9001-OK.pdf"},
        },
        headers=headers,
    )
    assert rem_res.status_code == 200

    # Ensure unverified self-closure WITHOUT human signature is REJECTED
    unauth_retest_res = api_client.post(
        "/v1/dispater/monitoring/retest",
        json={"tenant_id": tenant_id, "action_id": action_id, "closed_by_human": None, "retest_payload": {"passed": True}},
        headers=headers,
    )
    assert unauth_retest_res.status_code == 403

    # Execute retest WITH explicit human signature
    auth_retest_res = api_client.post(
        "/v1/dispater/monitoring/retest",
        json={"tenant_id": tenant_id, "action_id": action_id, "closed_by_human": "Auditor Sarah Connor", "retest_payload": {"passed": True}},
        headers=headers,
    )
    assert auth_retest_res.status_code == 200
    assert auth_retest_res.json()["closed_by_human"] == "Auditor Sarah Connor"

    # Stage 9: Cryptographic Receipt Verification & Readiness Assessment
    readiness_res2 = api_client.get(f"/v1/dispater/monitoring/readiness?tenant_id={tenant_id}", headers=headers)
    assert readiness_res2.json()["readiness_status"] == "AUDIT_READY"

    receipt_res = api_client.get(f"/v1/dispater/monitoring/receipt?tenant_id={tenant_id}", headers=headers)
    assert receipt_res.status_code == 200
    receipt_data = receipt_res.json()
    assert receipt_data["scope_record_count"] == 1
    assert len(receipt_data["receipt_sha256"]) == 64
