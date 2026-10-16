"""HELM-inspired transparent multi-axis evaluation inventory for AUREX.

The *idea* of measuring more than accuracy is drawn from Stanford CRFM's
holistic evaluation. This is original code, not an implementation of HELM,
and the numeric observations are explicitly source-reported, not admitted.
No aggregated "AI safety score": units and tasks are not interchangeable.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

_SHA = re.compile(r"^[0-9a-f]{64}$")
# The metrics use explicit units, avoiding misleading averaging of values.
AXES: dict[str, str] = {
    "accuracy": "fraction",
    "calibration_brier": "fraction",
    "robustness_pass_rate": "fraction",
    "fairness_gap": "fraction",
    "bias_rate": "fraction",
    "toxicity_rate": "fraction",
    "median_latency_seconds": "seconds",
    "false_pass_rate": "fraction",
    "privacy_incident_rate": "fraction",
    "mean_cost_usd": "usd",
}


@dataclass(frozen=True, slots=True)
class AxisObservation:
    metric: str
    value: float
    unit: str
    evaluated_count: int
    evidence_sha256: str


@dataclass(frozen=True, slots=True)
class HolisticReport:
    model_sha256: str
    run_sha256: str
    dataset_sha256: str
    evaluated: tuple[AxisObservation, ...]
    missing: tuple[str, ...]
    coverage: float
    gate: str
    independent_verification: str = "NOT VERIFIED"
    authority: str = "METRICS_ONLY"


def summarize_axes(
    model_sha256: str,
    run_sha256: str,
    dataset_sha256: str,
    observations: Sequence[AxisObservation],
) -> HolisticReport:
    """Show which dimensions are present, never award PASS for completeness.

    Observations must already be scoped to one frozen model/run/dataset by the
    caller. Valid SHA strings do not constitute independently verified data.
    """
    for value in (model_sha256, run_sha256, dataset_sha256):
        if not isinstance(value, str) or not _SHA.fullmatch(value):
            raise ValueError("frozen SHA-256 model, run, dataset identities required")
    if len(observations) > len(AXES):
        raise ValueError("too many metric rows")
    by_name: dict[str, AxisObservation] = {}
    for row in observations:
        if not isinstance(row, AxisObservation):
            raise ValueError("metric observations must be typed")
        expected = AXES.get(row.metric)
        if (
            expected is None or row.metric in by_name
            or row.unit != expected
            or not isinstance(row.value, (int, float))
            or isinstance(row.value, bool) or not math.isfinite(row.value)
            or row.value < 0
            or (row.unit == "fraction" and row.value > 1)
            or isinstance(row.evaluated_count, bool)
            or not isinstance(row.evaluated_count, int)
            or not 1 <= row.evaluated_count <= 1_000_000
            or not isinstance(row.evidence_sha256, str)
            or not _SHA.fullmatch(row.evidence_sha256)
        ):
            raise ValueError("unrecognized, duplicate, wrong-unit or invalid metric")
        by_name[row.metric] = row
    missing = tuple(axis for axis in AXES if axis not in by_name)
    return HolisticReport(
        model_sha256, run_sha256, dataset_sha256,
        tuple(by_name[name] for name in AXES if name in by_name),
        missing, len(by_name) / len(AXES),
        "INCOMPLETE_METRIC_COVERAGE" if missing else "REVIEW_UNVERIFIED_METRICS",
    )
