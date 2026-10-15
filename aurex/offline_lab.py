"""Explicitly opt-in, zero-cost deterministic integration probe; NOT a model worker."""
from __future__ import annotations

import hashlib
import json
import os
from uuid import uuid4

from aurex.database import create_job, get_job, record_evidence, update_job_state


def run_offline_probe(db_path: str, idempotency_key: str | None = None) -> dict:
    """Persist a bounded local probe; never invoke an LLM, network or subprocess."""
    if os.environ.get("AUREX_ENABLE_OFFLINE_LAB") != "1":
        raise RuntimeError("Offline lab disabled")
    params = {"probe": "sqlite_roundtrip_v1", "mode": "deterministic", "cost_usd": 0}
    job_id = str(uuid4())
    job = create_job(db_path, job_id, "regression_scan", params, idempotency_key=idempotency_key)
    if job["state"] != "queued":
        return job
    # A repeated idempotency key may resolve to an already-queued job.
    # Never claim that such a job was executed by this invocation.
    running = update_job_state(db_path, job["id"], "running", worker_id="offline_lab_v1")
    if running is None:
        raise RuntimeError("Job claim failed")
    observed = get_job(db_path, job["id"])
    if observed is None or observed["state"] != "running":
        raise RuntimeError("SQLite roundtrip failed")
    payload = {"probe": "sqlite_roundtrip_v1", "job_id": job["id"], "result": "local_roundtrip_observed"}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    evidence_id = str(uuid4())
    record_evidence(db_path, evidence_id, "offline_lab", "deterministic_probe", digest,
                    "Local SQLite roundtrip observed; NOT independently verified",
                    source_ref=job["id"], integrity_status="HASHED",
                    verification_status="UNVERIFIED")
    finished = update_job_state(db_path, job["id"], "succeeded", result=payload,
                                worker_id="offline_lab_v1", evidence_id=evidence_id)
    if finished is None:
        raise RuntimeError("Job completion failed")
    return finished
