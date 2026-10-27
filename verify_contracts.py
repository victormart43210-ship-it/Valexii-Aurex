"""Inline test script to verify dispater_contracts.py schemas."""
from aurex.dispater_contracts import (
    OperationalRecord,
    MonitoringObservation,
    AuditRule,
    AuditFinding,
    CorrectiveAction,
    AuditReadinessAssessment,
    AuditVerificationReceipt,
)

def test_contracts():
    rec = OperationalRecord(record_id="REC-1", tenant_id="T1", source="OILFIELD_FIELD_TICKET", payload={"a": 1})
    assert len(rec.content_sha256) == 64

    obs = MonitoringObservation(observation_id="OBS-1", tenant_id="T1", observation_type="MISSING_INSPECTION")
    assert len(obs.evidence_sha256) == 64

    rule = AuditRule(
        rule_id="R1", domain="SAFETY_COMPLIANCE", title="Pre-Job Inspection",
        description="Must have inspection log", effective_date="2026-01-01", source_reference="OSHA 1910"
    )
    assert rule.is_active is True

    finding = AuditFinding(
        finding_id="F1", rule_id="R1", tenant_id="T1", severity="CRITICAL",
        title="Missing Inspection", description="Unit operating without log"
    )
    assert finding.status == "OPEN"

    action = CorrectiveAction(
        action_id="A1", finding_id="F1", tenant_id="T1", assigned_to="Supervisor", due_date="2026-10-27"
    )
    assert action.retest_status == "PENDING"

    readiness = AuditReadinessAssessment(
        tenant_id="T1", total_records_evaluated=10, evidence_coverage_pct=100.0,
        open_findings_count=0, critical_findings_count=0, overdue_actions_count=0,
        readiness_status="AUDIT_READY"
    )
    assert len(readiness.assessment_sha256) == 64

    receipt = AuditVerificationReceipt(
        receipt_id="RCPT-1", tenant_id="T1", scope_record_count=10, root_evidence_sha256="abc"
    )
    assert len(receipt.receipt_sha256) == 64

    print("ALL DISPATER CONTRACT SCHEMAS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_contracts()
