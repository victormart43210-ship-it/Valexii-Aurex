"""Calibration diagnostics and leakage-resistant temporal evaluation.

Independent outcome labels and train/test provenance must be checked *before*
calling these pure functions. These scores never confer security authority.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

MAX_ROWS = 10_000
EPSILON = 1e-12


@dataclass(frozen=True, slots=True)
class Prediction:
    case_id: str
    lineage_group: str
    predicted_at: datetime
    probability: float
    actual: int


@dataclass(frozen=True, slots=True)
class ReliabilityBin:
    count: int
    mean_probability: float | None
    observed_frequency: float | None


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    n: int
    brier: float
    log_loss: float
    expected_calibration_error: float
    reliability: tuple[ReliabilityBin, ...]
    authority: str = "ANALYSIS_ONLY_NOT_VERIFIED"


@dataclass(frozen=True, slots=True)
class HoldoutReport:
    train_n: int
    holdout_n: int
    model: CalibrationReport
    prior_only: CalibrationReport
    brier_improvement: float
    authority: str = "ANALYSIS_ONLY_NOT_VERIFIED"


def _validate(rows: Sequence[Prediction]) -> None:
    if not 0 < len(rows) <= MAX_ROWS:
        raise ValueError("1..10000 predictions required")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Prediction):
            raise ValueError("expected Prediction records")
        if (
            not row.case_id or row.case_id in seen or not row.lineage_group
            or not isinstance(row.predicted_at, datetime)
            or row.predicted_at.tzinfo is None
            or row.predicted_at.utcoffset() is None
            or not isinstance(row.probability, (int, float))
            or isinstance(row.probability, bool)
            or not math.isfinite(row.probability)
            or not 0 <= row.probability <= 1
            or isinstance(row.actual, bool)
            or row.actual not in (0, 1)
            or not isinstance(row.actual, int)
        ):
            raise ValueError("duplicate/invalid sample, timestamp, probability or label")
        seen.add(row.case_id)


def calibration_report(rows: Sequence[Prediction], *, bins: int = 10) -> CalibrationReport:
    """Brier, proper log loss, and equally spaced-bin expected calibration error."""
    if not isinstance(bins, int) or isinstance(bins, bool) or not 2 <= bins <= 20:
        raise ValueError("bins must be an integer from 2 to 20")
    _validate(rows)
    n = len(rows)
    brier = math.fsum((r.probability - r.actual) ** 2 for r in rows) / n
    log_loss = -math.fsum(
        r.actual * math.log(max(EPSILON, min(1 - EPSILON, r.probability)))
        + (1 - r.actual) * math.log(max(EPSILON, min(1 - EPSILON, 1 - r.probability)))
        for r in rows
    ) / n
    groups: list[list[Prediction]] = [[] for _ in range(bins)]
    for row in rows:
        groups[min(bins - 1, int(row.probability * bins))].append(row)
    reliability: list[ReliabilityBin] = []
    error = 0.0
    for group in groups:
        if not group:
            reliability.append(ReliabilityBin(0, None, None))
            continue
        mean_p = math.fsum(x.probability for x in group) / len(group)
        observed = math.fsum(x.actual for x in group) / len(group)
        error += len(group) / n * abs(mean_p - observed)
        reliability.append(ReliabilityBin(len(group), mean_p, observed))
    return CalibrationReport(n, brier, log_loss, error, tuple(reliability))


def temporal_holdout(
    rows: Sequence[Prediction], cutoff: datetime, *, bins: int = 10
) -> HoldoutReport:
    """Holdout strictly after cutoff, with no lineage group appearing in both sets.

    Compare to a prior-only predictor fit ONLY on pre-cutoff labels. This is a
    diagnostic, not model fitting and not proof that labels are independent.
    """
    _validate(rows)
    if not isinstance(cutoff, datetime) or cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise ValueError("cutoff requires a timezone")
    train = [x for x in rows if x.predicted_at < cutoff]
    test = [x for x in rows if x.predicted_at >= cutoff]
    if not train or not test:
        raise ValueError("both historical training and later holdout required")
    if {x.lineage_group for x in train} & {x.lineage_group for x in test}:
        raise ValueError("lineage leakage across temporal holdout")
    prior = math.fsum(x.actual for x in train) / len(train)
    baseline = [
        Prediction(x.case_id, x.lineage_group, x.predicted_at, prior, x.actual)
        for x in test
    ]
    model_report = calibration_report(test, bins=bins)
    prior_report = calibration_report(baseline, bins=bins)
    return HoldoutReport(
        len(train), len(test), model_report, prior_report,
        prior_report.brier - model_report.brier,
    )
