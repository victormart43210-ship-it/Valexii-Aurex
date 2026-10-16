"""Concurrency and fail-closed tests for SQLite job claiming."""
from concurrent.futures import ThreadPoolExecutor

from aurex.atomic_claims import claim_queued_job
from aurex.database import create_job, get_job


def test_concurrent_claims_are_unique(tmp_path):
    db = str(tmp_path / "claims.db")
    for i in range(10):
        create_job(db, f"job-{i}", "regression_scan", {"i": i})

    with ThreadPoolExecutor(max_workers=6) as pool:
        claims = list(pool.map(lambda i: claim_queued_job(db, f"worker-{i}"), range(18)))
    ids = [str(c["id"]) for c in claims if c is not None]
    assert len(ids) == 10
    assert len(set(ids)) == 10
    assert all(get_job(db, job_id)["state"] == "running" for job_id in ids)


def test_empty_queue_returns_none(tmp_path):
    assert claim_queued_job(str(tmp_path / "empty.db"), "worker-1") is None


def test_worker_id_is_required(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        claim_queued_job(str(tmp_path / "claims.db"), " ")
