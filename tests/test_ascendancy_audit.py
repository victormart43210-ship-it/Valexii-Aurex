"""Synthetic 36-month audit. Expected money is computed in this file."""

from __future__ import annotations

from decimal import Decimal

from aurex.ascendancy.benchmark import run_benchmark
from aurex.ascendancy.dispater_adapter import run_synthetic_audit


def _oracle() -> dict[str, Decimal]:
    """Hand arithmetic for the synthetic ledger. This does not call the engine."""
    flat_over = Decimal("150.00") - Decimal("100.00")
    hour_amount = Decimal("4.00") * Decimal("25.00")
    hour_over = Decimal("150.00") - hour_amount
    partial_gap = Decimal("100.00") - Decimal("40.00")
    net_after_reversal = Decimal("100.00") - Decimal("40.00")
    reversal_gap = Decimal("100.00") - net_after_reversal
    misapplied = Decimal("100.00")
    withheld = Decimal("100.00") + Decimal("100.00")
    over = flat_over + hour_over
    unverified = partial_gap + reversal_gap + misapplied
    return {
        "potential_overbilling_usd": over,
        "potential_underbilling_usd": Decimal("0.00"),
        "unverified_exposure_usd": unverified,
        "withheld_unresolved_usd": withheld,
        "identified_exposure_usd": over + unverified,
        "confirmed_recovery_usd": Decimal("0.00"),
    }


def test_synthetic_audit_matches_the_independent_oracle() -> None:
    expected = _oracle()
    # 150-100 = 50 flat over. 4*25 = 100, so 150-100 = 50 hour over. Standby 9 is excluded.
    # Partial 100-40 = 60. Reversal leaves 60 against a paid 100, gap 40.
    # Misapplied cash is 100 and is not also a paid-status gap. Duplicate bills withhold 200.
    assert expected["potential_overbilling_usd"] == Decimal("100.00")
    assert expected["unverified_exposure_usd"] == Decimal("200.00")
    assert expected["identified_exposure_usd"] == Decimal("300.00")
    assert expected["withheld_unresolved_usd"] == Decimal("200.00")
    summary = run_synthetic_audit()["report"]["financial_summary"]
    for key, amount in expected.items():
        assert summary[key] == f"{amount:.2f}"
    assert summary["human_confirmed_discrepancy_usd"] == "0.00"
    codes = {item["code"] for item in run_synthetic_audit()["report"]["findings"]}
    assert codes == {
        "RATE_MISMATCH",
        "DUPLICATE_INVOICE_UNRESOLVED",
        "PARTIAL_PAYMENT",
        "EQUIPMENT_HOURS_MISMATCH",
        "OVERTIME_UNPRICED",
        "PAID_STATUS_UNRECONCILED",
        "MISAPPLIED_PAYMENT",
    }


def test_benchmark_records_the_ablation_without_claiming_a_rating() -> None:
    report = run_benchmark()
    assert report["rating_claimed"] is None
    assert report["financial_authority"] == "NONE"
    assert report["confirmed_recovery_usd"] == "0.00"
    assert report["identified_exposure_usd"] == "300.00"
    assert report["penalized_hypothesis"] == "kite-rule"
    assert report["unpenalized_hypothesis"] == "memorize-train"
    holdout = report["manuscript_holdout"]
    assert holdout["model_brier"] < holdout["prior_brier"]
    assert holdout["brier_improvement"] > 0
    assert 0 <= report["audit_seconds"] < 5
    assert 0 < report["audit_peak_bytes"] < 50_000_000
