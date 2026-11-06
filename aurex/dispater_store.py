"""Durable, tenant-scoped SQLite persistence for DISPATER audit runs.

Every query is filtered by tenant_id. Runs are immutable once written; an identical
submission (same tenant + dataset SHA-256) is idempotent and returns the existing run.
Reads re-verify the report receipt hash so on-disk tampering is detected.

Migration: tables are created idempotently (CREATE TABLE IF NOT EXISTS) on first use.
Rollback: stop the service and drop `dispater_findings`, `dispater_runs`
(or delete the file named by AUREX_DISPATER_DB). No other AUREX tables are touched.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path
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

_MONITOR_SCHEMA = """
CREATE TABLE IF NOT EXISTS dispater_monitor_events (
    event_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    checkpoint_sha256 TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    prev_sha256 TEXT NOT NULL,
    entry_sha256 TEXT NOT NULL,
    UNIQUE (tenant_id, source_sha256)
);
CREATE INDEX IF NOT EXISTS idx_dispater_monitor_tenant ON dispater_monitor_events (tenant_id, created_at);
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
                conn.executescript(_MONITOR_SCHEMA)
                _migrate_monitor_chain(conn)
                break
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc) or attempt == 49:
                    conn.close()
                    raise
                time.sleep(0.05)
    return conn


def _protect_report(encoded: str) -> str:
    from aurex.dispater_at_rest import protect_text

    return protect_text(encoded)


def _verified(row: sqlite3.Row) -> dict[str, Any]:
    from aurex.dispater_at_rest import AtRestError, reveal_text

    try:
        report: dict[str, Any] = json.loads(reveal_text(row["report_json"]))
    except (AtRestError, json.JSONDecodeError) as exc:
        raise IntegrityError("stored report envelope failed") from exc
    if (
        not verify_receipt(report)
        or not verify_mac(report)
        or report.get("receipt_sha256") != row["receipt_sha256"]
        or report.get("tenant_id") != row["tenant_id"]
        or report.get("dataset_sha256") != row["dataset_sha256"]
        or report.get("status") != row["status"]
    ):
        raise IntegrityError("stored audit report failed integrity verification")
    from aurex.dispater_intelligence import receipt_authenticity

    if receipt_authenticity(report) != "MAC":
        raise IntegrityError("stored audit report is not an authenticated receipt")
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
                    _protect_report(json.dumps(report, sort_keys=True)),
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
    """Delete one tenant's runs, cascaded findings, and monitor events.

    This is a local maintenance function. It is not a customer API and it does
    not contact anyone. The returned count is the number of runs removed.
    """
    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            if older_than_days is None:
                conn.execute("DELETE FROM dispater_monitor_events WHERE tenant_id=?", (tenant_id,))
                cur = conn.execute("DELETE FROM dispater_runs WHERE tenant_id=?", (tenant_id,))
            else:
                cutoff = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
                conn.execute(
                    "DELETE FROM dispater_monitor_events WHERE tenant_id=? AND created_at<?",
                    (tenant_id, cutoff),
                )
                cur = conn.execute(
                    "DELETE FROM dispater_runs WHERE tenant_id=? AND created_at<?",
                    (tenant_id, cutoff),
                )
            removed = cur.rowcount
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
    remaining = monitor_event_count(tenant_id)
    from aurex.dispater_anchor import clear_tenant, note_head

    if remaining == 0:
        _write_monitor_head(tenant_id, "0" * 64, 0)
        clear_tenant(tenant_id)
    else:
        last = list_monitor_events(tenant_id)[-1]
        _write_monitor_head(tenant_id, str(last["entry_sha256"]), remaining)
        note_head(tenant_id, str(last["entry_sha256"]), remaining)
    return removed


def _migrate_monitor_chain(conn: sqlite3.Connection) -> None:
    """Add chain columns without rewriting historical event bodies.

    Rows written before the chain existed keep empty link fields. Verification
    fails closed for those rows instead of inventing a predecessor hash.
    """
    cols = {str(row[1]) for row in conn.execute("PRAGMA table_info(dispater_monitor_events)")}
    if not cols:
        return
    if "prev_sha256" not in cols:
        conn.execute("ALTER TABLE dispater_monitor_events ADD COLUMN prev_sha256 TEXT NOT NULL DEFAULT ''")
    if "entry_sha256" not in cols:
        conn.execute("ALTER TABLE dispater_monitor_events ADD COLUMN entry_sha256 TEXT NOT NULL DEFAULT ''")


