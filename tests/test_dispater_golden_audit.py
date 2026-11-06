"""36-month synthetic audit. Expected dollars are written independently of the engine."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from aurex.dispater_intelligence import RevenueLeakageEngine

# Seeded months are the only months allowed to produce a finding. Dollars below are
# calculated from those seeds, not copied from an engine run.
SEEDS = {
    2: "unbilled",
    5: "rate_over_paid",
    8: "duplicate_unresolved",
    11: "orphan_invoice",
    14: "partial",
    17: "overpayment",
    20: "settled_open",
    23: "orphan_payment",
    26: "split_exact",
    29: "rate_over_open",
}
EXPECTED = {
    "identified_exposure_usd": "385.00",
    "potential_underbilling_usd": "100.00",
    "potential_overbilling_usd": "130.00",
    "unverified_exposure_usd": "155.00",
    "withheld_unresolved_usd": "150.00",
    "confirmed_recovery_usd": "0.00",
    "human_confirmed_discrepancy_usd": "0.00",
}


def _month(index: int) -> str:
    year = 2024 + index // 12
    month = index % 12 + 1
    return date(year, month, 1).isoformat()


def build_dataset() -> dict:
    jobs = []
    invoices = []
    payments = []
    for index in range(36):
        kind = SEEDS.get(index)
        day = _month(index)
        job_id = f"J{index:02d}"
        if kind == "orphan_payment":
            payments.append({"payment_id": f"P{index:02d}", "invoice_id": "NONE", "amount": "25.00"})
            continue
        if kind != "orphan_invoice":
            jobs.append({"job_id": job_id, "customer_id": "C1", "service_code": "S", "date": day})
        if kind == "unbilled":
            continue
        if kind == "duplicate_unresolved":
            invoices.append({"invoice_id": f"I{index:02d}A", "job_id": job_id, "amount": "80.00", "status": "open"})
            invoices.append({"invoice_id": f"I{index:02d}B", "job_id": job_id, "amount": "70.00", "status": "open"})
            continue
        if kind == "orphan_invoice":
            invoices.append({"invoice_id": f"I{index:02d}", "job_id": "MISSING", "amount": "40.00", "status": "open"})
            continue
        amount = "150.00" if kind == "rate_over_paid" else "180.00" if kind == "rate_over_open" else "100.00"
        status = "paid" if kind in {"rate_over_paid", "split_exact"} or kind is None else "open"
        invoices.append({"invoice_id": f"I{index:02d}", "job_id": job_id, "amount": amount, "status": status})
        if kind == "partial":
            payments.append({"payment_id": f"P{index:02d}", "invoice_id": f"I{index:02d}", "amount": "40.00"})
        elif kind == "overpayment":
            payments.append({"payment_id": f"P{index:02d}", "invoice_id": f"I{index:02d}", "amount": "130.00"})
        elif kind == "settled_open":
            payments.append({"payment_id": f"P{index:02d}", "invoice_id": f"I{index:02d}", "amount": "100.00"})
        elif kind == "split_exact":
            payments.append({"payment_id": f"P{index:02d}A", "invoice_id": f"I{index:02d}", "amount": "60.00"})
            payments.append({"payment_id": f"P{index:02d}B", "invoice_id": f"I{index:02d}", "amount": "40.00"})
        elif kind == "rate_over_open":
            pass
        else:
            paid = "150.00" if kind == "rate_over_paid" else "100.00"
            payments.append({"payment_id": f"P{index:02d}", "invoice_id": f"I{index:02d}", "amount": paid})
    return {
        "tenant_id": "golden",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": jobs,
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2024-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": invoices,
        "payments": payments,
    }


def independent_totals() -> dict[str, str]:
    """Restate the seed arithmetic without calling the engine."""
    under = Decimal("100.00")  # one unbilled job at the contract rate
    over = Decimal("50.00") + Decimal("80.00")  # 150-100 and 180-100
    unverified = Decimal("40.00") + Decimal("60.00") + Decimal("30.00") + Decimal("25.00")
    withheld = Decimal("80.00") + Decimal("70.00")
    identified = under + over + unverified
    return {
        "identified_exposure_usd": f"{identified:.2f}",
        "potential_underbilling_usd": f"{under:.2f}",
        "potential_overbilling_usd": f"{over:.2f}",
        "unverified_exposure_usd": f"{unverified:.2f}",
        "withheld_unresolved_usd": f"{withheld:.2f}",
        "confirmed_recovery_usd": "0.00",
        "human_confirmed_discrepancy_usd": "0.00",
    }


def test_thirty_six_month_audit_matches_independent_totals() -> None:
    assert independent_totals() == EXPECTED
    report = RevenueLeakageEngine("golden").reconcile_records(build_dataset())
    summary = report["financial_summary"]
    for key, value in EXPECTED.items():
        assert summary[key] == value
    assert report["authority_state"] == "HOLD"
    assert all(item["qualification"] != "CONFIRMED_DISCREPANCY" for item in report["findings"])
    codes = {item["code"] for item in report["findings"]}
    assert {
        "UNBILLED_JOB",
        "RATE_MISMATCH",
        "DUPLICATE_INVOICE_UNRESOLVED",
        "ORPHAN_INVOICE",
        "PARTIAL_PAYMENT",
        "OVERPAYMENT",
        "STATUS_UNRECONCILED",
        "ORPHAN_PAYMENT",
        "SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED",
    } <= codes
    clean_subjects = {f"J{index:02d}" for index in range(36) if index not in SEEDS}
    assert not any(item["subject"] in clean_subjects for item in report["findings"])
    duplicate = next(item for item in report["findings"] if item["code"] == "DUPLICATE_INVOICE_UNRESOLVED")
    assert duplicate["exposure_usd"] == "0.00"
    assert duplicate["qualification"] == "INSUFFICIENT_EVIDENCE"
