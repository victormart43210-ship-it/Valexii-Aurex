"""Reality Gate: durable state and evidence integrity regression tests."""

import pytest

from aurex.database import create_job, get_job, record_evidence, update_job_state


def test_terminal_state_cannot_be_rewritten(tmp_path):
    db = str(tmp_path / "jobs.sqlite")
    create_job(db, "job-1", "regression_scan", {})
    assert update_job_state(db, "job-1", "running")["state"] == "running"
    assert update_job_state(db, "job-1", "succeeded")["state"] == "succeeded"
    assert update_job_state(db, "job-1", "failed") is None
    assert update_job_state(db, "job-1", "succeeded") is None
    assert get_job(db, "job-1")["state"] == "succeeded"


def test_illegal_state_transition_rejected(tmp_path):
    db = str(tmp_path / "jobs.sqlite")
    create_job(db, "job-2", "regression_scan", {})
    assert update_job_state(db, "job-2", "succeeded") is None
    assert get_job(db, "job-2")["state"] == "queued"


def test_evidence_cannot_be_overwritten(tmp_path):
    db = str(tmp_path / "jobs.sqlite")
    record_evidence(db, "ev-1", "regression_scan", "test_run", "a" * 64, "first")
    with pytest.raises(Exception):
        record_evidence(db, "ev-1", "regression_scan", "test_run", "b" * 64, "second")
