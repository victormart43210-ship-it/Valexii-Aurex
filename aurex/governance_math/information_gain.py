"""Bounded expected-information-gain test prioritization (analysis only).

Likelihoods must be calibrated *externally*. A caller-provided flag is not
cryptographic evidence and NEVER grants permission for a test or a paid call.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Probe:
    probe_id: str
    sensitivity: float  # P(test positive | hypothesis true)
    specificity: float  # P(test negative | hypothesis false)
    duration_seconds: int
    risk: int
    cost_usd: Decimal
    calibration_reviewed: bool = False


@dataclass(frozen=True, slots=True)
class TestChoice:
    probe_id: str
    information_gain_bits: float
    positive_probability: float
    score: float
    status: str = "ADVISORY_NOT_AUTHORIZED"


def _p(value: float, label: str) -> float:
    if (
        not isinstance(value, (int, float)) or isinstance(value, bool)
        or not math.isfinite(value) or not 0 <= value <= 1
    ):
        raise ValueError(f"{label} must be finite in [0, 1]")
    return float(value)


def entropy(probability: float) -> float:
    p = _p(probability, "probability")
    if p in (0.0, 1.0):
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def information_gain(prior: float, sensitivity: float, specificity: float) -> tuple[float, float]:
    """Expected entropy reduction in bits for a binary observation.

    Assumes *calibrated* sensitivity and specificity, never estimates either.
    """
    p = _p(prior, "prior")
    tpr = _p(sensitivity, "sensitivity")
    tnr = _p(specificity, "specificity")
    positive = p * tpr + (1 - p) * (1 - tnr)
    negative = 1 - positive
    after_pos = (p * tpr / positive) if positive > 0 else 0.0
    after_neg = (p * (1 - tpr) / negative) if negative > 0 else 0.0
    gain = entropy(p) - positive * entropy(after_pos) - negative * entropy(after_neg)
    return max(0.0, min(entropy(p), gain)), positive


def rank_next_tests(
    prior: float,
    probes: Sequence[Probe],
    *,
    max_risk: int = 2,
    max_cost_usd: Decimal = Decimal("0"),
) -> tuple[TestChoice, ...]:
    """Choose most informative admissible $0 probe, never execute it.

    The heuristic score subtracts execution risk and time; it is not calibrated
    expected business utility. Rejected / uncalibrated probes are not suggested.
    """
    _p(prior, "prior")
    if len(probes) > 128:
        raise ValueError("too many probes")
    if isinstance(max_risk, bool) or not isinstance(max_risk, int) or not 0 <= max_risk <= 5:
        raise ValueError("max_risk must be 0..5")
    if (
        not isinstance(max_cost_usd, Decimal) or not max_cost_usd.is_finite()
        or max_cost_usd < 0
    ):
        raise ValueError("max_cost_usd must be nonnegative finite Decimal")
    seen: set[str] = set()
    choices: list[TestChoice] = []
    for probe in probes:
        if not isinstance(probe, Probe) or not probe.probe_id or probe.probe_id in seen:
            raise ValueError("invalid or duplicate probe")
        seen.add(probe.probe_id)
        _p(probe.sensitivity, "sensitivity")
        _p(probe.specificity, "specificity")
        if (
            isinstance(probe.duration_seconds, bool)
            or not isinstance(probe.duration_seconds, int)
            or not 0 <= probe.duration_seconds <= 86_400
            or isinstance(probe.risk, bool)
            or not isinstance(probe.risk, int)
            or not 0 <= probe.risk <= 5
            or not isinstance(probe.cost_usd, Decimal)
            or not probe.cost_usd.is_finite()
            or probe.cost_usd < 0
            or not isinstance(probe.calibration_reviewed, bool)
        ):
            raise ValueError("invalid probe resource bounds")
        if (
            not probe.calibration_reviewed
            or probe.risk > max_risk
            or probe.cost_usd > max_cost_usd
        ):
            continue
        bits, positive = information_gain(prior, probe.sensitivity, probe.specificity)
        # Transparent heuristic; no empirical performance claim.
        score = bits - 0.03 * probe.risk - 0.0001 * probe.duration_seconds
        choices.append(TestChoice(probe.probe_id, bits, positive, score))
    choices.sort(key=lambda x: (-x.score, x.probe_id))
    return tuple(choices)
