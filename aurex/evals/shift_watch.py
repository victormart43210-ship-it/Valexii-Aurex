"""Data-shift warning for reliability checks, not a statistical certificate.

Motivated by worldwide research into deployment distribution shift including
Masashi Sugiyama's group at the University of Tokyo. This is original
categorical total-variation arithmetic: no learned density ratio, no tests of
significance, and no assertion that a model is safe when the warning is quiet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ShiftReport:
    baseline_n: int
    current_n: int
    total_variation: float
    threshold: float
    gate: str
    authority: str = "DIAGNOSTIC_ONLY"


def _validate_counts(counts: Mapping[str, int]) -> int:
    if not isinstance(counts, dict) or not 1 <= len(counts) <= 128:
        raise ValueError("bounded categorical histogram expected")
    if any(
        not isinstance(k, str) or not k or len(k) > 128
        or type(v) is not int or v < 0 or v > 1_000_000
        for k, v in counts.items()
    ):
        raise ValueError("invalid categories or frequencies")
    total = sum(counts.values())
    if not 20 <= total <= 1_000_000:
        raise ValueError("insufficient or oversized observations")
    return total


def compare_categorical_shift(
    baseline: Mapping[str, int],
    current: Mapping[str, int],
    *,
    review_threshold: float = 0.20,
) -> ShiftReport:
    """1/2 sum |frequency_baseline - frequency_current|, all categories.

    An alert threshold is an operator policy choice, not a statistical
    significance level. Window sampling/independence is not authenticated here.
    """
    if (
        not isinstance(review_threshold, (float, int))
        or isinstance(review_threshold, bool)
        or not math.isfinite(review_threshold)
        or not 0 < review_threshold < 1
    ):
        raise ValueError("threshold must be finite in (0,1)")
    bn = _validate_counts(baseline)
    cn = _validate_counts(current)
    keys = set(baseline) | set(current)
    distance = 0.5 * math.fsum(
        abs(baseline.get(k, 0) / bn - current.get(k, 0) / cn)
        for k in sorted(keys)
    )
    return ShiftReport(
        bn, cn, distance, float(review_threshold),
        "DRIFT_REVIEW_HOLD" if distance > review_threshold else "NO_DRIFT_SIGNAL_NOT_PROOF",
    )
