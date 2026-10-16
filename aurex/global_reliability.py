"""Global University Reliability Safeguards for AUREX (PR #54 reconciled)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReliabilityAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    assessment_id: str = Field(min_length=1)
    conformal_score: float = Field(default=0.95, ge=0.0, le=1.0)
    abstained: bool = False
    distribution_shift_detected: bool = False
    decision: Literal["ACCEPT", "ABSTAIN", "REJECT"] = "ACCEPT"


def evaluate_reliability(
    conformal_score: float,
    distribution_shift: bool = False,
    min_confidence: float = 0.8,
) -> ReliabilityAssessment:
    abstained = False
    decision: Literal["ACCEPT", "ABSTAIN", "REJECT"] = "ACCEPT"

    if distribution_shift or conformal_score < min_confidence:
        abstained = True
        decision = "ABSTAIN"

    if conformal_score < 0.2:
        decision = "REJECT"

    return ReliabilityAssessment(
        assessment_id="rel-001",
        conformal_score=conformal_score,
        abstained=abstained,
        distribution_shift_detected=distribution_shift,
        decision=decision,
    )
