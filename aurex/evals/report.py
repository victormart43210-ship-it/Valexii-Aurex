"""Score reporting that keeps percentage points separate from relative uplift."""

from pydantic import BaseModel

from aurex.evals.paired import relative_uplift


class PairedScoreReport(BaseModel):
    total: int
    base_correct: int
    governed_correct: int
    base_score: float
    governed_score: float
    percentage_point_delta: float
    relative_uplift: float | None


def build_report(total: int, base_correct: int, governed_correct: int) -> PairedScoreReport:
    if total <= 0:
        raise ValueError("total must be positive")
    if not (0 <= base_correct <= total and 0 <= governed_correct <= total):
        raise ValueError("correct counts must be between zero and total")
    base = base_correct / total
    governed = governed_correct / total
    return PairedScoreReport(
        total=total,
        base_correct=base_correct,
        governed_correct=governed_correct,
        base_score=base,
        governed_score=governed,
        percentage_point_delta=(governed - base) * 100.0,
        relative_uplift=relative_uplift(base, governed),
    )
