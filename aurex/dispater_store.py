"""Durable, tenant-scoped SQLite persistence for DISPATER audit runs.

Every query is filtered by tenant_id. Runs are immutable once written; an identical
submission (same tenant + dataset SHA-256) is idempotent and returns the existing run.
Reads re-verify the report receipt hash so on-disk tampering is detected.

Migration: tables are created idempotently (CREATE TABLE IF NOT EXISTS) on first use.
Rollback: stop the service and drop `dispater_findings`, `dispater_runs`
(or delete the file named by AUREX_DISPATER_DB). No other AUREX tables are touched.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta
from typing import Any

from aurex.dispater_intelligence import verify_receipt

DEFAULT_DISPATER_DB = "/tmp/aurex_dispater.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS dispater_runs (
    run_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    dataset_sha256 TEXT NOT NULL,
    receipt_sha256 TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    report_json TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    UNIQUE (tenant_id, dataset_sha256)
);
CREATE INDEX IF NOT EXISTS idx_dispater_runs_tenant ON dispater_runs (tenant_id, created_at);
CREATE TABLE IF NOT EXISTS dispater_findings (
    run_id TEXT NOT NULL REFERENCES dispater_runs (run_id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    finding_sha256 TEXT NOT NULL,
    code TEXT NOT NULL,
    severity TEXT NOT NULL,
    exposure_usd TEXT NOT NULL,
    PRIMARY KEY (run_id, finding_id)
);
CREATE INDEX IF NOT EXISTS idx_dispater_findings_tenant ON dispater_findings (tenant_id, finding_id);
"""


class IntegrityError(RuntimeError):
    """A stored report no longer matches its receipt hash."""


def db_path() -> str:
    return os.environ.get("AUREX_DISPATER_DB", DEFAULT_DISPATER_DB)


_init_lock = threading.Lock()
_initialized: set[str] = set()


def _connect() -> sqlite3.Connection:
    path = db_path()
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    if path not in _initialized:
        with _init_lock:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(_SCHEMA)
            _initialized.add(path)
    return conn


def _verified(row: sqlite3.Row) -> dict[str, Any]:
    report: dict[str, Any] = json.loads(row["report_json"])
    if (
        not verify_receipt(report)
        or report.get("receipt_sha256") != row["receipt_sha256"]
        or report.get("tenant_id") != row["tenant_id"]
    ):
        raise IntegrityError("stored audit report failed integrity verification")
    report["run_id"] = row["run_id"]
    report["created_at"] = row["created_at"]
    return report


def save_run(tenant_id: str, report: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Persist atomically. Returns (stored report, created). Idempotent on dataset hash."""
    if report.get("tenant_id") != tenant_id:
        raise ValueError("report tenant mismatch")
    run_id = f"run-{uuid.uuid4().hex}"
    now = datetime.now(UTC).isoformat()
    refs: list[dict[str, str]] = []
    for f in report.get("findings", []):
        for ev in f.get("evidence", []):
            ref = {"kind": ev["kind"], "record_sha256": ev["record_sha256"]}
            if ref not in refs:
                refs.append(ref)
    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = conn.execute(
                "SELECT * FROM dispater_runs WHERE tenant_id=? AND dataset_sha256=?",
                (tenant_id, report["dataset_sha256"]),
            ).fetchone()
            if existing:
                conn.execute("COMMIT")
                return _verified(existing), False
            conn.execute(
                "INSERT INTO dispater_runs VALUES (?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    tenant_id,
                    report["dataset_sha256"],
                    report["receipt_sha256"],
                    report["status"],
                    now,
                    json.dumps(report, sort_keys=True),
                    json.dumps(refs, sort_keys=True),
                ),
            )
            conn.executemany(
                "INSERT INTO dispater_findings VALUES (?,?,?,?,?,?,?)",
                [
                    (run_id, tenant_id, f["finding_id"], f["finding_sha256"], f["code"], f["severity"], f["exposure_usd"])
                    for f in report.get("findings", [])
                ],
            )
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        row = conn.execute("SELECT * FROM dispater_runs WHERE run_id=?", (run_id,)).fetchone()
        return _verified(row), True


def latest_run(tenant_id: str) -> dict[str, Any] | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT * FROM dispater_runs WHERE tenant_id=? ORDER BY created_at DESC, rowid DESC LIMIT 1",
            (tenant_id,),
        ).fetchone()
        return _verified(row) if row else None


def get_run(tenant_id: str, run_id: str) -> dict[str, Any] | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT * FROM dispater_runs WHERE tenant_id=? AND run_id=?", (tenant_id, run_id)
        ).fetchone()
        return _verified(row) if row else None


def list_runs(tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT run_id, dataset_sha256, receipt_sha256, status, created_at FROM dispater_runs "
            "WHERE tenant_id=? ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (tenant_id, max(1, min(limit, 200))),
        ).fetchall()
        return [dict(r) for r in rows]


def finding_history(tenant_id: str, finding_id: str) -> list[dict[str, Any]]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT run_id, finding_sha256, severity, exposure_usd FROM dispater_findings "
            "WHERE tenant_id=? AND finding_id=? ORDER BY rowid",
            (tenant_id, finding_id),
        ).fetchall()
        return [dict(r) for r in rows]


def purge_tenant(tenant_id: str, older_than_days: int | None = None) -> int:
    """Explicit retention/purge. Deletes a single tenant's runs (and findings by cascade)."""
    with closing(_connect()) as conn:
        if older_than_days is None:
            cur = conn.execute("DELETE FROM dispater_runs WHERE tenant_id=?", (tenant_id,))
        else:
            cutoff = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
            cur = conn.execute(
                "DELETE FROM dispater_runs WHERE tenant_id=? AND created_at<?", (tenant_id, cutoff)
            )
        return cur.rowcount
