"""Execution-trace helpers and correlation IDs for repository-only instrumentation.

This module provides a minimal, dependency-light trace context that can be used by
API and job execution code without requiring a live OpenTelemetry exporter.

NOT VERIFIED UNTIL LIVE STAGING ACCESS IS PROVIDED.
"""
from __future__ import annotations

import contextvars
import secrets
from collections.abc import Iterator
from contextlib import contextmanager
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    span_id: str
    request_id: str | None = None
    job_id: str | None = None

    @classmethod
    def new(cls, *, request_id: str | None = None, job_id: str | None = None) -> TraceContext:
        return cls(
            trace_id=uuid.uuid4().hex,
            span_id=secrets.token_hex(8),
            request_id=request_id,
            job_id=job_id,
        )


_current_trace: contextvars.ContextVar[TraceContext | None] = contextvars.ContextVar(
    "aurex.current_trace",
    default=None,
)


def current_trace() -> TraceContext | None:
    return _current_trace.get()


def trace_context(*, request_id: str | None = None, job_id: str | None = None) -> TraceContext:
    context = TraceContext.new(request_id=request_id, job_id=job_id)
    _current_trace.set(context)
    return context


@contextmanager
def scoped_trace_context(
    *, request_id: str | None = None, job_id: str | None = None
) -> Iterator[TraceContext]:
    """Bound correlation IDs to a scope and restore the previous context.

    A scope is NOT an OpenTelemetry exporter, authentication, or independent
    attestation. Avoid using raw tokens or sensitive data as context IDs.
    """
    context = TraceContext.new(request_id=request_id, job_id=job_id)
    token = _current_trace.set(context)
    try:
        yield context
    finally:
        _current_trace.reset(token)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
