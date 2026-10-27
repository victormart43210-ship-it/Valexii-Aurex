import pytest
from dispater_operations import detect_unbilled_tickets, detect_maintenance_exceptions, summarize_exceptions


def row(id, **kwargs):
    return {"id": id, "tenant_id": "demo", "synthetic": True, **kwargs}


def test_unbilled_completed_job():
    tickets = [row("T1", status="COMPLETED", estimated_billable_amount="7500.00"), row("T2", status="OPEN")]
    findings = detect_unbilled_tickets("demo", tickets, [])
    assert len(findings) == 1
    assert findings[0].potential_exposure == "7500.00"
    assert findings[0].status == "HUMAN_REVIEW_REQUIRED"


def test_invoiced_job_not_flagged():
    assert detect_unbilled_tickets("demo", [row("T1", status="COMPLETED")], [row("I1", ticket_id="T1")]) == []


def test_maintenance_and_inspection():
    result = detect_maintenance_exceptions("demo", [row("PUMP-1", meter_unit="hours", meter_reading="700", service_due_at="500", inspection_status="MISSING")])
    assert {f.kind for f in result} == {"MAINTENANCE_DUE", "INSPECTION_MISSING"}
    assert len(result[0].evidence_hash) == 64


def test_tenant_isolation():
    with pytest.raises(ValueError):
        detect_unbilled_tickets("demo", [row("T1", tenant_id="other")], [])


def test_exposure_not_double_counted():
    f = detect_unbilled_tickets("demo", [row("T1", status="COMPLETED", estimated_billable_amount="7500.00")], [])[0]
    summary = summarize_exceptions([f, f])
    assert summary["potential_exposure_upper_bound"] == "7500.00"
    assert summary["verified_savings"] is None
