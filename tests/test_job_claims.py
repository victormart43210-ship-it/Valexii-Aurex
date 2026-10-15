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


def test_atomic_evidence_finalization(tmp_path):
    import hashlib
    import sqlite3
    from aurex.database import finalize_probe, list_evidence
    db = str(tmp_path / "atomic.db")
    create_job(db, "job-atomic", "regression_scan", {})
    expiry = (datetime.now(UTC) + timedelta(minutes=1)).isoformat()
    assert claim_queued_job(db, "job-atomic", "worker", "lease-good", expiry)
    digest = hashlib.sha256(b"local-proof").hexdigest()
    assert finalize_probe(db, "job-atomic", "wrong-lease", {"ok": True},
                          "evidence-wrong", digest, "not verified") is None
    assert list_evidence(db) == []
    finished = finalize_probe(db, "job-atomic", "lease-good", {"ok": True},
                              "evidence-good", digest, "not verified")
    assert finished is not None
    assert finished["state"] == "succeeded"
    assert finished["evidence_id"] == "evidence-good"
    evidence = list_evidence(db)
    assert len(evidence) == 1
    assert evidence[0]["verification_status"] == "UNVERIFIED"
    assert finalize_probe(db, "job-atomic", "lease-good", {"ok": True},
                          "evidence-repeat", digest, "not verified") is None
    assert len(list_evidence(db)) == 1


def test_expired_claim_cannot_create_evidence(tmp_path):
    import hashlib
    from aurex.database import finalize_probe, list_evidence
    db = str(tmp_path / "expired-atomic.db")
    create_job(db, "expired-job", "regression_scan", {})
    past = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    assert claim_queued_job(db, "expired-job", "worker", "expired-token", past)
    assert finalize_probe(db, "expired-job", "expired-token", {},
                          "expired-evidence", hashlib.sha256(b"x").hexdigest(),
                          "unverified") is None
    assert list_evidence(db) == []
