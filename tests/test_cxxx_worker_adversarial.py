"""Adversarial worker lease fencing and SQLite evidence security tests for KUSANAGI CXXX."""
from __future__ import annotations

import hashlib
import json

import pytest

from aurex.database import create_job, get_job
from aurex.fenced_worker import cancel_job, claim_job, fail_job, finalize_job


def test_cxxx_atomic_job_creation_and_idempotency(tmp_path) -> None:
    db_path = str(tmp_path / "test_cxxx_jobs.sqlite")
    job1 = create_job(db_path, "job-cxxx-001", "regression_scan", {"probe": "sqlite_roundtrip_v1"}, idempotency_key="key-001")
    assert job1["state"] == "queued"

    job2 = create_job(db_path, "job-cxxx-001", "regression_scan", {"probe": "sqlite_roundtrip_v1"}, idempotency_key="key-001")
    assert job2["id"] == job1["id"]

    with pytest.raises(ValueError, match="Idempotency key collision with different request"):
        create_job(db_path, "job-cxxx-002", "regression_scan", {"probe": "different"}, idempotency_key="key-001")


def test_cxxx_worker_lease_expiry_and_fail_job(tmp_path) -> None:
    db_path = str(tmp_path / "test_cxxx_fencing.sqlite")
    create_job(db_path, "job-cxxx-002", "regression_scan", {"probe": "sqlite_roundtrip_v1"}, idempotency_key="key-002")
    claimed = claim_job(db_path, "job-cxxx-002", "worker-1", ttl_seconds=1)
    assert claimed is not None
    assert claimed["state"] == "running"

    failed = fail_job(db_path, "job-cxxx-002", "worker-1", str(claimed["lease_token"]), int(claimed["lease_generation"]))
    assert isinstance(failed, dict)
    assert failed["state"] == "failed"

    failed_job = get_job(db_path, "job-cxxx-002")
    assert failed_job["state"] == "failed"
    assert failed_job["lease_token"] is None


def test_cxxx_stale_worker_cannot_finalize_job(tmp_path) -> None:
    db_path = str(tmp_path / "test_cxxx_stale.sqlite")
    create_job(db_path, "job-cxxx-003", "regression_scan", {"probe": "sqlite_roundtrip_v1"}, idempotency_key="key-003")
    claimed1 = claim_job(db_path, "job-cxxx-003", "worker-1", ttl_seconds=1)
    assert claimed1 is not None

    cancel_job(db_path, "job-cxxx-003")

    obs = {"probe": "sqlite_roundtrip_v1", "executed": True, "passed": True, "sha256": "a" * 64, "verification": "NOT VERIFIED"}
    digest = hashlib.sha256(json.dumps(obs, sort_keys=True).encode()).hexdigest()

    with pytest.raises(ValueError, match="Worker lease invalid, expired, cancelled, or superseded"):
        finalize_job(
            db_path,
            "job-cxxx-003",
            "worker-1",
            str(claimed1["lease_token"]),
            int(claimed1["lease_generation"]),
            obs,
            digest,
            "ev-001",
        )
