"""Atomic SQLite claim primitive for offline jobs.

This module does not grant verification or release authority.
"""
import sqlite3
from datetime import UTC, datetime
from typing import Any

from aurex.database import get_db, get_job


def claim_queued_job(db_path: str, worker_id: str) -> dict[str, Any] | None:
    """Serialize claims across processes and transition one queued job."""
    if not worker_id.strip():
        raise ValueError("worker_id required")
    conn = get_db(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT id FROM jobs WHERE state = 'queued' ORDER BY created_at, id LIMIT 1"
        ).fetchone()
        if row is None:
            conn.commit()
            return None
        job_id = str(row["id"])
        changed = conn.execute(
            "UPDATE jobs SET state = 'running', updated_at = ? "
            "WHERE id = ? AND state = 'queued'",
            (datetime.now(UTC).isoformat(), job_id),
        ).rowcount
        if changed != 1:
            raise RuntimeError("Queued job changed during claim")
        conn.commit()
        return get_job(db_path, job_id)
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
