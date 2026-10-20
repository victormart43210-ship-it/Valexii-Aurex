"""Local Qwen Evaluation Harness Module for AUREX (Project Qwen Ascension)."""

import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint


class QwenEvalTask(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)
    task_category: Literal[
        "instruction_following",
        "python_debugging",
        "json_compliance",
        "security_explanation",
        "evidence_abstention",
    ]
    prompt: str = Field(min_length=1)
    expected_keyword: str | None = None


class QwenEvalResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    passed: bool
    latency_ms: float = Field(default=0.0, ge=0.0)
    evaluated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def digest_sha256(self) -> str:
        body = {
            "task_id": self.task_id,
            "model_name": self.model_name,
            "passed": self.passed,
        }
        return fingerprint(body)


def evaluate_qwen_task(
    task: QwenEvalTask, model_name: str, candidate_response: str, latency_ms: float = 0.0
) -> QwenEvalResult:
    if not candidate_response or not candidate_response.strip():
        return QwenEvalResult(
            task_id=task.task_id,
            model_name=model_name,
            passed=False,
            latency_ms=latency_ms,
        )

    clean_resp = candidate_response.strip().lower()
    passed = True

    if task.expected_keyword and task.expected_keyword.lower() not in clean_resp:
        passed = False

    if task.task_category == "json_compliance":
        try:
            parsed = json.loads(candidate_response.strip())
            if not isinstance(parsed, (dict, list)):
                passed = False
        except (json.JSONDecodeError, ValueError):
            passed = False

    elif task.task_category == "evidence_abstention":
        if "not verified" not in clean_resp and "insufficient evidence" not in clean_resp:
            passed = False

    elif task.task_category == "python_debugging":
        if len(clean_resp) < 5:
            passed = False

    return QwenEvalResult(
        task_id=task.task_id,
        model_name=model_name,
        passed=passed,
        latency_ms=latency_ms,
    )
