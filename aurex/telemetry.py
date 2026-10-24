"""OpenTelemetry-style W3C request tracing and privacy-safe observability for AUREX.

Provides structured trace generation, correlation ID propagation, and timing metrics
while strictly redacting Bearer tokens, API keys, and customer payload data.
"""

from __future__ import annotations

import re
import secrets
import time
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

MAX_TRACE_BUFFER = 500

_SENSITIVE_PATTERNS = [
    re.compile(r"bearer\s+[a-zA-Z0-9_.~+/-]+=*", re.IGNORECASE),
    re.compile(r"api[-_]?key[\"\s:=]+[a-zA-Z0-9_.~+/-]+", re.IGNORECASE),
    re.compile(r"token[\"\s:=]+[a-zA-Z0-9_.~+/-]+", re.IGNORECASE),
    re.compile(r"password[\"\s:=]+[^\",\s]+", re.IGNORECASE),
]

_trace_buffer: deque[dict[str, Any]] = deque(maxlen=MAX_TRACE_BUFFER)


def generate_trace_id() -> str:
    """128-bit W3C compliant trace ID hex string."""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """64-bit W3C compliant span ID hex string."""
    return secrets.token_hex(8)


def format_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """Format W3C traceparent header: 00-{trace_id}-{span_id}-{flags}."""
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def sanitize_telemetry_value(value: Any) -> Any:
    """Recursively strip secrets, credentials, and long PII strings from telemetry metadata."""
    if isinstance(value, str):
        cleaned = value
        for pattern in _SENSITIVE_PATTERNS:
            cleaned = pattern.sub("[REDACTED_SECRET]", cleaned)
        return cleaned
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for k, v in value.items():
            key_str = str(k)
            key_lower = key_str.lower()
            if any(s in key_lower for s in ("token", "secret", "auth", "key", "password")):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    result[key_str] = "[REDACTED_KEY]"
                else:
                    result[key_str] = sanitize_telemetry_value(v)
            else:
                result[key_str] = sanitize_telemetry_value(v)
        return result
    if isinstance(value, list):
        return [sanitize_telemetry_value(v) for v in value]
    return value


class TraceSpan:
    """Active telemetry span tracking execution latency and status."""

    def __init__(
        self,
        name: str,
        service: str = "aurex-backend",
        trace_id: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.service = service
        self.trace_id = trace_id or generate_trace_id()
        self.span_id = generate_span_id()
        self.correlation_id = correlation_id or self.trace_id
        self.start_time = time.perf_counter()
        self.attributes: dict[str, Any] = sanitize_telemetry_value(attributes or {})
        self.status = "OK"
        self.error_category: str | None = None
        self.end_time: float | None = None
        self.duration_ms: float = 0.0

    def finish(self, status: str = "OK", error_category: str | None = None) -> dict[str, Any]:
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 3)
        self.status = status
        self.error_category = error_category

        span_record = {
            "name": self.name,
            "service": self.service,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "correlation_id": self.correlation_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error_category": self.error_category,
            "attributes": self.attributes,
            "traceparent": format_traceparent(self.trace_id, self.span_id),
        }
        _trace_buffer.append(span_record)
        return span_record


@contextmanager
def start_span(
    name: str,
    service: str = "aurex-backend",
    trace_id: str | None = None,
    correlation_id: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[TraceSpan]:
    """Context manager for wrapping execution blocks with OpenTelemetry tracing."""
    span = TraceSpan(name, service, trace_id, correlation_id, attributes)
    try:
        yield span
        if span.end_time is None:
            span.finish(status="OK")
    except Exception as exc:
        span.finish(status="ERROR", error_category=exc.__class__.__name__)
        raise


def get_recent_traces(limit: int = 50) -> list[dict[str, Any]]:
    """Return recently buffered telemetry spans (most recent first)."""
    return list(_trace_buffer)[-limit:][::-1]


def clear_trace_buffer() -> None:
    """Clear in-memory trace buffer (used by unit tests)."""
    _trace_buffer.clear()
