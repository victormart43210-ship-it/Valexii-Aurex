"""Paired evaluation primitives for base-vs-governed experiments."""

from pydantic import BaseModel, Field


class EvalItem(BaseModel):
    item_id: str
    prompt: str
    reference: str | None = None


class EvalOutcome(BaseModel):
    item_id: str
    base_correct: bool | None = None
    governed_correct: bool | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


def relative_uplift(base_score: float, governed_score: float) -> float | None:
    if base_score <= 0:
        return None
    return (governed_score - base_score) / base_score
