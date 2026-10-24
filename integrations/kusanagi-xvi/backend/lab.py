"""Reproducible zero-cost AUREX Python labs; isolated temporary SQLite only.

Usage:
  python -m backend.lab              # staged, no execution
  python -m backend.lab --execute    # run two fictional SQLite probes locally

Does not access production, Railway, NVIDIA, customer documents or secrets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from . import store, supervisor, worker

PAYLOAD = b"aurex-offline-roundtrip-v1"
PARAMS = {"probe": "sqlite_roundtrip_v1"}


def sqlite_lab(db: str) -> dict[str, Any]:
    store.initialize(db)
    first = store.create_job(db, "regression_scan", PARAMS, "lab-idempotency-roundtrip-0001")
    again = store.create_job(db, "regression_scan", PARAMS, "lab-idempotency-roundtrip-0001")
    assert first["id"] == again["id"], "Idempotency mismatch"
    before = os.environ.get("AUREX_ENABLE_OFFLINE_LAB")
    try:
        os.environ["AUREX_ENABLE_OFFLINE_LAB"] = "true"
        ran = worker.once(worker_id="local-lab-roundtrip", db_path=db)
    finally:
        if before is None:
            os.environ.pop("AUREX_ENABLE_OFFLINE_LAB", None)
        else:
            os.environ["AUREX_ENABLE_OFFLINE_LAB"] = before
    evidence = store.evidence(db)
    job = store.get_job(db, first["id"])
    expected = hashlib.sha256(PAYLOAD).hexdigest()
    assert ran["status"] == "EXECUTED", "Worker failed"
    assert job is not None and job["state"] == "succeeded", "Job not durable"
    assert len(evidence) == 1 and evidence[0]["sha256"] == expected
    return {
        "name": "sqlite_roundtrip",
        "status": "PASS",
        "jobState": "succeeded",
        "evidenceDigestMatched": True,
        "idempotentReplay": True,
        "authority": "NONE",
        "independentVerification": "NOT VERIFIED",
    }


def fencing_lab(db: str) -> dict[str, Any]:
    store.initialize(db)
    cancelled = store.create_job(db, "regression_scan", PARAMS, "lab-fence-cancel-case-0001")
    first = store.claim(db, "worker-before-cancel")
    assert first is not None and first["id"] == cancelled["id"]
    assert store.cancel(db, cancelled["id"]) is not None
    assert store.fail_claim(db, first, "worker-before-cancel") is None, "Cancelled job revived"
    assert store.get_job(db, cancelled["id"])["state"] == "cancelled"

    second = store.create_job(db, "regression_scan", PARAMS, "lab-fence-takeover-case-0001")
    stale = store.claim(db, "old-worker")
    assert stale is not None and stale["id"] == second["id"]
    with store.connect(db) as conn:
        conn.execute("UPDATE jobs SET lease_expires_at=? WHERE id=?", ("2000-01-01T00:00:00+00:00", second["id"]))
    successor = store.claim(db, "new-worker")
    assert successor is not None and successor["lease_generation"] > stale["lease_generation"]
    assert store.fail_claim(db, stale, "old-worker") is None, "Stale worker demoted new lease"
    try:
        store.finalize(db, stale, "old-worker")
    except ValueError:
        pass
    else:
        raise AssertionError("Stale worker wrongly finalized")
    result = store.finalize(db, successor, "new-worker")
    assert result["state"] == "succeeded"
    assert len(store.evidence(db)) == 1, "Cancelled job manufactured evidence"
    return {
        "name": "lease_fencing",
        "status": "PASS",
        "cancelledJobPreserved": True,
        "staleWorkerRejected": True,
        "newLeaseSucceeded": True,
        "authority": "NONE",
        "independentVerification": "NOT VERIFIED",
    }


def run_labs() -> dict[str, Any]:
    """Use two disposable databases and no network or production state."""
    with tempfile.TemporaryDirectory(prefix="aurex-python-lab-") as directory:
        first = sqlite_lab(str(Path(directory) / "roundtrip.db"))
        second = fencing_lab(str(Path(directory) / "fencing.db"))
    return {
        "status": "LOCAL_OFFLINE_LABS_PASS",
        "labs": [first, second],
        "unixSupervisorConfig": "CHECKED",
        "authority": "NONE",
        "release": "HOLD",
        "independentEfficacy": "NOT VERIFIED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Default-staged, local-only AUREX Python labs")
    parser.add_argument("--execute", action="store_true", help="Run strictly local temporary SQLite checks")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({
            "status": "STAGED", "execute": "NOT RUN", "labs": ["sqlite_roundtrip", "lease_fencing"],
            "network": "NONE", "billing": "NONE", "authority": "NONE", "release": "HOLD",
        }, sort_keys=True))
        return
    # Build an explicit environment test with no mounted/production DB dependency.
    supervisor.validate_config({"AUREX_DB_PATH": "/tmp/aurex-lab.db", "PORT": "8080"})
    print(json.dumps(run_labs(), sort_keys=True))


if __name__ == "__main__":
    main()
