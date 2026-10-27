"""
Unit tests for DISPATER Continuous Audit Monitoring Engine and AUREX Governance.
"""

from datetime import UTC, datetime
import pytest

from aurex.dispater_contracts import OperationalRecord, AuditRule
from aurex.dispater_monitoring import ContinuousMonitoringEngine


def test_ingest_and_evaluate_missing_inspection():
    engine = ContinuousMonitoringEngine()
    tenant_id = "TENANT-OIL-TEST"

    # Record with missing inspection
    rec = OperationalRecord(
        record_id="REC-101",
        tenant_id=tenant_id,
        source="OILFIELD_FIELD_TICKET",
        payload={
            "ticket_id": "FT-101",
            "equipment_id": "RIG-UNIT-99",
            "operating_hours": 10.0,
            "has_inspection_record": False,
        },
    )

    obs = engine.ingest_record(rec)
    assert obs.observation_type == "RECORD_INGESTED"
    assert len(obs.evidence_sha256) == 64

    findings = engine.evaluate_tenant_monitoring(tenant_id)
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"
    assert findings[0].rule_id == "RULE-INSP-MISSING"

    # Convert to XAELI explanation
    xaeli = engine.convert_findings_to_xaeli(findings)
    assert len(xaeli) == 1
    assert "NOW:" in xaeli[0].now or "Operational Audit Finding" in xaeli[0].now
    assert xaeli[0].proof.startswith("SHA-256 Digest:")


def test_corrective_action_and_human_review_closure_safeguard():
    engine = ContinuousMonitoringEngine()
    tenant_id = "TENANT-TOW-TEST"

    rec = OperationalRecord(
        record_id="REC-TOW-01",
        tenant_id=tenant_id,
        source="TOWING_DISPATCH",
        payload={
            "dispatch_id": "DISP-500",
            "equipment_id": "WRECKER-01",
            "has_inspection_record": False,
        },
    )
    engine.ingest_record(rec)
    findings = engine.evaluate_tenant_monitoring(tenant_id)
    assert len(findings) == 1
    f_id = findings[0].finding_id

    # Assign action
    ca = engine.assign_corrective_action(tenant_id, f_id, "Safety Lead", "2026-11-01")
    assert ca.retest_status == "PENDING"
    assert findings[0].status == "ASSIGNED"

    # Submit remediation
    remediated_ca = engine.submit_remediation_evidence(
        tenant_id, ca.action_id, "Completed OSHA inspection and filed log.", {"log_id": "INSP-FILE-1"}
    )
    assert len(remediated_ca.remediation_evidence_sha256) == 64
    assert findings[0].status == "REMEDIATED"

    # Attempt retest self-closure without human reviewer identification -> MUST FAIL
    retest_rec = OperationalRecord(
        record_id="REC-INSP-RETEST", tenant_id=tenant_id, source="EQUIPMENT_INSPECTION", payload={"verified": True}
    )
    with pytest.raises(PermissionError) as exc_info:
        engine.execute_independent_retest(tenant_id, ca.action_id, retest_rec, closed_by_human=None)
    assert "explicit human reviewer signature for closure" in str(exc_info.value)

    # Execute retest WITH human reviewer signature -> MUST SUCCEED
    closed_ca = engine.execute_independent_retest(
        tenant_id, ca.action_id, retest_rec, closed_by_human="Auditor Jane Doe"
    )
    assert closed_ca.retest_status == "RETEST_PASSED"
    assert closed_ca.closed_by_human == "Auditor Jane Doe"
    assert findings[0].status == "CLOSED"


def test_audit_readiness_assessment_and_receipt():
    engine = ContinuousMonitoringEngine()
    tenant_id = "TENANT-READINESS-TEST"

    rec1 = OperationalRecord(
        record_id="REC-R1", tenant_id=tenant_id, source="PRESSURE_TELEMETRY", payload={"has_inspection_record": True}
    )
    rec2 = OperationalRecord(
        record_id="REC-R2", tenant_id=tenant_id, source="PRESSURE_TELEMETRY", payload={"has_inspection_record": True}
    )
    engine.ingest_record(rec1)
    engine.ingest_record(rec2)
    engine.evaluate_tenant_monitoring(tenant_id)

    readiness = engine.evaluate_audit_readiness(tenant_id)
    assert readiness.total_records_evaluated == 2
    assert readiness.evidence_coverage_pct == 100.0
    assert readiness.open_findings_count == 0
    assert readiness.readiness_status == "AUDIT_READY"

    receipt = engine.generate_audit_receipt(tenant_id)
    assert receipt.scope_record_count == 2
    assert len(receipt.receipt_sha256) == 64
