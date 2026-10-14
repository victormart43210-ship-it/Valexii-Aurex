"""Durable SQLite job and evidence store for AUREX backend."""

import json
import os
import sqlite3
from datetime import UTC, datetime
from typing import Any

DEFAULT_DB_PATH = os.environ.get("AUREX_DB_PATH", "/tmp/aurex_jobs.db")


def get_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                idempotency_key TEXT,
                params_json TEXT NOT NULL,
                reservation_usd REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                result_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_records (
                id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                summary TEXT NOT NULL
            )
        """)
    return conn


def create_job(
    db_path: str,
    job_id: str,
    kind: str,
    params: dict[str, Any],
    idempotency_key: str | None = None,
    reservation_usd: float = 0.0,
) -> dict[str, Any]:
    conn = get_db(db_path)
    now = datetime.now(UTC).isoformat()
    if idempotency_key:
        cursor = conn.execute("SELECT * FROM jobs WHERE idempotency_key = ?", (idempotency_key,))
        row = cursor.fetchone()
        if row:
            row_params = json.loads(row["params_json"])
            if row_params != params or row["kind"] != kind:
                raise ValueError("Idempotency key collision with different parameters")
            return dict(row)

    with conn:
        conn.execute(
            """
            INSERT INTO jobs (id, kind, state, idempotency_key, params_json, reservation_usd, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, kind, "queued", idempotency_key, json.dumps(params), reservation_usd, now, now),
        )
    return get_job(db_path, job_id)  # type: ignore


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
    jobs = []
    for r in rows:
        d = dict(r)
        d["params"] = json.loads(d["params_json"])
        jobs.append(d)
    return jobs


def update_job_state(
    db_path: str,
    job_id: str,
    state: str,
    result: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    transitions = {
        "queued": {"running", "cancelled", "failed"},
        "running": {"succeeded", "failed", "cancelled"},
        "succeeded": set(), "failed": set(), "cancelled": set(),
    }
    conn = get_db(db_path)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT state FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row is None:
                return None
            if state not in transitions.get(row["state"], set()):
                raise ValueError("Invalid job state transition")
            conn.execute(
                "UPDATE jobs SET state = ?, updated_at = ?, result_json = ? WHERE id = ? AND state = ?",
                (state, datetime.now(UTC).isoformat(), json.dumps(result) if result is not None else None,
                 job_id, row["state"]),
            )
    finally:
        conn.close()
    return get_job(db_path, job_id)


def record_evidence(
    db_path: str,
    evidence_id: str,
    capability_id: str,
    kind: str,
    sha256: str,
    summary: str,
) -> dict[str, Any]:
    conn = get_db(db_path)
    now = datetime.now(UTC).isoformat()
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence_records (id, capability_id, kind, collected_at, sha256, summary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (evidence_id, capability_id, kind, now, sha256, summary),
        )
    cursor = conn.execute("SELECT * FROM evidence_records WHERE id = ?", (evidence_id,))
    return dict(cursor.fetchone())


def list_evidence(db_path: str) -> list[dict[str, Any]]:
    conn = get_db(db_path)
    cursor = conn.execute("SELECT * FROM evidence_records ORDER BY collected_at DESC")
    return [dict(r) for r in cursor.fetchall()]
