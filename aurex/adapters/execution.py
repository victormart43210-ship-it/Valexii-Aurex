"""Auditable execution records; execution success is never answer verification."""

import hashlib
import time
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.adapters.base import GenerationSettings, ModelAdapter, ModelAnswer
from aurex.provenance import fingerprint


class ModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    quantization: str | None = None
    runtime: str = "unspecified"
    identity_status: Literal["DECLARED"] = "DECLARED"


class InferenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    input_id: str
    input_sha256: str
    output_sha256: str | None
    output: str | None
    started_at: datetime
    elapsed_seconds: float
    status: Literal["PASS", "FAIL"]
    error_code: str | None
    model: ModelSpec
    generation: GenerationSettings
    input_tokens: int | None = None
    output_tokens: int | None = None
    evidence_ids: tuple[str, ...] = ()
    verification_status: Literal["NOT VERIFIED"] = "NOT VERIFIED"


class ExecutionFailure(RuntimeError):
    pass


def _answer(adapter: ModelAdapter, prompt: str, spec: ModelSpec) -> ModelAnswer:
    try:
        answer = ModelAnswer.model_validate(adapter.answer(prompt).model_dump())
        if (
            answer.model != spec.model
            or answer.provider != spec.provider
            or not answer.text.strip()
        ):
            raise ValueError("Invalid response identity or empty content")
        return answer
    except Exception as exc:
        # Do not serialize exception text, cause, headers, URLs, or traceback.
        code = "TIMEOUT" if isinstance(exc, TimeoutError) else "PROVIDER_OR_SCHEMA_FAILURE"
        raise ExecutionFailure(code) from exc


class InferenceClient:
    def __init__(self, adapter: ModelAdapter, spec: ModelSpec) -> None:
        self.adapter = adapter
        self.spec = spec
        self.generation = getattr(adapter, "generation", GenerationSettings())

    def config_digest(self) -> str:
        return fingerprint(
            {"model": self.spec.model_dump(), "generation": self.generation.model_dump()}
        )

    def run(
        self, input_id: str, prompt: str, evidence_ids: tuple[str, ...] = ()
    ) -> InferenceRecord:
        started = datetime.now(UTC)
        clock = time.perf_counter()
        answer = None
        error = None
        try:
            answer = _answer(self.adapter, prompt, self.spec)
        except ExecutionFailure as exc:
            error = str(exc)
        return InferenceRecord(
            input_id=input_id,
            input_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            output=answer.text if answer else None,
            output_sha256=hashlib.sha256(answer.text.encode()).hexdigest() if answer else None,
            started_at=started,
            elapsed_seconds=time.perf_counter() - clock,
            status="PASS" if answer else "FAIL",
            error_code=error,
            model=self.spec,
            generation=self.generation,
            input_tokens=answer.input_tokens if answer else None,
            output_tokens=answer.output_tokens if answer else None,
            evidence_ids=evidence_ids,
        )
