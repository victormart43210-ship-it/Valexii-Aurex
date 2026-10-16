"""Helsinki Mathematical Intelligence Module for AUREX (PR #53 reconciled)."""

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
    information_gain_bits: float = Field(default=1.0, ge=0.0)
    evaluated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def evaluate_math_problem(
    problem: MathematicalProblem, candidate_answer: str
) -> HelsinkiMathEvaluation:
    clean_target = problem.solution_target.strip().lower()
    clean_candidate = candidate_answer.strip().lower()
    correct = clean_target in clean_candidate or clean_candidate in clean_target
    info_gain = 1.0 if correct else 0.0

    return HelsinkiMathEvaluation(
        problem_id=problem.problem_id,
        extracted_answer=candidate_answer,
        correct=correct,
        information_gain_bits=info_gain,
    )
