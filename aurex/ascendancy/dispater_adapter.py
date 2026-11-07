"""Run the existing DISPATER engine on one synthetic 36-month ledger.

This module builds the ledger and returns the engine report. It does not
compute the expected exposure. The expected figures live in the test, which
uses separate Decimal arithmetic.
"""

from __future__ import annotations

from typing import Any

from aurex.dispater_intelligence import RevenueLeakageEngine, digest


def _day(index: int) -> str:
    year = 2024 + index // 12
    month = index % 12 + 1
    return f"{year}-{month:02d}-01"


def synthetic_ledger() -> dict[str, Any]:
    """Thirty-six monthly jobs plus the hour, reversal, and misapplied cases."""
    jobs: list[dict[str, str]] = []
    invoices: list[dict[str, str]] = []
    payments: list[dict[str, str]] = []
    equipment: list[dict[str, str]] = []
    labor: list[dict[str, str]] = []
    for index in range(36):
        job_id = f"J{index:02d}"
        if index == 21:
            service = "EQ"
        elif index == 22:
            service = "LAB"
        else:
            service = "S"
        jobs.append(
            {"job_id": job_id, "customer_id": "C1", "service_code": service, "date": _day(index)}
        )
        if index == 12:
            invoices.append({"invoice_id": "I12A", "job_id": job_id, "amount": "100.00", "status": "open"})
            invoices.append({"invoice_id": "I12B", "job_id": job_id, "amount": "100.00", "status": "open"})
            continue
        if index == 3:
            invoices.append({"invoice_id": "I03", "job_id": job_id, "amount": "150.00", "status": "open"})
            continue
        if index == 21:
            invoices.append({"invoice_id": "I21", "job_id": job_id, "amount": "150.00", "status": "open"})
            equipment.append(
                {
                    "ticket_id": "T21",
                    "job_id": job_id,
                    "equipment_id": "PUMP-1",
                    "service_date": _day(index),
                    "billable_hours": "4.00",
                    "standby_hours": "9.00",
                    "invoiced_hours": "4.00",
                }
            )
            continue
        if index == 22:
            invoices.append({"invoice_id": "I22", "job_id": job_id, "amount": "100.00", "status": "open"})
            labor.append(
                {
                    "record_id": "L22",
                    "job_id": job_id,
                    "role": "operator",
                    "service_date": _day(index),
                    "approved_hours": "4.00",
                    "billed_hours": "4.00",
                    "overtime_hours": "8.00",
                }
            )
            continue
        invoices.append({"invoice_id": f"I{index:02d}", "job_id": job_id, "amount": "100.00", "status": "paid"})
        if index == 20:
            invoices[-1]["status"] = "open"
            payments.append({"payment_id": "P20", "invoice_id": "I20", "amount": "40.00"})
        elif index == 23:
            payments.append({"payment_id": "P23", "invoice_id": "I23", "amount": "100.00"})
            payments.append({"payment_id": "P23R", "invoice_id": "I23", "amount": "40.00", "kind": "REVERSAL"})
        elif index == 24:
            payments.append(
                {"payment_id": "P24", "invoice_id": "I24", "amount": "100.00", "job_id": "OTHER"}
            )
        else:
            payments.append(
                {"payment_id": f"P{index:02d}", "invoice_id": f"I{index:02d}", "amount": "100.00"}
            )
    return {
        "tenant_id": "tenant-asc",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": jobs,
        "rates": [
            {
                "rate_id": "R-S",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2024-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            },
            {
                "rate_id": "R-EQ",
                "customer_id": "C1",
                "service_code": "EQ",
                "start": "2024-01-01",
                "end": "2026-12-31",
                "amount": "25.00",
                "unit": "HOUR",
            },
            {
                "rate_id": "R-LAB",
                "customer_id": "C1",
                "service_code": "LAB",
                "start": "2024-01-01",
                "end": "2026-12-31",
                "amount": "25.00",
                "unit": "HOUR",
            },
        ],
        "invoices": invoices,
        "payments": payments,
        "equipment": equipment,
        "labor": labor,
    }


def run_synthetic_audit() -> dict[str, Any]:
    """Reconcile the synthetic ledger with the canonical engine."""
    dataset = synthetic_ledger()
    report = RevenueLeakageEngine("tenant-asc").reconcile_records(dataset)
    return {
        "dataset_sha256": digest(dataset),
        "report": report,
        "financial_authority": "NONE",
        "production": "HOLD",
    }
