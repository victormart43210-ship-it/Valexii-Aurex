"""Reusable statistical comparison layer for paired experiments."""

import math

from pydantic import BaseModel, ConfigDict, Field


class PairedItemOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(min_length=1)
    baseline_correct: bool
    experimental_correct: bool


class PairedStatisticalReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    total_items: int = Field(ge=0)
    evaluated_items: int = Field(ge=0)
    abstentions: int = Field(ge=0)
    coverage: float = Field(ge=0.0, le=1.0)

    baseline_correct_count: int = Field(ge=0)
    experimental_correct_count: int = Field(ge=0)

    baseline_score: float = Field(ge=0.0, le=1.0)
    experimental_score: float = Field(ge=0.0, le=1.0)
    percentage_point_delta: float

    improved_count: int = Field(ge=0)
    regressed_count: int = Field(ge=0)
    unchanged_count: int = Field(ge=0)

    relative_uplift: float | None
    mcnemar_p_value: float | None
    mcnemar_statistic: float | None


def analyze_paired_outcomes(
    outcomes: tuple[PairedItemOutcome, ...],
    total_items: int | None = None,
) -> PairedStatisticalReport:
    evaluated = len(outcomes)
    total = total_items if total_items is not None else evaluated
    if total < evaluated:
        raise ValueError("total_items cannot be less than evaluated outcomes count")

    abstentions = total - evaluated
    coverage = (evaluated / total) if total > 0 else 0.0

    if evaluated == 0:
        return PairedStatisticalReport(
            total_items=total,
            evaluated_items=0,
            abstentions=abstentions,
            coverage=0.0,
            baseline_correct_count=0,
            experimental_correct_count=0,
            baseline_score=0.0,
            experimental_score=0.0,
            percentage_point_delta=0.0,
            improved_count=0,
            regressed_count=0,
            unchanged_count=0,
            relative_uplift=None,
            mcnemar_p_value=None,
            mcnemar_statistic=None,
        )

    base_correct = sum(1 for item in outcomes if item.baseline_correct)
    exp_correct = sum(1 for item in outcomes if item.experimental_correct)

    base_score = base_correct / evaluated
    exp_score = exp_correct / evaluated
    percentage_point_delta = (exp_score - base_score) * 100.0

    # Relative uplift is only mathematically valid when base_score > 0
    relative_uplift = (exp_score - base_score) / base_score if base_score > 0 else None

    # Contingency table counts for discordance
    improved = sum(
        1 for item in outcomes if not item.baseline_correct and item.experimental_correct
    )
    regressed = sum(
        1 for item in outcomes if item.baseline_correct and not item.experimental_correct
    )
    unchanged = sum(
        1
        for item in outcomes
        if (item.baseline_correct and item.experimental_correct)
        or (not item.baseline_correct and not item.experimental_correct)
    )

    # McNemar's test with continuity correction
    b = improved
    c = regressed
    discordant = b + c

    mcnemar_stat: float | None = None
    p_value: float | None = None

    if discordant > 0:
        mcnemar_stat = ((abs(b - c) - 0.5) ** 2) / discordant
        # Asymptotic chi-squared approximation with 1 degree of freedom: erfc(sqrt(stat/2))
        p_value = math.erfc(math.sqrt(mcnemar_stat / 2.0))

    return PairedStatisticalReport(
        total_items=total,
        evaluated_items=evaluated,
        abstentions=abstentions,
        coverage=coverage,
        baseline_correct_count=base_correct,
        experimental_correct_count=exp_correct,
        baseline_score=base_score,
        experimental_score=exp_score,
        percentage_point_delta=percentage_point_delta,
        improved_count=improved,
        regressed_count=regressed,
        unchanged_count=unchanged,
        relative_uplift=relative_uplift,
        mcnemar_p_value=p_value,
        mcnemar_statistic=mcnemar_stat,
    )
