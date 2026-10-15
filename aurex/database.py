"""Owner-scoped SQLite records. Stored observations do not grant authority."""

import hashlib
import json
import math
import os
import re
import sqlite3
import time
import uuid
from contextlib import closing
from datetime import UTC, datetime
from typing import Any, cast

DEFAULT_DB_PATH = os.environ.get("AUREX_DB_PATH", "/tmp/aurex_jobs.db")
SCHEMA_VERSION = 2
SERVICE_OWNER = "service"


def _owner(owner_id: str) -> str:
    if not isinstance(owner_id, str) or not 1 <= len(owner_id) <= 128 or "\x00" in owner_id:
        raise ValueError("Invalid owner scope")
    return owner_id


def get_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Initialize atomically; ambiguous legacy idempotency data requires operator repair.

    Existing rows belong to the legacy service, never to an inferred end user.
    No rows are removed or deduplicated by this migration.
    """
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version == SCHEMA_VERSION:
            return conn
        if version not in (0, 1):
            raise ValueError("Unsupported database schema version")
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            # Another initializer may have completed while this connection waited.
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version == SCHEMA_VERSION:
                return conn
            if version not in (0, 1):
                raise ValueError("Unsupported database schema version")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, state TEXT NOT NULL,
                    idempotency_key TEXT, params_json TEXT NOT NULL,
                    reservation_usd REAL NOT NULL DEFAULT 0.0,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, result_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_records (
                    id TEXT PRIMARY KEY, capability_id TEXT NOT NULL, kind TEXT NOT NULL,
                    collected_at TEXT NOT NULL, sha256 TEXT NOT NULL, summary TEXT NOT NULL
                )
            """)
            for table in ("jobs", "evidence_records"):
                columns = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
                if "owner_id" not in columns:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'service'")
            duplicate = conn.execute("""
                SELECT 1 FROM jobs WHERE idempotency_key IS NOT NULL
                GROUP BY owner_id, idempotency_key HAVING COUNT(*) > 1 LIMIT 1
            """).fetchone()
            if duplicate:
                raise ValueError("Legacy idempotency conflicts require explicit operator reconciliation")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jobs_owner_key ON jobs(owner_id, idempotency_key) WHERE idempotency_key IS NOT NULL")
            conn.execute("CREATE INDEX IF NOT EXISTS jobs_owner_created ON jobs(owner_id, created_at DESC, id DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS evidence_owner_created ON evidence_records(owner_id, collected_at DESC, id DESC)")
            columns = {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}
            for name, declaration in {
                "worker_id": "TEXT", "lease_until": "REAL", "fence": "INTEGER NOT NULL DEFAULT 0",
                "attempts": "INTEGER NOT NULL DEFAULT 0", "max_attempts": "INTEGER NOT NULL DEFAULT 3",
                "deadline": "REAL", "error_code": "TEXT",
            }.items():
                if name not in columns:
                    conn.execute(f"ALTER TABLE jobs ADD COLUMN {name} {declaration}")
            conn.execute("CREATE TABLE IF NOT EXISTS workers (id TEXT PRIMARY KEY, heartbeat REAL NOT NULL, model_configured INTEGER NOT NULL DEFAULT 0)")
            conn.execute("CREATE TABLE IF NOT EXISTS job_evidence_links (job_id TEXT NOT NULL REFERENCES jobs(id), evidence_id TEXT NOT NULL UNIQUE REFERENCES evidence_records(id), PRIMARY KEY(job_id, evidence_id))")
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        return conn
    except Exception:
        conn.close()
        raise


