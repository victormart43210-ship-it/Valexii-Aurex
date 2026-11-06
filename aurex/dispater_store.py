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
import logging
import os
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta
from typing import Any

from aurex.dispater_intelligence import verify_receipt
from aurex.dispater_receipt import receipt_version, seal_run, verify_mac

logger = logging.getLogger("aurex.dispater")

DEFAULT_DISPATER_DB = os.environ.get("AUREX_DISPATER_DB", "/data/aurex_dispater.db" if os.path.isdir("/data") else "/tmp/aurex_dispater.db")

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

class StorageUnavailableError(RuntimeError):
    """Raised when persistent storage directory is unwriteable or missing when required."""


_EPHEMERAL_ROOTS = ("/tmp", "/var/tmp", "/dev/shm", "/run/shm")


def persistence_required() -> bool:
    """Explicit opt-in/out wins; otherwise a Railway runtime requires a durable volume."""
    explicit = os.environ.get("AUREX_DISPATER_REQUIRE_PERSISTENT")
    if explicit in ("0", "1"):
        return explicit == "1"
    return bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_ENVIRONMENT_NAME"))


def _is_ephemeral(directory: str) -> bool:
    real = os.path.realpath(directory)
    return any(real == root or real.startswith(root + os.sep) for root in _EPHEMERAL_ROOTS)


def validate_storage_mount(path: str) -> None:
    """Validate that the target storage directory exists and is writeable.

    When persistence is required, ephemeral locations (after symlink resolution) are rejected.
    """
    directory = os.path.dirname(os.path.abspath(path))
    if persistence_required() and _is_ephemeral(directory):
        raise StorageUnavailableError(
            f"Ephemeral storage path '{path}' rejected: persistent volume required by configuration"
        )
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as exc:
            raise StorageUnavailableError(f"Persistent storage directory '{directory}' is not accessible") from exc
    if not os.access(directory, os.W_OK):
        raise StorageUnavailableError(f"Persistent storage directory '{directory}' is not writeable")
    if _is_ephemeral(directory):
        logger.warning("DISPATER store is on ephemeral storage (%s); records will not survive restarts", directory)


def db_path() -> str:
    return os.environ.get("AUREX_DISPATER_DB", DEFAULT_DISPATER_DB)


_init_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    path = db_path()
    validate_storage_mount(path)
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA synchronous=FULL")
    # No process-level cache: a replaced or recreated file must always be re-validated.
    # Setup is serialised and retried because switching to WAL needs an exclusive lock.
    with _init_lock:
        for attempt in range(50):
            try:
                mode = conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
                if str(mode).lower() != "wal":
                    conn.close()
                    raise StorageUnavailableError(f"SQLite WAL mode unavailable (got '{mode}')")
                present = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE name='idx_dispater_findings_tenant'"
                ).fetchone()  # last object in _SCHEMA; DDL commits in order, so it implies the rest
                if present is None:
                    conn.executescript(_SCHEMA)
                break
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc) or attempt == 49:
                    conn.close()
                    raise
                time.sleep(0.05)
    return conn


def _verified(row: sqlite3.Row) -> dict[str, Any]:
    report: dict[str, Any] = json.loads(row["report_json"])
    if (
        not verify_receipt(report)
        or not verify_mac(report)
        or report.get("receipt_sha256") != row["receipt_sha256"]
        or report.get("tenant_id") != row["tenant_id"]
        or report.get("dataset_sha256") != row["dataset_sha256"]
        or report.get("status") != row["status"]
    ):
        raise IntegrityError("stored audit report failed integrity verification")
    version = receipt_version(report)
    if version is None:
        raise IntegrityError("unknown receipt version")
    if version == 2:
        if report.get("run_id") != row["run_id"] or report.get("created_at") != row["created_at"]:
            raise IntegrityError("receipt identity does not match stored metadata")
        if report.get("receipt_binding") != "BOUND_V2":
            raise IntegrityError("versioned receipt is missing its binding label")
        return report
    if any(key in report for key in ("run_id", "created_at", "receipt_binding")):
        raise IntegrityError("legacy receipt carries identity fields")
    # Not an upgrade: column identity stays unbound and is labeled as such.
    annotated = dict(report)
    annotated["run_id"] = row["run_id"]
    annotated["created_at"] = row["created_at"]
    annotated["receipt_binding"] = "LEGACY_METADATA_UNBOUND"
    return annotated


def save_run(tenant_id: str, report: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Persist atomically. Returns (stored report, created). Idempotent on dataset hash.

    New rows are sealed as receipt v2. An existing row is returned unchanged, including a
    legacy receipt. Replaying a dataset does not rewrite its receipt.
    """
    if report.get("tenant_id") != tenant_id:
        raise ValueError("report tenant mismatch")
    run_id = f"run-{uuid.uuid4().hex}"
    now = datetime.now(UTC).isoformat()
    report = seal_run(report, run_id=run_id, created_at=now)
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
            if conn.in_transaction:
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


_LIST_FIELDS = ("run_id", "dataset_sha256", "receipt_sha256", "status", "created_at")


def list_runs(tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """List run metadata. Every row is MAC-verified; a tampered row fails the whole read."""
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM dispater_runs WHERE tenant_id=? ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (tenant_id, max(1, min(limit, 200))),
        ).fetchall()
    listed: list[dict[str, Any]] = []
    for row in rows:
        report = _verified(row)
        listed.append({key: report[key] for key in _LIST_FIELDS})
    return listed


def finding_history(tenant_id: str, finding_id: str) -> list[dict[str, Any]]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT f.run_id, f.finding_sha256, f.severity, f.exposure_usd, r.* FROM dispater_findings f "
            "JOIN dispater_runs r ON r.run_id=f.run_id AND r.tenant_id=f.tenant_id "
            "WHERE f.tenant_id=? AND f.finding_id=? ORDER BY f.rowid",
            (tenant_id, finding_id),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        # The findings table columns are unsigned; only values from the MAC-verified report count.
        report = _verified(row)
        match = next((f for f in report.get("findings", []) if f.get("finding_id") == finding_id), None)
        if (
            match is None
            or match.get("finding_sha256") != row["finding_sha256"]
            or match.get("severity") != row["severity"]
            or str(match.get("exposure_usd")) != row["exposure_usd"]
        ):
            raise IntegrityError("finding history row does not match the verified report")
        out.append(
            {
                "run_id": row["run_id"],
                "finding_sha256": match["finding_sha256"],
                "severity": match["severity"],
                "exposure_usd": str(match["exposure_usd"]),
                "receipt_sha256": report.get("receipt_sha256"),
                "verified": True,
            }
        )
    return out


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


def checkpoint(db_path_override: str | None = None) -> None:
    """Explicitly checkpoint the SQLite WAL log to ensure full durability to disk."""
    target_path = db_path_override or db_path()
    with closing(sqlite3.connect(target_path, timeout=30)) as conn:
        conn.execute("PRAGMA wal_checkpoint(FULL)")
