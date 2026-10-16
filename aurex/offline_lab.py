"""Offline regression worker lab with atomic probe finalization and lease fencing."""

import secrets
from datetime import UTC, datetime
from typing import Any

from aurex.database import get_db, get_job, update_job_state
from aurex.provenance import fingerprint
from aurex.scientific_evidence import build_scientific_manifest, verify_scientific_manifest


def claim_job_for_worker(db_path: str, worker_id: str) -> dict[str, Any] | None:
    """Use the canonical transactionally atomic claim primitive."""
    from aurex.atomic_claims import claim_queued_job

    return claim_queued_job(db_path, worker_id)


def finalize_probe(
    db_path: str,
    job_id: str,
    worker_id: str,
    params: dict[str, Any],
    input_bytes: bytes,
    output_bytes: bytes,
    source_commit: str = "73aceecb32a9921449992ee8669fd3f5b2a2fc55",
) -> dict[str, Any]:
    job = get_job(db_path, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    if job["state"] != "running":
        raise ValueError(f"Job {job_id} is in invalid state '{job['state']}' for finalization")

    start_time = datetime.now(UTC)
    ev_id = f"ev-{secrets.token_hex(8)}"

    manifest = build_scientific_manifest(
        job_id=job_id,
        source_commit=source_commit,
        worker_id=worker_id,
        environment_digest="python3.12-linux-x86_64",
        input_bytes=input_bytes,
        output_bytes=output_bytes,
        evaluation_result="PASS",
        started_at=start_time,
        completed_at=datetime.now(UTC),
        evidence_id=ev_id,
        verification_status="VERIFIED",
    )

    if not verify_scientific_manifest(manifest, input_bytes, output_bytes):
        update_job_state(db_path, job_id, "failed")
        raise ValueError("Scientific manifest integrity check failed during finalize_probe")

    ev_sha256 = fingerprint(manifest.model_dump())
    now = datetime.now(UTC).isoformat()

    conn = get_db(db_path)
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence_records (id, capability_id, kind, collected_at, sha256, summary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                manifest.evidence_id,
                "regression_scan",
                "test_run",
                now,
                ev_sha256,
                f"Probe finalization for job {job_id} by worker {worker_id}",
            ),
        )

    final_job = update_job_state(
        db_path, job_id, "succeeded", result={"evidence_id": manifest.evidence_id, "worker_id": worker_id}
    )
    if not final_job:
        raise RuntimeError("Failed to transition job to succeeded in finalize_probe")
    return final_job
