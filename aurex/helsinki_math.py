"""Helsinki Mathematical Intelligence Module for AUREX (PR #53 & KUSANAGI LXIX reconciled)."""

import re
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class MathematicalProblem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    problem_id: str = Field(min_length=1)
    domain: str = "algebra"
    prompt: str = Field(min_length=1)
    solution_target: str = Field(min_length=1)


class HelsinkiMathEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    problem_id: str = Field(min_length=1)
    extracted_answer: str = Field(min_length=1)
    correct: bool
    information_gain_bits: float = Field(default=0.0, ge=0.0)
    evaluated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def _normalize_tokens(text: str) -> list[str]:
    # Strip whitespace and tokenize non-whitespace mathematical tokens
    tokens = re.findall(r"[a-zA-Z0-9\.]+|[^\s\w]", text.strip().lower())
    return tokens


def evaluate_math_problem(
    problem: MathematicalProblem, candidate_answer: str
) -> HelsinkiMathEvaluation:
    target_tokens = _normalize_tokens(problem.solution_target)
    candidate_tokens = _normalize_tokens(candidate_answer)

    # Exact token equality check prevents "2" matching "20"
    correct = target_tokens == candidate_tokens

    # Information gain requires actual correct verification
    info_gain = 1.0 if correct else 0.0

    return HelsinkiMathEvaluation(
        problem_id=problem.problem_id,
        extracted_answer=candidate_answer,
        correct=correct,
        information_gain_bits=info_gain,
    )
