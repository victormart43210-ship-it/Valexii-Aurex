"""Unit tests for OpenTelemetry request tracing and secret redaction."""

from __future__ import annotations

import pytest

from aurex.telemetry import (
    clear_trace_buffer,
    format_traceparent,
    generate_span_id,
    generate_trace_id,
    get_recent_traces,
    sanitize_telemetry_value,
    start_span,
)


def test_w3c_trace_and_span_id_formats() -> None:
    trace_id = generate_trace_id()
    span_id = generate_span_id()
    assert len(trace_id) == 32
    assert len(span_id) == 16
    assert int(trace_id, 16) >= 0
    assert int(span_id, 16) >= 0

    parent = format_traceparent(trace_id, span_id, sampled=True)
    assert parent == f"00-{trace_id}-{span_id}-01"


def test_telemetry_secret_redaction() -> None:
    raw = {
        "user": "operator_1",
        "authorization": "Bearer secret_token_abc123",
        "api_key": "sk-proj-xyz987654321",
        "nested": {
            "password": "super_secret_pass",
            "safe_field": "public_metadata",
        },
        "tokens_list": ["Bearer token1", "safe_item"],
    }
    cleaned = sanitize_telemetry_value(raw)
    assert cleaned["user"] == "operator_1"
    assert cleaned["authorization"] == "[REDACTED_KEY]"
    assert cleaned["api_key"] == "[REDACTED_KEY]"
    assert cleaned["nested"]["password"] == "[REDACTED_KEY]"
    assert cleaned["nested"]["safe_field"] == "public_metadata"
    assert cleaned["tokens_list"] == ["[REDACTED_SECRET]", "safe_item"]


def test_span_context_manager_records_trace() -> None:
    clear_trace_buffer()
    with start_span("test_operation", attributes={"client": "valexii-web"}) as span:
        assert span.trace_id is not None
        assert span.span_id is not None
        assert span.status == "OK"

    traces = get_recent_traces()
    assert len(traces) == 1
    assert traces[0]["name"] == "test_operation"
    assert traces[0]["status"] == "OK"
    assert traces[0]["attributes"]["client"] == "valexii-web"
    assert traces[0]["duration_ms"] >= 0.0


def test_span_records_exception() -> None:
    clear_trace_buffer()
    with pytest.raises(ValueError, match="simulated failure"):
        with start_span("failing_operation"):
            raise ValueError("simulated failure")

    traces = get_recent_traces()
    assert len(traces) == 1
    assert traces[0]["name"] == "failing_operation"
    assert traces[0]["status"] == "ERROR"
    assert traces[0]["error_category"] == "ValueError"
