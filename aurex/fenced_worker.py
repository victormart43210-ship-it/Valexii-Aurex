"""Atomic SQLite worker ownership and evidence finalization.

An execution observation is NOT independent verification.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any

from aurex.database import get_db, get_job


def _now() -> datetime:
    return datetime.now(UTC)


def _ensure_generation(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    if "lease_generation" not in cols:
        conn.execute("ALTER TABLE jobs ADD COLUMN lease_generation INTEGER NOT NULL DEFAULT 0")


def claim_job(db_path: str, job_id: str, worker_id: str, ttl_seconds: int = 60) -> dict[str, Any] | None:
    if not worker_id or not 1 <= ttl_seconds <= 3600:
        raise ValueError("Invalid worker or lease TTL")
    conn = get_db(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_generation(conn)
        now = _now()
        token = secrets.token_hex(24)
        cur = conn.execute(
            """UPDATE jobs SET state='running', worker_id=?, lease_token=?,
               lease_expires_at=?, lease_generation=lease_generation+1, updated_at=?
               WHERE id=? AND (state='queued' OR
                 (state='running' AND lease_expires_at IS NOT NULL AND lease_expires_at<=?))""",
            (worker_id, token, (now + timedelta(seconds=ttl_seconds)).isoformat(),
             now.isoformat(), job_id, now.isoformat()),
        )
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone() if cur.rowcount == 1 else None
        conn.commit()
        return dict(row) if row else None
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def finalize_job(
    db_path: str, job_id: str, worker_id: str, token: str, generation: int,
    observation: dict[str, Any], digest: str, evidence_id: str,
) -> dict[str, Any]:
    canonical = json.dumps(observation, sort_keys=True).encode()
    if hashlib.sha256(canonical).hexdigest() != digest:
        raise ValueError("Observation digest mismatch")
    conn = get_db(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_generation(conn)
        now = _now().isoformat()
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if (row is None or row["state"] != "running" or row["worker_id"] != worker_id
                or row["lease_token"] != token or row["lease_generation"] != generation
                or not row["lease_expires_at"] or row["lease_expires_at"] <= now):
            raise ValueError("Worker lease invalid, expired, cancelled, or superseded")
        conn.execute(
            """INSERT INTO evidence_records
               (id, capability_id, kind, collected_at, sha256, summary,
                integrity_status, verification_status)
               VALUES (?, 'regression_scan', 'offline_probe', ?, ?,
                ?, 'RECORDED', 'UNVERIFIED')""",
            (evidence_id, now, digest, f"Real SQLite observation for {job_id}; independently NOT VERIFIED"),
        )
        cur = conn.execute(
            """UPDATE jobs SET state='succeeded', updated_at=?, evidence_id=?, result_json=?,
               lease_token=NULL, lease_expires_at=NULL
               WHERE id=? AND state='running' AND worker_id=? AND lease_token=?
               AND lease_generation=? AND lease_expires_at>?""",
            (now, evidence_id, json.dumps({"evidence_id": evidence_id, "observation": observation}),
             job_id, worker_id, token, generation, now),
        )
        if cur.rowcount != 1:
            raise ValueError("Worker lost authority before finalization")
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
    result = get_job(db_path, job_id)
    if result is None:
        raise RuntimeError("Committed job not found")
    return result


def fail_job(
    db_path: str, job_id: str, worker_id: str, token: str, generation: int,
) -> bool:
    """Record a redacted failure only while the caller still owns a live lease.

    A false return means no write authority; callers must not force a transition.
    Database errors propagate so callers cannot mistake unavailable storage for
    a durable failure record. No exception text or model content is persisted.
    """
    conn = get_db(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_generation(conn)
        now = _now().isoformat()
        cur = conn.execute(
            """UPDATE jobs SET state='failed', updated_at=?, error_json=?,
               lease_token=NULL, lease_expires_at=NULL
               WHERE id=? AND state='running' AND worker_id=? AND lease_token=?
               AND lease_generation=? AND lease_expires_at>?""",
            (now, json.dumps({"kind": "EXECUTION_FAILURE"}), job_id,
             worker_id, token, generation, now),
        )
        conn.commit()
        return cur.rowcount == 1
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancel_job(db_path: str, job_id: str) -> dict[str, Any] | None:
    conn = get_db(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_generation(conn)
        cur = conn.execute(
            """UPDATE jobs SET state='cancelled', updated_at=?,
               lease_token=NULL, lease_expires_at=NULL, lease_generation=lease_generation+1
               WHERE id=? AND state IN ('queued', 'running')""",
            (_now().isoformat(), job_id),
        )
        conn.commit()
        if cur.rowcount != 1:
            return None
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
    return get_job(db_path, job_id)
