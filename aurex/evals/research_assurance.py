"""Demote-only read-only synthesis for worldwide university research baselines.

Evaluation reports are diagnostic and have no signed independent admission
themselves. In particular, apparent confidence, evidence digests, or behavioral
agreement cannot authorize an AUREX effect or establish model correctness.
"""

from __future__ import annotations

from dataclasses import dataclass

from .anytime_watch import AnytimeReport
from .behavioral_consensus import ConsensusReport
from .conformal_guard import BinarySet
from .holistic_axes import HolisticReport
from .shift_watch import ShiftReport


@dataclass(frozen=True, slots=True)
class SafetyReview:
    state: str
    issues: tuple[str, ...]
    authority: str = "NONE"
    signed_independent_admission: str = "NOT VERIFIED"
    automatic_execution: bool = False


def review_diagnostics(
    *,
    conformal: BinarySet | None = None,
    sequential: AnytimeReport | None = None,
    holistic: HolisticReport | None = None,
    behaviors: ConsensusReport | None = None,
    shift: ShiftReport | None = None,
) -> SafetyReview:
    """NO diagnostic input can return PASS; absent/missing evidence demotes."""
    issues: list[str] = []
    if conformal is None or conformal.decision != "CANDIDATE_ONLY":
        issues.append("Conformal decision abstained or unavailable")
    if sequential is None or sequential.gate != "NO_SIGNAL_NOT_PROOF":
        issues.append("Anytime false-pass monitoring unavailable or flagged")
    if holistic is None or holistic.missing:
        issues.append("Holistic evaluation metrics missing")
    if behaviors is None or behaviors.gate != "CONSISTENT_CANDIDATE_REVIEW_REQUIRED":
        issues.append("Code behavior comparison unavailable or inconclusive")
    if shift is None or shift.gate != "NO_DRIFT_SIGNAL_NOT_PROOF":
        issues.append("Distribution shift not ruled out")
    return SafetyReview("HOLD" if issues else "INDEPENDENT_REVIEW_REQUIRED", tuple(issues))
