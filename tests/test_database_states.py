import os
import tempfile
from pathlib import Path

import pytest

from aurex.database import create_job, get_job, update_job_state, record_evidence


def make_db(tmp_path: Path) -> str:
    return str(tmp_path / "test_aurex.db")


def test_terminal_state_immutability(tmp_path: Path):
    db = make_db(tmp_path)
    job_id = "job-terminal"
    # create job
    create_job(db, job_id, "regression_scan", {})
    # move to succeeded
    j = update_job_state(db, job_id, "succeeded")
    assert j["state"] == "succeeded"
    # attempt to move back to running (should be ignored)
    j2 = update_job_state(db, job_id, "running")
    assert j2["state"] == "succeeded"


def test_cancel_after_completion(tmp_path: Path):
    db = make_db(tmp_path)
    job_id = "job-cancel"
    create_job(db, job_id, "regression_scan", {})
    update_job_state(db, job_id, "succeeded")
    # attempting to cancel after success should not change state
    j = update_job_state(db, job_id, "cancelled")
    assert j["state"] == "succeeded"


def test_record_evidence_returns_row(tmp_path: Path):
    db = make_db(tmp_path)
    ev = record_evidence(db, "ev-1", "cap-1", "test", "a" * 64, "summary")
    assert ev["id"] == "ev-1"
    assert ev["capability_id"] == "cap-1"
    assert ev["sha256"] == "a" * 64
