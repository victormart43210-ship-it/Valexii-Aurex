"""Split conformal *prediction sets* for advisory binary decisions.

Inspired by research and teaching from UC Berkeley (Angelopoulos/Bates and
Ryan Tibshirani). This independently written implementation relies on the
assumption that calibration and future evaluation scores are exchangeable.
It does NOT certify that assumption, a model, or any AUREX security claim.
No gradients, neural models, inference calls, data retrieval, or side effects.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

_MAX = 10_000
_SHA = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class CalibrationCase:
    case_id: str
    source_group: str
    run_sha256: str
    model_sha256: str
    predicted_at: datetime
    outcome_observed_at: datetime
    probability_positive: float
    actual_label: Literal[0, 1]


@dataclass(frozen=True, slots=True)
class BinaryConformal:
    model_sha256: str
    calibration_run_sha256: str
    cutoff: datetime
    alpha: float
    calibration_n: int
    nonconformity_threshold: float
    assumption: str = "EXCHANGEABILITY_NOT_INDEPENDENTLY_ESTABLISHED"
    authority: str = "ADVISORY_ONLY"


@dataclass(frozen=True, slots=True)
class BinarySet:
    labels: tuple[int, ...]
    decision: str
    authority: str = "NOT_A_SECURITY_VERDICT"


def _prob(p: float) -> float:
    if (
        not isinstance(p, (float, int)) or isinstance(p, bool)
        or not math.isfinite(p) or not 0 <= p <= 1
    ):
        raise ValueError("probability must be finite between 0 and 1")
    return float(p)


def _clock(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")


def fit_binary_conformal(
    rows: Sequence[CalibrationCase], *, alpha: float, cutoff: datetime
) -> BinaryConformal:
    """Finite-sample split conformal threshold using ceil((n+1)*(1-alpha)).

    A rank above n returns threshold 1, allowing both labels, rather than
    claiming precision without enough calibration samples.
    """
    _clock(cutoff)
    a = _prob(alpha)
    if not 0 < a < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    if not 10 <= len(rows) <= _MAX:
        raise ValueError("at least 10 and at most 10000 calibration rows required")
    ids: set[str] = set()
    source_groups: set[str] = set()
    scores: list[float] = []
    model: str | None = None
    run: str | None = None
    for item in rows:
        if not isinstance(item, CalibrationCase):
            raise ValueError("invalid calibration row")
        _clock(item.predicted_at)
        _clock(item.outcome_observed_at)
        if (
            not item.case_id or item.case_id in ids
            or not item.source_group or item.source_group in source_groups
            or not _SHA.fullmatch(item.run_sha256)
            or not _SHA.fullmatch(item.model_sha256)
            or item.predicted_at > item.outcome_observed_at
            or item.outcome_observed_at > cutoff
            or item.actual_label not in (0, 1)
            or isinstance(item.actual_label, bool)
            or (model is not None and item.model_sha256 != model)
            or (run is not None and item.run_sha256 != run)
        ):
            raise ValueError("unqualified, duplicate, future or mismatched calibration cases")
        p = _prob(item.probability_positive)
        model = item.model_sha256
        run = item.run_sha256
        ids.add(item.case_id)
        source_groups.add(item.source_group)
        scores.append((1 - p) if item.actual_label == 1 else p)
    scores.sort()
    index = math.ceil((len(scores) + 1) * (1 - a))
    q = 1.0 if index > len(scores) else scores[index - 1]
    assert model is not None and run is not None
    return BinaryConformal(model, run, cutoff, a, len(scores), q)


def predict_binary_set(
    fitted: BinaryConformal, probability_positive: float, model_sha256: str
) -> BinarySet:
    """Never reinterpret a singleton as PASS. Two/zero labels means abstain."""
    p = _prob(probability_positive)
    if not isinstance(fitted, BinaryConformal) or model_sha256 != fitted.model_sha256:
        raise ValueError("model identity mismatch or calibration unavailable")
    labels = tuple(
        y for y, nonconformity in ((0, p), (1, 1 - p))
        if nonconformity <= fitted.nonconformity_threshold
    )
    decision = "CANDIDATE_ONLY" if len(labels) == 1 else "ABSTAIN_HOLD"
    return BinarySet(labels, decision)
