"""Measurements for the synthetic kernel. Figures are observations, not a rating."""

from __future__ import annotations

import time
import tracemalloc
from datetime import UTC, datetime
from typing import Any

from aurex.ascendancy.dispater_adapter import run_synthetic_audit
from aurex.ascendancy.manuscript_adapter import HOLDOUT, TRAIN, kite_rule, rank_training
from aurex.governance_math.calibration import Prediction, temporal_holdout


def _class_probability(sequence: tuple[str, ...]) -> float:
    return 0.9 if kite_rule(sequence) else 0.1


def manuscript_holdout() -> dict[str, float | int]:
    """Score the selected rule against the training base rate on later rows."""
    cutoff = datetime(2026, 3, 1, tzinfo=UTC)
    rows: list[Prediction] = []
    for index, (sequence, label) in enumerate(TRAIN):
        rows.append(
            Prediction(
                f"train-{index}",
                "train-kite",
                datetime(2026, 1, 1, tzinfo=UTC),
                datetime(2026, 2, 1, tzinfo=UTC),
                _class_probability(sequence),
                int(label),
            )
        )
    for index, (sequence, label) in enumerate(HOLDOUT):
        rows.append(
            Prediction(
                f"holdout-{index}",
                "holdout-kite",
                datetime(2026, 4, 1, tzinfo=UTC),
                datetime(2026, 5, 1, tzinfo=UTC),
                _class_probability(sequence),
                int(label),
            )
        )
    report = temporal_holdout(rows, cutoff)
    return {
        "train_n": report.train_n,
        "holdout_n": report.holdout_n,
        "model_brier": report.model.brier,
        "prior_brier": report.prior_only.brier,
        "brier_improvement": report.brier_improvement,
    }


def run_benchmark() -> dict[str, Any]:
    """Time one synthetic audit and record the manuscript ablation winners."""
    penalized = rank_training(penalty=True)[0].hypothesis_id
    unpenalized = rank_training(penalty=False)[0].hypothesis_id
    tracemalloc.start()
    started = time.perf_counter()
    audit = run_synthetic_audit()
    elapsed = time.perf_counter() - started
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    summary = audit["report"]["financial_summary"]
    return {
        "financial_authority": "NONE",
        "production": "HOLD",
        "confirmed_recovery_usd": summary["confirmed_recovery_usd"],
        "identified_exposure_usd": summary["identified_exposure_usd"],
        "potential_overbilling_usd": summary["potential_overbilling_usd"],
        "potential_underbilling_usd": summary["potential_underbilling_usd"],
        "unverified_exposure_usd": summary["unverified_exposure_usd"],
        "withheld_unresolved_usd": summary["withheld_unresolved_usd"],
        "audit_seconds": elapsed,
        "audit_peak_bytes": peak,
        "penalized_hypothesis": penalized,
        "unpenalized_hypothesis": unpenalized,
        "manuscript_holdout": manuscript_holdout(),
        "rating_claimed": None,
    }