def _job(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["params"] = json.loads(result["params_json"])
    if result["result_json"] is not None:
        result["result"] = json.loads(result["result_json"])
    return result


def create_job(
    db_path: str,
    job_id: str,
    kind: str,
    params: dict[str, Any],
    idempotency_key: str | None = None,
    reservation_usd: float = 0.0,
    *,
    owner_id: str = SERVICE_OWNER,
    deadline_seconds: float = 180,
    max_attempts: int = 3,
) -> dict[str, Any]:
    if not math.isfinite(deadline_seconds) or not 1 <= deadline_seconds <= 3600 or not 1 <= max_attempts <= 5:
        raise ValueError("Invalid execution limits")
    owner_id = _owner(owner_id)
    if idempotency_key is not None and (not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 128):
        raise ValueError("Invalid idempotency key")
    if not math.isfinite(reservation_usd) or reservation_usd < 0:
        raise ValueError("Invalid reservation")
    encoded = json.dumps(params, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(encoded.encode()) > 16_384:
        raise ValueError("Job parameters too large")
    now = datetime.now(UTC).isoformat()
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        if idempotency_key is not None:
            row = conn.execute("SELECT * FROM jobs WHERE owner_id = ? AND idempotency_key = ?", (owner_id, idempotency_key)).fetchone()
            if row is not None:
                if (json.loads(row["params_json"]) != params or row["kind"] != kind or row["reservation_usd"] != reservation_usd or row["max_attempts"] != max_attempts):
                    raise ValueError("Idempotency key collision with different request")
                return _job(row)
        conn.execute("""
            INSERT INTO jobs (id, kind, state, idempotency_key, params_json, reservation_usd, created_at, updated_at, owner_id, deadline, max_attempts)
            VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_id, kind, idempotency_key, encoded, reservation_usd, now, now, owner_id, time.time() + deadline_seconds, max_attempts))
        return _job(conn.execute("SELECT * FROM jobs WHERE id = ? AND owner_id = ?", (job_id, owner_id)).fetchone())


def get_job(db_path: str, job_id: str, *, owner_id: str = SERVICE_OWNER) -> dict[str, Any] | None:
    with closing(get_db(db_path)) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ? AND owner_id = ?", (job_id, _owner(owner_id))).fetchone()
        return _job(row) if row is not None else None


def list_jobs(db_path: str, *, owner_id: str = SERVICE_OWNER, before_id: str | None = None) -> list[dict[str, Any]]:
    with closing(get_db(db_path)) as conn:
        owner_id = _owner(owner_id)
        if before_id is not None:
            anchor = conn.execute("SELECT created_at, id FROM jobs WHERE owner_id = ? AND id = ?", (owner_id, before_id)).fetchone()
            if anchor is None:
                return []
            rows = conn.execute("SELECT * FROM jobs WHERE owner_id = ? AND (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT 200", (owner_id, anchor["created_at"], anchor["id"]))
        else:
            rows = conn.execute("SELECT * FROM jobs WHERE owner_id = ? ORDER BY created_at DESC, id DESC LIMIT 200", (owner_id,))
        return [_job(row) for row in rows]


def update_job_state(
    db_path: str, job_id: str, state: str, result: dict[str, Any] | None = None,
    *, owner_id: str = SERVICE_OWNER,
) -> dict[str, Any] | None:
    transitions = {
        "queued": {"running", "cancelled", "failed"},
        "running": {"succeeded", "failed", "cancelled"},
        "succeeded": set(), "failed": set(), "cancelled": set(),
    }
    encoded = json.dumps(result, allow_nan=False) if result is not None else None
    if encoded is not None and len(encoded.encode()) > 65_536:
        raise ValueError("Job result too large")
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT state, fence FROM jobs WHERE id = ? AND owner_id = ?", (job_id, _owner(owner_id))).fetchone()
        if row is None:
            return None
        if row["fence"] and state != "cancelled":
            raise ValueError("Leased jobs require fenced worker transitions")
        if state not in transitions.get(row["state"], set()):
            raise ValueError("Invalid job state transition")
        conn.execute("UPDATE jobs SET state = ?, updated_at = ?, result_json = ? WHERE id = ? AND owner_id = ? AND state = ?", (state, datetime.now(UTC).isoformat(), encoded, job_id, owner_id, row["state"]))
        return _job(conn.execute("SELECT * FROM jobs WHERE id = ? AND owner_id = ?", (job_id, owner_id)).fetchone())


def record_evidence(
    db_path: str, evidence_id: str, capability_id: str, kind: str, sha256: str, summary: str,
    *, owner_id: str = SERVICE_OWNER,
) -> dict[str, Any]:
    owner_id = _owner(owner_id)
    if not re.fullmatch(r"[0-9a-f]{64}", sha256) or len(summary) > 500:
        raise ValueError("Invalid evidence metadata")
    now = datetime.now(UTC).isoformat()
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM evidence_records WHERE id = ?", (evidence_id,)).fetchone()
        if row is not None:
            if (row["owner_id"], row["capability_id"], row["kind"], row["sha256"], row["summary"]) != (owner_id, capability_id, kind, sha256, summary):
                raise ValueError("Evidence identifier already exists")
            return dict(row)
        conn.execute("INSERT INTO evidence_records (id, capability_id, kind, collected_at, sha256, summary, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (evidence_id, capability_id, kind, now, sha256, summary, owner_id))
        return dict(conn.execute("SELECT * FROM evidence_records WHERE id = ?", (evidence_id,)).fetchone())


def list_evidence(db_path: str, *, owner_id: str = SERVICE_OWNER) -> list[dict[str, Any]]:
    with closing(get_db(db_path)) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM evidence_records WHERE owner_id = ? ORDER BY collected_at DESC, id DESC LIMIT 200", (_owner(owner_id),))]


def _lease_args(worker_id: str, lease_seconds: float) -> None:
    _owner(worker_id)
    if not math.isfinite(lease_seconds) or not 1 <= lease_seconds <= 120:
        raise ValueError("Invalid lease")


def register_worker(db_path: str, worker_id: str, model_configured: bool = True) -> None:
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("INSERT INTO workers VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET heartbeat=excluded.heartbeat, model_configured=excluded.model_configured", (_owner(worker_id), time.time(), int(model_configured)))


def worker_status(db_path: str) -> dict[str, Any]:
    with closing(get_db(db_path)) as conn:
        count = conn.execute("SELECT COUNT(*) FROM workers WHERE heartbeat > ?", (time.time() - 15,)).fetchone()[0]
        configured = conn.execute("SELECT COUNT(*) FROM workers WHERE heartbeat > ? AND model_configured=1", (time.time() - 15,)).fetchone()[0]
        return {"active": count > 0, "activeWorkers": count, "modelConfigured": configured > 0}


def claim_job(db_path: str, worker_id: str, lease_seconds: float = 30) -> dict[str, Any] | None:
    _lease_args(worker_id, lease_seconds)
    now = time.time()
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE jobs SET state='expired', error_code='DEADLINE_EXCEEDED' WHERE kind='local_inference' AND state IN ('queued','running') AND deadline <= ?", (now,))
        conn.execute("UPDATE jobs SET state='failed', error_code='RETRY_EXHAUSTED' WHERE kind='local_inference' AND state='running' AND lease_until <= ? AND attempts >= max_attempts", (now,))
        row = conn.execute("SELECT * FROM jobs WHERE kind='local_inference' AND (state='queued' OR (state='running' AND lease_until <= ?)) AND attempts < max_attempts ORDER BY created_at, id LIMIT 1", (now,)).fetchone()
        if row is None:
            return None
        conn.execute("UPDATE jobs SET state='running', worker_id=?, lease_until=?, fence=fence+1, attempts=attempts+1, updated_at=? WHERE id=?", (worker_id, min(now + lease_seconds, row['deadline'] or now + 180), datetime.now(UTC).isoformat(), row['id']))
        return _job(conn.execute("SELECT * FROM jobs WHERE id=?", (row['id'],)).fetchone())


def _active_claim(conn: sqlite3.Connection, job_id: str, worker_id: str, fence: int) -> sqlite3.Row | None:
    now = time.time()
    return cast(sqlite3.Row | None, conn.execute("SELECT * FROM jobs WHERE id=? AND state='running' AND worker_id=? AND fence=? AND lease_until > ? AND (deadline IS NULL OR deadline > ?)", (job_id, worker_id, fence, now, now)).fetchone())


def heartbeat_job(db_path: str, job_id: str, worker_id: str, fence: int, lease_seconds: float = 30) -> bool:
    _lease_args(worker_id, lease_seconds)
    with closing(get_db(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        row = _active_claim(conn, job_id, worker_id, fence)
        if row is None:
            return False
        conn.execute("UPDATE jobs SET lease_until=? WHERE id=?", (min(time.time() + lease_seconds, row['deadline'] or time.time() + lease_seconds), job_id))
        return True


def finish_job(db_path: str, job_id: str, worker_id: str, fence: int, result: dict[str, Any]) -> bool:
    # Persist the exact advisory result plus its digest in one transaction.
    result = {**result, 'verification': 'NOT VERIFIED', 'authorityGranted': False}
    encoded = json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False, ensure_ascii=False)
    if len(encoded.encode()) > 65_536:
        raise ValueError('Job result too large')
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    with closing(get_db(db_path)) as conn, conn:
        conn.execute('BEGIN IMMEDIATE')
        row = _active_claim(conn, job_id, worker_id, fence)
        if row is None:
            return False
        evidence_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        conn.execute("INSERT INTO evidence_records(id,capability_id,kind,collected_at,sha256,summary,owner_id) VALUES (?,?,?,?,?,?,?)", (evidence_id, 'local-inference', 'model_response', now, digest, 'Advisory model response; factual correctness not independently verified.', row['owner_id']))
        conn.execute('INSERT INTO job_evidence_links VALUES (?,?)', (job_id, evidence_id))
        conn.execute("UPDATE jobs SET state='succeeded', result_json=?, lease_until=NULL, updated_at=? WHERE id=?", (encoded, now, job_id))
        return True


def fail_job(db_path: str, job_id: str, worker_id: str, fence: int, error_code: str) -> bool:
    if error_code not in {'MODEL_UNAVAILABLE', 'MODEL_TIMEOUT', 'MODEL_INVALID_RESPONSE', 'WORKER_FAILURE'}:
        raise ValueError('Invalid error code')
    with closing(get_db(db_path)) as conn, conn:
        conn.execute('BEGIN IMMEDIATE')
        row = _active_claim(conn, job_id, worker_id, fence)
        if row is None:
            return False
        state = 'failed' if row['attempts'] >= row['max_attempts'] else 'queued'
        conn.execute('UPDATE jobs SET state=?, error_code=?, lease_until=NULL, updated_at=? WHERE id=?', (state, error_code, datetime.now(UTC).isoformat(), job_id))
        return True


def job_evidence(db_path: str, job_id: str, owner_id: str = SERVICE_OWNER) -> list[dict[str, Any]]:
    with closing(get_db(db_path)) as conn:
        rows = conn.execute('SELECT e.*, j.result_json FROM evidence_records e JOIN job_evidence_links l ON e.id=l.evidence_id JOIN jobs j ON j.id=l.job_id WHERE j.id=? AND j.owner_id=? AND e.owner_id=j.owner_id', (job_id, _owner(owner_id)))
        output = []
        for row in rows:
            record = dict(row)
            raw = record.pop('result_json')
            integrity = raw is not None and hashlib.sha256(raw.encode()).hexdigest() == record['sha256']
            output.append({**record, 'integrity': 'PASS' if integrity else 'FAIL', 'verification': 'NOT VERIFIED', 'authorityGranted': False})
        return output
