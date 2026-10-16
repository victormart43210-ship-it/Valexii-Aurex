"""Scoped trace context restores previous request correlation state."""

import pytest

from aurex.tracing import TraceContext, current_trace, scoped_trace_context


def test_scoped_context_restores_previous_span() -> None:
    original = current_trace()
    with scoped_trace_context(request_id="request-one", job_id="job-one") as outer:
        assert isinstance(outer, TraceContext)
        assert outer == current_trace()
        assert len(outer.trace_id) == 32
        with scoped_trace_context(request_id="request-two") as inner:
            assert current_trace() == inner
            assert inner.trace_id != outer.trace_id
            assert inner.request_id == "request-two"
        assert current_trace() == outer
    assert current_trace() == original


def test_scoped_context_cleans_up_after_exception() -> None:
    original = current_trace()
    with pytest.raises(RuntimeError, match="sample failure"):
        with scoped_trace_context():
            assert current_trace() is not None
            raise RuntimeError("sample failure")
    assert current_trace() == original
