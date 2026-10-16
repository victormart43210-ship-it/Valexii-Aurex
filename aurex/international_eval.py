"""International AI Evaluation & Bounded Benchmark Adapter (Inspect AI & PR #35 inspired)."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint


class InternationalEvalObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    benchmark_id: str = Field(min_length=1)
    eval_framework: str = "international-v1"
    prompt: str = Field(min_length=1)
    response_text: str = Field(min_length=1)
    expected_pattern: str | None = None
    passed: bool
    evaluated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def digest_sha256(self) -> str:
        body = {
            "benchmark_id": self.benchmark_id,
            "eval_framework": self.eval_framework,
            "prompt": self.prompt,
            "response_text": self.response_text,
            "passed": self.passed,
        }
        return fingerprint(body)


def evaluate_international_response(
    benchmark_id: str,
    prompt: str,
    response_text: str,
    expected_pattern: str | None = None,
) -> InternationalEvalObservation:
    passed = True
    if expected_pattern and expected_pattern.lower() not in response_text.lower():
        passed = False
    return InternationalEvalObservation(
        benchmark_id=benchmark_id,
        prompt=prompt,
        response_text=response_text,
        expected_pattern=expected_pattern,
        passed=passed,
    )
