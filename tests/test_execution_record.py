import uuid

import pytest

from aurex.database import create_job, get_job, record_evidence, update_job_state
from aurex.execution_record import ExecutionRecord
from aurex.tracing import TraceContext, current_trace, trace_context


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "aurex-test.db")


def test_create_job_and_trace_context(tmp_db):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    trace = trace_context(request_id="req-123", job_id=job_id)
    created = create_job(tmp_db, job_id, "regression_scan", {"x": 1}, request_id="req-123", trace_id=trace.trace_id)
    assert created["state"] == "queued"
    assert get_job(tmp_db, job_id)["request_id"] == "req-123"
    assert current_trace() is not None
    assert current_trace().trace_id == trace.trace_id


def test_update_job_state_records_evidence_and_error(tmp_db):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    create_job(tmp_db, job_id, "regression_scan", {"a": 2})
    ev = record_evidence(tmp_db, "ev-1", "regression_scan", "test_run", "abc123", "test evidence")
    updated = update_job_state(
        tmp_db,
        job_id,
        "succeeded",
        result={"evidence_id": ev["id"]},
        worker_id="worker-1",
        evidence_id=ev["id"],
        error={"type": "none"},
    )
    assert updated is not None
    assert updated["state"] == "succeeded"
    assert updated["evidence_id"] == "ev-1"
    assert updated["worker_id"] == "worker-1"


def test_execution_record_roundtrip():
    rec = ExecutionRecord(
        job_id="job-1",
        request_id="req-1",
        trace_id="trace-1",
        span_id="span-1",
        worker_id="worker-1",
        evidence_id="ev-1",
    )
    payload = rec.to_dict()
    assert payload["job_id"] == "job-1"
    assert payload["trace_id"] == "trace-1"


def test_trace_context_helper():
    ctx = TraceContext.new(request_id="r", job_id="j")
    assert ctx.request_id == "r"
    assert ctx.job_id == "j"
    assert len(ctx.trace_id) >= 32
