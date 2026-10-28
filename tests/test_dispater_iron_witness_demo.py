"""
OPERATION DISPATER II — PROJECT IRON WITNESS
Demonstration Test & Security Verification Suite.

Validates the complete 12-stage synthetic oilfield audit scenario:
1. Ingest synthetic operational record for hydraulic fracturing pressure pumping unit (FRAC-PUMP-104)
2. Evaluate versioned inspection rule RULE-INSP-MISSING (OSHA 1910.120 / DOT CFR 396)
3. Detect missing inspection evidence
4. Generate CRITICAL audit finding
5. Preserve triggering record payload and SHA-256 evidence digest in EvidenceLedger
6. Display finding and grounded XAELI 5-step explanation (NOW, CHANGED, NEXT, WHY, PROOF)
7. Record corrective action assignment
8. Submit synthetic remediation evidence
9. Enforce independent retest requirement
10. Verify unauthorized AI self-closure attempt fails (HTTP 403 / PermissionError)
11. Close finding only after authorized human reviewer signature
12. Generate cryptographic audit receipt proving immutable audit history
"""

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_contracts import OperationalRecord
from aurex.dispater_monitoring import ContinuousMonitoringEngine


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")
    return TestClient(app)


def test_project_iron_witness_12_stage_demo(api_client):
    headers = {"Authorization": "Bearer 12345678901234567890123456789012"}
    tenant_id = "TENANT-IRON-WITNESS-01"

    # Stage 1: Ingest synthetic operational record for pressure pumping unit missing pre-job safety inspection log
    frac_record = {
        "record_id": "REC-FRAC-104-001",
        "tenant_id": tenant_id,
        "source": "OILFIELD_FIELD_TICKET",
        "payload": {
            "ticket_id": "FT-FRAC-104",
            "equipment_id": "FRAC-PUMP-104",
            "operating_hours": 24.0,
            "has_inspection_record": False,
            "telemetry_sensor_hours": 24.0,
            "well_name": "PERMIAN-ALPHA-WELL-02",
        },
    }

    ingest_res = api_client.post("/v1/dispater/monitoring/records", json=frac_record, headers=headers)
    assert ingest_res.status_code == 200
    ingest_data = ingest_res.json()

    # Stage 2 & 3: Evaluate rule and detect missing inspection evidence
    obs = ingest_data["observation"]
    assert obs["observation_type"] == "RECORD_INGESTED"

    # Stage 4: Generate CRITICAL audit finding
    findings = ingest_data["findings"]
    assert len(findings) == 1
    finding = findings[0]
    assert finding["severity"] == "CRITICAL"
    assert finding["rule_id"] == "RULE-INSP-MISSING"
    assert "FRAC-PUMP-104" in finding["description"]
    finding_id = finding["finding_id"]

    # Stage 5 & 6: Preserve provenance and ground XAELI 5-step explanation
    xaeli_findings = ingest_data["xaeli_findings"]
    assert len(xaeli_findings) == 1
    xaeli = xaeli_findings[0]
    assert "Operational Audit Finding [CRITICAL]" in xaeli["now"]
    assert xaeli["proof"].startswith("SHA-256 Digest:")

    # Verify audit readiness -> CRITICAL_DEFICIT
    readiness_res1 = api_client.get(f"/v1/dispater/monitoring/readiness?tenant_id={tenant_id}", headers=headers)
    assert readiness_res1.json()["readiness_status"] == "CRITICAL_DEFICIT"

    # Stage 7: Record corrective action assignment
    ca_res = api_client.post(
        "/v1/dispater/monitoring/corrective-actions",
        json={
            "tenant_id": tenant_id,
            "finding_id": finding_id,
            "assigned_to": "Field Safety Supervisor Vance",
            "due_date": "2026-11-10",
        },
        headers=headers,
    )
    assert ca_res.status_code == 200
    action_id = ca_res.json()["action_id"]

    # Stage 8: Submit synthetic remediation evidence
    rem_res = api_client.post(
        "/v1/dispater/monitoring/remediation",
        json={
            "tenant_id": tenant_id,
            "action_id": action_id,
            "remediation_notes": "Unit FRAC-PUMP-104 pulled for shop maintenance and certified OSHA safety log attached.",
            "evidence_payload": {
                "inspection_log_id": "INSP-LOG-104-OK",
                "inspector": "Certified Inspector Miller",
                "passed": True,
            },
        },
        headers=headers,
    )
    assert rem_res.status_code == 200
    assert rem_res.json()["retest_status"] == "INDEPENDENT_RETEST_REQUIRED"

    # Stage 9 & 10: Enforce independent retest requirement and REJECT unauthorized self-closure
    unauth_retest_res = api_client.post(
        "/v1/dispater/monitoring/retest",
        json={
            "tenant_id": tenant_id,
            "action_id": action_id,
            "closed_by_human": None,
            "retest_payload": {"passed": True},
        },
        headers=headers,
    )
    assert unauth_retest_res.status_code == 403
    assert "AUREX SAFEGUARD: Critical/High finding" in unauth_retest_res.json()["detail"]

    # Stage 11: Close finding ONLY after authorized human reviewer signature
    auth_retest_res = api_client.post(
        "/v1/dispater/monitoring/retest",
        json={
            "tenant_id": tenant_id,
            "action_id": action_id,
            "closed_by_human": "Chief Auditor Sarah Connor",
            "retest_payload": {"passed": True},
        },
        headers=headers,
    )
    assert auth_retest_res.status_code == 200
    assert auth_retest_res.json()["closed_by_human"] == "Chief Auditor Sarah Connor"

    # Stage 12: Generate cryptographic audit receipt proving immutable audit history
    readiness_res2 = api_client.get(f"/v1/dispater/monitoring/readiness?tenant_id={tenant_id}", headers=headers)
    assert readiness_res2.json()["readiness_status"] == "AUDIT_READY"

    receipt_res = api_client.get(f"/v1/dispater/monitoring/receipt?tenant_id={tenant_id}", headers=headers)
    assert receipt_res.status_code == 200
    receipt = receipt_res.json()
    assert receipt["scope_record_count"] == 1
    assert len(receipt["receipt_sha256"]) == 64


def test_negative_security_tampered_evidence_and_missing_retest():
    """Negative security tests for data digest mismatch and invalid corrective action IDs."""
    engine = ContinuousMonitoringEngine()
    tenant_id = "TENANT-NEG-TEST"

    # Record with tampered content_sha256 digest
    tampered_rec = OperationalRecord(
        record_id="REC-TAMPERED-01",
        tenant_id=tenant_id,
        source="OILFIELD_FIELD_TICKET",
        payload={"ticket_id": "FT-BAD", "amount": 5000.0},
        content_sha256="0000000000000000000000000000000000000000000000000000000000000000",
    )
    engine.ingest_record(tampered_rec)
    findings = engine.evaluate_tenant_monitoring(tenant_id)

    # Should detect data quality digest mismatch
    qual_findings = [f for f in findings if f.rule_id == "RULE-DATA-QUALITY"]
    assert len(qual_findings) == 1
    assert qual_findings[0].severity == "MEDIUM"

    # Verify invalid action_id lookup raises ValueError
    with pytest.raises(ValueError) as exc_info:
        engine.submit_remediation_evidence(
            tenant_id, "ACT-NONEXISTENT", "Notes", {"a": 1}
        )
    assert "Corrective action 'ACT-NONEXISTENT' not found" in str(exc_info.value)
