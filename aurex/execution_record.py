"""Repository-only execution record scaffolding for durable job metadata.

This model captures the execution identifiers and timestamps required by the
handoff, without claiming a live backend is connected to a website or model.

NOT VERIFIED UNTIL LIVE STAGING ACCESS IS PROVIDED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class ExecutionRecord:
    job_id: str
    workflow_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    worker_id: str | None = None
    evidence_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    queued_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    verification_at: str | None = None
    model_identifier: str | None = None
    model_version: str | None = None
    runtime: str | None = None
    output_digest: str | None = None
    error: dict[str, str] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "workflow_id": self.workflow_id,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "worker_id": self.worker_id,
            "evidence_id": self.evidence_id,
            "created_at": self.created_at,
            "queued_at": self.queued_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "verification_at": self.verification_at,
            "model_identifier": self.model_identifier,
            "model_version": self.model_version,
            "runtime": self.runtime,
            "output_digest": self.output_digest,
            "error": self.error,
        }
