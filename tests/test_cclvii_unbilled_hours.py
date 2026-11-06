"""Unbilled equipment tickets must establish distinct work before pricing hours."""

import pytest

from aurex.dispater_intelligence import RevenueLeakageEngine, digest


@pytest.mark.parametrize(
    ("tickets", "expected_code", "expected_amount"),
    [
        (["T1", "T2"], "DUPLICATE_FIELD_TICKET", "0.00"),
        (["T2", "T1"], "DUPLICATE_FIELD_TICKET", "0.00"),
        (["T1"], "UNBILLED_EQUIPMENT", "200.00"),
    ],
)
def test_unbilled_equipment_requires_distinct_tickets(
    tickets: list[str], expected_code: str, expected_amount: str
) -> None:
    job = {"job_id": "TOW-3", "customer_id": "C", "service_code": "WINCH", "date": "2026-01-15"}
    rate = {
        "rate_id": "R", "customer_id": "C", "service_code": "WINCH",
        "start": "2026-01-01", "end": "2026-02-01", "unit": "HOUR", "amount": "25",
    }
    equipment = [
        {
            "ticket_id": ticket, "job_id": "TOW-3", "equipment_id": "TRUCK-X",
            "service_date": job["date"], "billable_hours": "8", "standby_hours": "0",
            "invoiced_hours": "8",
        }
        for ticket in tickets
    ]
    report = RevenueLeakageEngine("t").reconcile_records(
        {
            "tenant_id": "t", "dataset_type": "SYNTHETIC_ONLY", "jobs": [job], "rates": [rate],
            "invoices": [], "payments": [], "equipment": equipment,
        }
    )
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == expected_amount
    assert summary["confirmed_recovery_usd"] == "0.00"
    finding, = report["findings"]
    assert finding["code"] == expected_code
    assert finding["authority"] == "HUMAN_REVIEW_REQUIRED"
    if len(tickets) > 1:
        assert finding["qualification"] == "INSUFFICIENT_EVIDENCE"
        assert finding["exposure_usd"] == "0.00"
        assert {ref["record_sha256"] for ref in finding["evidence"]} == {
            digest(row) for row in (job, rate, *equipment)
        }
