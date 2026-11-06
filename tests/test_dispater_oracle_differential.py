"""CCXXI differential check: engine vs an independent integer-cent oracle on randomised single-job data."""

import random
from decimal import Decimal
from typing import Any

import pytest

from aurex.dispater_intelligence import RevenueLeakageEngine


def _dataset(rate_cents: int, invoice_cents: int) -> dict[str, Any]:
    return {
        "tenant_id": "t",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [
            {"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01",
             "end": "2026-12-31", "amount": f"{rate_cents // 100}.{rate_cents % 100:02d}"}
        ],
        "invoices": [
            {"invoice_id": "I1", "job_id": "J1", "status": "open",
             "amount": f"{invoice_cents // 100}.{invoice_cents % 100:02d}"}
        ],
        "payments": [],
    }


@pytest.mark.parametrize("seed", range(25))
def test_engine_matches_integer_cent_oracle(seed: int) -> None:
    rng = random.Random(seed)
    rate = rng.randint(1, 5_000_000)
    invoice = rate + rng.choice([0, 1, -1, rng.randint(-rate, 100_000)])
    invoice = max(invoice, 0)
    summary = RevenueLeakageEngine("t").reconcile_records(_dataset(rate, invoice))["financial_summary"]
    assert Decimal(summary["potential_overbilling_usd"]) == Decimal(max(invoice - rate, 0)) / 100
    assert Decimal(summary["potential_underbilling_usd"]) == Decimal(max(rate - invoice, 0)) / 100
    # Potential exposure must never become confirmed money without documented settlement.
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert summary["human_confirmed_discrepancy_usd"] == "0.00"


def test_report_never_grants_authority() -> None:
    report = RevenueLeakageEngine("t").reconcile_records(_dataset(10000, 15000))
    assert report["authority_state"] == "HOLD"
    assert report["human_review_required"] is True
    assert all(f["authority"] == "HUMAN_REVIEW_REQUIRED" for f in report["findings"])
