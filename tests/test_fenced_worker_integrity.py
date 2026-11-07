"""Independent worker ownership, cancellation and evidence-integrity tests."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from aurex.database import create_job, get_job, list_evidence
from aurex.fenced_worker import cancel_job, claim_job, finalize_job


def _make_job(db: str, key: str = "unique"):
    return create_job(db, "job-one", "regression_scan", {"probe": "sqlite_roundtrip_v1"}, idempotency_key=key)


def _finalize(db: str, claimed: dict, observation: dict, evidence_id: str = "ev-one"):
    digest = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
    return finalize_job(db, claimed["id"], claimed["worker_id"], claimed["lease_token"],
                        claimed["lease_generation"], observation, digest, evidence_id)


def test_exactly_one_of_100_concurrent_claims(tmp_path):
    db = str(tmp_path / "concurrent.db")
    _make_job(db)
    with ThreadPoolExecutor(max_workers=20) as pool:
        claims = list(pool.map(lambda i: claim_job(db, "job-one", f"worker-{i}"), range(100)))
    winners = [c for c in claims if c is not None]
    assert len(winners) == 1
    assert winners[0]["lease_generation"] == 1


def test_finalization_atomic_and_unverified(tmp_path):
    db = str(tmp_path / "final.db")
    _make_job(db)
    claimed = claim_job(db, "job-one", "worker")
    assert claimed
    result = _finalize(db, claimed, {"executed": True, "verification": "NOT VERIFIED"})
    assert result["state"] == "succeeded"
    assert result["evidence_id"] == "ev-one"
    evidence = list_evidence(db)
    assert len(evidence) == 1
    assert evidence[0]["verification_status"] == "UNVERIFIED"


def test_cancel_fences_old_worker(tmp_path):
    db = str(tmp_path / "cancel.db")
    _make_job(db)
    claimed = claim_job(db, "job-one", "worker")
    assert claimed
    cancelled = cancel_job(db, "job-one")
    assert cancelled and cancelled["state"] == "cancelled"
    with pytest.raises(ValueError, match="lease"):
        _finalize(db, claimed, {"executed": True})
    assert list_evidence(db) == []
    assert get_job(db, "job-one")["state"] == "cancelled"


def test_invalid_digest_rejected_without_evidence(tmp_path):
    db = str(tmp_path / "digest.db")
    _make_job(db)
    claimed = claim_job(db, "job-one", "worker")
    assert claimed
    with pytest.raises(ValueError, match="digest"):
        finalize_job(db, "job-one", "worker", claimed["lease_token"],
                     claimed["lease_generation"], {"executed": True}, "0" * 64, "ev-one")
    assert list_evidence(db) == []
    assert get_job(db, "job-one")["state"] == "running"


def test_idempotency_reuses_same_job_and_rejects_changed_payload(tmp_path):
    db = str(tmp_path / "idempotency.db")
    original = _make_job(db)
    again = create_job(db, "another-id", "regression_scan", {"probe": "sqlite_roundtrip_v1"},
                       idempotency_key="unique")
    assert again["id"] == original["id"]
    with pytest.raises(ValueError, match="Idempotency"):
        create_job(db, "another-id", "regression_scan", {"probe": "different"},
                   idempotency_key="unique")
