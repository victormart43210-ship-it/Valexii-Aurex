"""Explicit operator-controlled recovery for interrupted AUREX workflow jobs.

Fail-closed: only jobs still RUNNING and older than the cutoff can transition to
FAILED_INTERRUPTED. Never retry automatically; never grant model authority.
Use only after confirming no active worker is processing the database.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path


def recover_interrupted_jobs(db_path: str | Path, *, older_than_seconds: float,
                             operator_confirmed_no_active_workers: bool = False,
                             now: float | None = None) -> list[str]:
    if operator_confirmed_no_active_workers is not True:
        raise PermissionError('operator must confirm all workers stopped')
    if not isinstance(older_than_seconds, (int, float)) or not 60 <= older_than_seconds <= 86400 * 30:
        raise ValueError('recovery age must be between 60 seconds and 30 days')
    moment = time.time() if now is None else now
    if not isinstance(moment, (int, float)) or not 0 < moment < float('inf'):
        raise ValueError('invalid recovery time')
    path=Path(db_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with sqlite3.connect(str(path), timeout=5) as conn:
        conn.execute('BEGIN IMMEDIATE')
        rows=conn.execute("SELECT id FROM jobs WHERE state='RUNNING' AND updated_at <= ? ORDER BY id", (moment-older_than_seconds,)).fetchall()
        recovered=[]
        for (job_id,) in rows:
            changed=conn.execute("UPDATE jobs SET state='FAILED_INTERRUPTED', updated_at=? WHERE id=? AND state='RUNNING' AND updated_at <= ?",(moment,job_id,moment-older_than_seconds)).rowcount
            if changed == 1:
                conn.execute('INSERT INTO events (job_id,action,data_json,at) VALUES (?,?,?,?)',(job_id,'FAILED_INTERRUPTED','{"reason":"operator_confirmed_interruption"}',moment))
                recovered.append(job_id)
        return recovered
