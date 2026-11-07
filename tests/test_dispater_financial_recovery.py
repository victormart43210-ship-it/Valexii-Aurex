"""Towing revenue recovery scenarios recovered from PR #197, reconciled to main's stricter engine.

Validates all 10 required towing revenue recovery scenarios:
1. Unbilled completed tow
2. Incorrect contracted rate
3. Unbilled storage days
4. Incorrect after-hours surcharge
5. Partial motor-club payment (short pay)
6. Duplicate invoice
7. Missing deposit reconciliation
8. Contract amendment and effective-date changes
9. Disputed charges
10. Confirmed payment recovery separation (guaranteeing 0.00 until human validation)
"""

from decimal import Decimal

import pytest

from aurex.dispater_intelligence import (
    UNDERBILLING,
    UNVERIFIED,
    InvalidSnapshot,
    RevenueLeakageEngine,
    verify_receipt,
)


def make_base_dataset():
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": "towing-co",
        "jobs": [],
        "invoices": [],
        "rates": [
            {
                "rate_id": "RATE-TOW-STD",
                "customer_id": "CUST-PD",
                "service_code": "TOW_STANDARD",
                "amount": "125.00",
                "start": "2026-01-01",
                "end": "2026-12-31",
            },
            {
                "rate_id": "RATE-STORAGE",
                "customer_id": "CUST-PD",
                "service_code": "STORAGE_DAILY",
                "amount": "45.00",
                "start": "2026-01-01",
                "end": "2026-12-31",
            },
            {
                "rate_id": "RATE-AH",
                "customer_id": "CUST-PD",
                "service_code": "AFTER_HOURS_SURCHARGE",
                "amount": "75.00",
                "start": "2026-01-01",
                "end": "2026-12-31",
            },
        ],
        "payments": [],
        "deposits": [],
        "disputes": [],
    }


