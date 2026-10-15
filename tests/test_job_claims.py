"""Atomic claim and expiry fencing tests."""
from datetime import UTC, datetime, timedelta

from aurex.database import claim_queued_job, create_job, finish_claimed_job, get_job


def test_only_one_claim_wins(tmp_path):
    db = str(tmp_path / "claims.db")
    create_job(db, "job1", "regression_scan", {})
    future = (datetime.now(UTC) + timedelta(minutes=1)).isoformat()
    assert claim_queued_job(db, "job1", "worker-a", "lease-a", future)
    assert claim_queued_job(db, "job1", "worker-b", "lease-b", future) is None
    assert finish_claimed_job(db, "job1", "lease-b", {"ok": True}) is None
    assert finish_claimed_job(db, "job1", "lease-a", {"ok": True})
    assert finish_claimed_job(db, "job1", "lease-a", {"ok": True}) is None


def test_expired_lease_cannot_finish(tmp_path):
    db = str(tmp_path / "expiry.db")
    create_job(db, "job2", "regression_scan", {})
    past = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    assert claim_queued_job(db, "job2", "worker-a", "lease-a", past)
    assert finish_claimed_job(db, "job2", "lease-a", {"ok": True}) is None
    assert get_job(db, "job2")["state"] == "running"


def test_idempotency_collision(tmp_path):
    db = str(tmp_path / "idem.db")
    first = create_job(db, "job3", "regression_scan", {"x": 1}, idempotency_key="key")
    second = create_job(db, "job4", "regression_scan", {"x": 1}, idempotency_key="key")
    assert first["id"] == second["id"]
    import pytest
    with pytest.raises(ValueError):
        create_job(db, "job5", "regression_scan", {"x": 2}, idempotency_key="key")