def _monitor_head_path() -> Path:
    return Path(str(db_path()) + ".monitor-head.json")


def _write_monitor_head(tenant_id: str, head: str, count: int) -> None:
    """Record the chain head outside the event table. The MAC uses the receipt key.

    A reader who can edit only the event table cannot hide a deleted tail. A reader
    who also holds the receipt key can still rewrite both. This is not an outside witness.
    """
    from aurex.dispater_receipt import mac_mapping

    body = {"count": count, "head": head, "tenant_id": tenant_id}
    kid, mac = mac_mapping(body)
    path = _monitor_head_path()
    with _init_lock:
        current: dict[str, Any] = {}
        if path.exists():
            current = json.loads(path.read_text())
        current[tenant_id] = {**body, "kid": kid, "mac": mac}
        temporary = path.with_name(f"{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
        temporary.write_text(json.dumps(current, sort_keys=True))
        temporary.replace(path)


def _monitor_head_agrees(tenant_id: str, events: list[dict[str, Any]]) -> bool:
    from aurex.dispater_receipt import verify_mapping_mac

    path = _monitor_head_path()
    if not path.exists():
        return not events
    try:
        stored = json.loads(path.read_text()).get(tenant_id)
    except (OSError, ValueError):
        return False
    if not events:
        if not isinstance(stored, dict):
            # A missing sidecar entry cannot be told apart from a tenant that never wrote
            # an event. Deleting the rows and the entry together is not detectable here.
            return True
        body = {"count": stored.get("count"), "head": stored.get("head"), "tenant_id": tenant_id}
        if not verify_mapping_mac(body, kid=str(stored.get("kid", "")), mac=str(stored.get("mac", ""))):
            return False
        return stored.get("count") == 0 and stored.get("head") == "0" * 64
    if not isinstance(stored, dict):
        return False
    body = {"count": stored.get("count"), "head": stored.get("head"), "tenant_id": tenant_id}
    if not verify_mapping_mac(body, kid=str(stored.get("kid", "")), mac=str(stored.get("mac", ""))):
        return False
    return stored.get("head") == events[-1]["entry_sha256"] and stored.get("count") == len(events)


def _chain_digest(body: dict[str, Any]) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def save_monitor_event(
    tenant_id: str,
    *,
    source_sha256: str,
    checkpoint_sha256: str,
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Append one tenant-scoped monitoring event. A repeated source digest returns the original.

    A repeated digest with a different checkpoint is a conflict and is not rewritten.
    Each event hashes the previous event. The actor is SYSTEM.
    """
    from aurex.dispater_anchor import require_configured

    require_configured()
    event_id = f"mon-{uuid.uuid4().hex}"
    created_at = datetime.now(UTC).isoformat()
    recorded = dict(payload)
    recorded["actor"] = "SYSTEM"
    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = conn.execute(
                "SELECT * FROM dispater_monitor_events WHERE tenant_id=? AND source_sha256=?",
                (tenant_id, source_sha256),
            ).fetchone()
            if existing is not None:
                conn.execute("COMMIT")
                if existing["checkpoint_sha256"] != checkpoint_sha256:
                    raise sqlite3.IntegrityError(
                        "conflicting source evidence: digest reused for a different checkpoint"
                    )
                from aurex.dispater_anchor import anchor_agrees, note_head

                # A replay must not move the checkpoint back to an older event.
                events = list_monitor_events(tenant_id)
                if events and not anchor_agrees(tenant_id, events):
                    note_head(tenant_id, str(events[-1]["entry_sha256"]), len(events))
                return _monitor_row(existing)
            previous = conn.execute(
                "SELECT entry_sha256 FROM dispater_monitor_events WHERE tenant_id=? "
                "ORDER BY created_at DESC, rowid DESC LIMIT 1",
                (tenant_id,),
            ).fetchone()
            prev_sha256 = previous["entry_sha256"] if previous else "0" * 64
            recorded.pop("chain_auth", None)
            chain_body = {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "source_sha256": source_sha256,
                "checkpoint_sha256": checkpoint_sha256,
                "event_type": event_type,
                "payload": recorded,
                "created_at": created_at,
                "prev_sha256": prev_sha256,
                "actor": "SYSTEM",
            }
            entry_sha256 = _chain_digest(chain_body)
            from aurex.dispater_receipt import mac_mapping

            kid, mac = mac_mapping(chain_body)
            stored_payload = dict(recorded)
            stored_payload["chain_auth"] = {"alg": "HMAC-SHA256", "kid": kid, "mac": mac}
            conn.execute(
                "INSERT INTO dispater_monitor_events VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    event_id,
                    tenant_id,
                    source_sha256,
                    checkpoint_sha256,
                    event_type,
                    json.dumps(stored_payload, sort_keys=True),
                    created_at,
                    prev_sha256,
                    entry_sha256,
                ),
            )
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        count_row = conn.execute(
            "SELECT COUNT(*) AS n FROM dispater_monitor_events WHERE tenant_id=?",
            (tenant_id,),
        ).fetchone()
        count = int(count_row["n"])
        _write_monitor_head(tenant_id, entry_sha256, count)
        from aurex.dispater_anchor import note_head

        note_head(tenant_id, entry_sha256, count)
        row = conn.execute(
            "SELECT * FROM dispater_monitor_events WHERE event_id=?", (event_id,)
        ).fetchone()
    return _monitor_row(row)


def _monitor_row(row: sqlite3.Row) -> dict[str, Any]:
    payload = json.loads(row["payload_json"])
    return {
        "event_id": row["event_id"],
        "tenant_id": row["tenant_id"],
        "source_sha256": row["source_sha256"],
        "checkpoint_sha256": row["checkpoint_sha256"],
        "event_type": row["event_type"],
        "created_at": row["created_at"],
        "prev_sha256": row["prev_sha256"],
        "entry_sha256": row["entry_sha256"],
        "payload": payload,
        "actor": payload.get("actor", "SYSTEM"),
        "confirmed_recovery_usd": "0.00",
    }


def verify_monitor_chain(tenant_id: str) -> bool:
    """True when the unkeyed hash and the server MAC both match.

    The MAC shows a holder of the receipt key wrote the event. It is not a human
    signature and it does not prove the underlying records are true.
    """
    previous = "0" * 64
    for event in list_monitor_events(tenant_id):
        if event["prev_sha256"] != previous or event["actor"] != "SYSTEM":
            return False
        body = {
            "event_id": event["event_id"],
            "tenant_id": event["tenant_id"],
            "source_sha256": event["source_sha256"],
            "checkpoint_sha256": event["checkpoint_sha256"],
            "event_type": event["event_type"],
            "payload": event["payload"],
            "created_at": event["created_at"],
            "prev_sha256": event["prev_sha256"],
            "actor": "SYSTEM",
        }
        payload = dict(event["payload"])
        auth = payload.pop("chain_auth", None)
        body["payload"] = payload
        if _chain_digest(body) != event["entry_sha256"]:
            return False
        if not isinstance(auth, dict) or auth.get("alg") != "HMAC-SHA256":
            return False
        from aurex.dispater_receipt import verify_mapping_mac

        if not verify_mapping_mac(body, kid=str(auth.get("kid", "")), mac=str(auth.get("mac", ""))):
            return False
        previous = event["entry_sha256"]
    events = list_monitor_events(tenant_id)
    if not _monitor_head_agrees(tenant_id, events):
        return False
    from aurex.dispater_anchor import anchor_agrees

    return anchor_agrees(tenant_id, events)


def get_monitor_event(tenant_id: str, source_sha256: str) -> dict[str, Any] | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT * FROM dispater_monitor_events WHERE tenant_id=? AND source_sha256=?",
            (tenant_id, source_sha256),
        ).fetchone()
    return _monitor_row(row) if row else None


def list_monitor_events(tenant_id: str) -> list[dict[str, Any]]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM dispater_monitor_events WHERE tenant_id=? ORDER BY created_at, rowid",
            (tenant_id,),
        ).fetchall()
    return [_monitor_row(row) for row in rows]


def monitor_event_count(tenant_id: str) -> int:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM dispater_monitor_events WHERE tenant_id=?",
            (tenant_id,),
        ).fetchone()
    return int(row["n"]) if row else 0


def checkpoint(db_path_override: str | None = None) -> None:
    """Explicitly checkpoint the SQLite WAL log to ensure full durability to disk."""
    target_path = db_path_override or db_path()
    with closing(sqlite3.connect(target_path, timeout=30)) as conn:
        conn.execute("PRAGMA wal_checkpoint(FULL)")