def test_scenario_1_unbilled_completed_tow():
    """Scenario 1: Completed tow dispatch with no invoice generated."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-101",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-10",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    assert report["financial_summary"]["potential_underbilling_usd"] == "125.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    codes = [f["code"] for f in report["findings"]]
    assert "UNBILLED_JOB" in codes
    assert verify_receipt(report)


def test_scenario_2_incorrect_contracted_rate():
    """Scenario 2: Tow billed at incorrect rate below or above contracted schedule."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-102",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-11",
    })
    # Billed 100.00 instead of 125.00 contracted
    ds["invoices"].append({
        "invoice_id": "INV-102",
        "job_id": "JOB-102",
        "customer_id": "CUST-PD",
        "amount": "100.00",
        "status": "open",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    assert report["financial_summary"]["potential_underbilling_usd"] == "25.00"
    fnd = next(f for f in report["findings"] if f["code"] == "RATE_MISMATCH")
    assert fnd["exposure_usd"] == "25.00"
    assert fnd["exposure_class"] == UNDERBILLING


def test_scenario_3_unbilled_storage_days():
    """Scenario 3: Tow job has 3 days storage logged, but invoice storage_amount is 0.00."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-103",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-12",
        "storage_days": "3",
    })
    ds["invoices"].append({
        "invoice_id": "INV-103",
        "job_id": "JOB-103",
        "customer_id": "CUST-PD",
        "amount": "125.00",
        "storage_amount": "0.00",
        "status": "open",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    # 3 days * $45.00 = $135.00 underbilling
    assert Decimal(report["financial_summary"]["potential_underbilling_usd"]) == Decimal("135.00")
    fnd = next(f for f in report["findings"] if f["code"] == "UNBILLED_STORAGE_DAYS")
    assert fnd["exposure_usd"] == "135.00"


def test_scenario_4_incorrect_after_hours_surcharge():
    """Scenario 4: After-hours tow with $50 billed instead of $75 contracted."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-104",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-12",
        "after_hours": "true",
    })
    ds["invoices"].append({
        "invoice_id": "INV-104",
        "job_id": "JOB-104",
        "customer_id": "CUST-PD",
        "amount": "125.00",
        "after_hours_amount": "50.00",
        "status": "open",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    assert Decimal(report["financial_summary"]["potential_underbilling_usd"]) == Decimal("25.00")
    fnd = next(f for f in report["findings"] if f["code"] == "INCORRECT_AFTER_HOURS_SURCHARGE")
    assert fnd["exposure_usd"] == "25.00"


def test_scenario_5_partial_motor_club_payment():
    """Scenario 5: Motor club remits partial payment ($80 on a $125 invoice)."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-105",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-13",
    })
    ds["invoices"].append({
        "invoice_id": "INV-105",
        "job_id": "JOB-105",
        "customer_id": "CLUB-AAA",
        "customer_type": "MOTOR_CLUB",
        "amount": "125.00",
        "status": "open",
    })
    ds["payments"].append({
        "payment_id": "PAY-105",
        "invoice_id": "INV-105",
        "amount": "80.00",
        "date": "2026-05-15",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    fnd = next(f for f in report["findings"] if f["code"] == "PARTIAL_PAYMENT")
    assert fnd["exposure_usd"] == "45.00"
    assert fnd["exposure_class"] == UNVERIFIED


def test_scenario_6_duplicate_invoice():
    """Scenario 6: Same job billed twice on two distinct invoices."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-106",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-14",
    })
    ds["invoices"].append({
        "invoice_id": "INV-106A",
        "job_id": "JOB-106",
        "customer_id": "CUST-PD",
        "amount": "125.00",
        "status": "paid",
    })
    ds["invoices"].append({
        "invoice_id": "INV-106B",
        "job_id": "JOB-106",
        "customer_id": "CUST-PD",
        "amount": "125.00",
        "status": "open",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    # Main refuses to guess which duplicate is legitimate, so nothing is booked as overbilling.
    assert report["financial_summary"]["potential_overbilling_usd"] == "0.00"
    assert report["financial_summary"]["withheld_unresolved_usd"] == "250.00"
    fnd = next(f for f in report["findings"] if f["code"] == "DUPLICATE_INVOICE_UNRESOLVED")
    assert fnd["severity"] == "CRITICAL"
    assert fnd["exposure_usd"] == "0.00"


def test_scenario_7_missing_deposit_reconciliation():
    """Scenario 7: Received payments total $500, but bank deposit batch is only $400."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-107",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-15",
    })
    ds["invoices"].append({
        "invoice_id": "INV-107",
        "job_id": "JOB-107",
        "customer_id": "CUST-PD",
        "amount": "500.00",
        "status": "paid",
    })
    ds["payments"].append({
        "payment_id": "PAY-107",
        "invoice_id": "INV-107",
        "amount": "500.00",
        "date": "2026-05-16",
    })
    ds["deposits"].append({
        "deposit_id": "DEP-107",
        "amount": "400.00",
        "date": "2026-05-17",
        "reference": "BATCH-001",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    fnd = next(f for f in report["findings"] if f["code"] == "DEPOSIT_RECONCILIATION_GAP")
    # The bank variance is disclosed, not added on top of invoice/payment dollars.
    assert fnd["exposure_usd"] == "0.00"
    assert "variance $100.00" in fnd["xaeli_explanation"]["now"]
    assert fnd["exposure_class"] == UNVERIFIED


def test_scenario_8_contract_amendment_effective_date():
    """Scenario 8: Rate amended mid-year; job executed during amendment window."""
    ds = make_base_dataset()
    ds["rates"] = [
        {
            "rate_id": "RATE-V1",
            "customer_id": "CUST-FLEET",
            "service_code": "TOW_STANDARD",
            "amount": "100.00",
            "start": "2026-01-01",
            "end": "2026-05-31",
        },
        {
            "rate_id": "RATE-V2-AMENDMENT",
            "customer_id": "CUST-FLEET",
            "service_code": "TOW_STANDARD",
            "amount": "130.00",
            "start": "2026-06-01",
            "end": "2026-12-31",
        },
    ]
    ds["jobs"].append({
        "job_id": "JOB-108",
        "customer_id": "CUST-FLEET",
        "service_code": "TOW_STANDARD",
        "date": "2026-06-15",
    })
    # Billed at old rate 100.00 instead of amended 130.00
    ds["invoices"].append({
        "invoice_id": "INV-108",
        "job_id": "JOB-108",
        "customer_id": "CUST-FLEET",
        "amount": "100.00",
        "status": "open",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    assert report["financial_summary"]["potential_underbilling_usd"] == "30.00"
    fnd = next(f for f in report["findings"] if f["code"] == "RATE_MISMATCH")
    assert fnd["exposure_usd"] == "30.00"


def test_scenario_9_disputed_charges():
    """Scenario 9: Customer disputes invoice charge."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-109",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-18",
    })
    ds["invoices"].append({
        "invoice_id": "INV-109",
        "job_id": "JOB-109",
        "customer_id": "CUST-PD",
        "amount": "125.00",
        "status": "disputed",
    })
    ds["disputes"].append({
        "dispute_id": "DISP-109",
        "invoice_id": "INV-109",
        "disputed_amount": "125.00",
        "reason": "Vehicle damage claim pending inspection",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    fnd = next(f for f in report["findings"] if f["code"] == "DISPUTED_CHARGE")
    assert fnd["exposure_usd"] == "125.00"
    assert fnd["exposure_class"] == UNVERIFIED


def test_scenario_10_confirmed_payment_recovery_separation():
    """Scenario 10: Invariant enforcement that AI never books confirmed recovery autonomously."""
    ds = make_base_dataset()
    ds["jobs"].append({
        "job_id": "JOB-110",
        "customer_id": "CUST-PD",
        "service_code": "TOW_STANDARD",
        "date": "2026-05-19",
    })

    engine = RevenueLeakageEngine("towing-co")
    report = engine.reconcile_records(ds)

    assert report["financial_summary"]["potential_underbilling_usd"] == "125.00"
    # Even though potential underbilling is found, confirmed recovery MUST remain 0.00
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert report["financial_summary"]["human_confirmed_discrepancy_usd"] == "0.00"
    assert report["authority_state"] == "HOLD"
    assert report["human_review_required"] is True


def _single_job_dataset(job_extra=None, invoice_extra=None):
    ds = make_base_dataset()
    ds["jobs"].append(
        {
            "job_id": "JOB-200",
            "customer_id": "CUST-PD",
            "service_code": "TOW_STANDARD",
            "date": "2026-05-12",
            **(job_extra or {}),
        }
    )
    ds["invoices"].append(
        {
            "invoice_id": "INV-200",
            "job_id": "JOB-200",
            "amount": "125.00",
            "status": "open",
            **(invoice_extra or {}),
        }
    )
    return ds


def test_addon_without_stated_invoice_amount_is_not_assumed_zero():
    ds = _single_job_dataset({"storage_days": "3"})
    report = RevenueLeakageEngine("towing-co").reconcile_records(ds)
    codes = [f["code"] for f in report["findings"]]
    assert "ADDON_UNVERIFIED" in codes
    assert "UNBILLED_STORAGE_DAYS" not in codes
    assert report["financial_summary"]["potential_underbilling_usd"] == "0.00"


def test_storage_overbilling_is_not_booked_as_underbilling():
    ds = _single_job_dataset({"storage_days": "2"}, {"storage_amount": "100.00"})
    report = RevenueLeakageEngine("towing-co").reconcile_records(ds)
    assert report["financial_summary"]["potential_overbilling_usd"] == "10.00"
    assert report["financial_summary"]["potential_underbilling_usd"] == "0.00"


def test_correct_addons_produce_no_findings():
    ds = _single_job_dataset(
        {"storage_days": "2", "after_hours": "true"},
        {"storage_amount": "90.00", "after_hours_amount": "75.00"},
    )
    report = RevenueLeakageEngine("towing-co").reconcile_records(ds)
    assert report["findings"] == []


@pytest.mark.parametrize(
    "job_extra",
    [
        {"after_hours": "yes"},
        {"storage_days": "-1"},
        {"storage_days": "3.5"},
        {"storage_days": "99999"},
    ],
)
def test_malformed_addon_fields_fail_closed(job_extra):
    with pytest.raises(InvalidSnapshot):
        RevenueLeakageEngine("towing-co").reconcile_records(_single_job_dataset(job_extra))


def test_dispute_against_unknown_invoice_fails_closed():
    ds = _single_job_dataset()
    ds["disputes"].append(
        {"dispute_id": "D-1", "invoice_id": "INV-NOPE", "disputed_amount": "10.00", "reason": "x"}
    )
    with pytest.raises(InvalidSnapshot):
        RevenueLeakageEngine("towing-co").reconcile_records(ds)


def test_disputes_never_exceed_invoice_amount():
    ds = _single_job_dataset()
    for ident in ("D-1", "D-2"):
        ds["disputes"].append(
            {"dispute_id": ident, "invoice_id": "INV-200", "disputed_amount": "100.00", "reason": "x"}
        )
    report = RevenueLeakageEngine("towing-co").reconcile_records(ds)
    assert report["financial_summary"]["unverified_exposure_usd"] == "125.00"
    assert verify_receipt(report)
