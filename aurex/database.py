"""Durable SQLite job and evidence store for AUREX backend.

This module provides the repository's durable job engine. It maintains the
canonical job lifecycle and evidence records used by the server-side API.

NOT VERIFIED UNTIL LIVE STAGING ACCESS IS PROVIDED.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from typing import Any

DEFAULT_DB_PATH = os.environ.get("AUREX_DB_PATH", "/tmp/aurex_jobs.db")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if cursor.fetchone():
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(jobs)").fetchall()]
        if "params" in cols and "params_json" not in cols:
            conn.close()
            raise ValueError("Legacy database schema detected; canonical engine requires updated schema")
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                idempotency_key TEXT,
                params_json TEXT NOT NULL,
                reservation_usd REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                result_json TEXT,
                lease_token TEXT,
                lease_expires_at TEXT,
                worker_id TEXT,
                request_id TEXT,
                trace_id TEXT,
                evidence_id TEXT,
                error_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence_records (
                id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                summary TEXT NOT NULL,
                source_ref TEXT,
                integrity_status TEXT DEFAULT 'UNKNOWN',
                verification_status TEXT DEFAULT 'UNVERIFIED'
            )
            """
        )
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_idempotency ON jobs(idempotency_key) WHERE idempotency_key IS NOT NULL')
    return conn


def create_job(
    db_path: str,
    job_id: str,
    kind: str,
    params: dict[str, Any],
    idempotency_key: str | None = None,
    reservation_usd: float = 0.0,
    request_id: str | None = None,
    trace_id: str | None = None,
    worker_id: str | None = None,
) -> dict[str, Any]:
    conn = get_db(db_path)
    now = _now_iso()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if idempotency_key is not None:
            row = conn.execute(
                "SELECT * FROM jobs WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if row is not None:
                if (json.loads(row["params_json"]) != params
                        or row["kind"] != kind
                        or row["reservation_usd"] != reservation_usd):
                    raise ValueError("Idempotency key collision with different request")
                conn.commit()
                return dict(row)
        conn.execute(
            """INSERT INTO jobs (
                id, kind, state, idempotency_key, params_json, reservation_usd,
                created_at, updated_at, request_id, trace_id, worker_id
            ) VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job_id, kind, idempotency_key, json.dumps(params), reservation_usd,
             now, now, request_id, trace_id, worker_id),
        )
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
    created = get_job(db_path, job_id)
    if created is None:
        raise RuntimeError("Job not persisted")
    return created


def get_job(db_path: str, job_id: str) -> dict[str, Any] | None:
    conn = get_db(db_path)
    cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    if not row:
        return None
    res = dict(row)
    res["params"] = json.loads(res["params_json"])
    if res.get("result_json"):
        res["result"] = json.loads(res["result_json"])
    return res


def list_jobs(db_path: str) -> list[dict[str, Any]]:
    conn = get_db(db_path)
    cursor = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    jobs: list[dict[str, Any]] = []
    for row in rows:
        data = dict(row)
        data["params"] = json.loads(data["params_json"])
        jobs.append(data)
    return jobs


def update_job_state(
    db_path: str,
    job_id: str,
    state: str,
    result: dict[str, Any] | None = None,
    *,
    lease_token: str | None = None,
    lease_expires_at: str | None = None,
    worker_id: str | None = None,
    evidence_id: str | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    conn = get_db(db_path)
    now = _now_iso()
    res_json = json.dumps(result) if result else None
    error_json = json.dumps(error) if error else None
    with conn:
        cursor = conn.execute(
            """
            UPDATE jobs
            SET state = ?,
                updated_at = ?,
                result_json = ?,
                lease_token = COALESCE(?, lease_token),
                lease_expires_at = COALESCE(?, lease_expires_at),
                worker_id = COALESCE(?, worker_id),
                evidence_id = COALESCE(?, evidence_id),
                error_json = COALESCE(?, error_json)
            WHERE id = ? AND state NOT IN ('succeeded', 'failed', 'cancelled')
              AND ((state = 'queued' AND ? IN ('running', 'failed', 'cancelled'))
                OR (state = 'running' AND ? IN ('succeeded', 'failed', 'cancelled')))
            """,
            (state, now, res_json, lease_token, lease_expires_at, worker_id, evidence_id, error_json, job_id, state, state),
        )
        if cursor.rowcount != 1:
            return None
    return get_job(db_path, job_id)


def record_evidence(
    db_path: str,
    evidence_id: str,
    capability_id: str,
    kind: str,
    sha256: str,
    summary: str,
    *,
    source_ref: str | None = None,
    integrity_status: str = "UNKNOWN",
    verification_status: str = "UNVERIFIED",
) -> dict[str, Any]:
    conn = get_db(db_path)
    now = _now_iso()
    with conn:
        conn.execute(
            """
            INSERT INTO evidence_records (
                id, capability_id, kind, collected_at, sha256, summary,
                source_ref, integrity_status, verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                capability_id,
                kind,
                now,
                sha256,
                summary,
                source_ref,
                integrity_status,
                verification_status,
            ),
        )
    cursor = conn.execute("SELECT * FROM evidence_records WHERE id = ?", (evidence_id,))
    return dict(cursor.fetchone())


def list_evidence(db_path: str) -> list[dict[str, Any]]:
    conn = get_db(db_path)
    cursor = conn.execute("SELECT * FROM evidence_records ORDER BY collected_at DESC")
    return [dict(row) for row in cursor.fetchall()]
