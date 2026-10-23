"""CXXXII: inspect SQLite layout without creating or migrating a database.

Source-only guard; not evidence of Railway volume isolation or release approval.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote

_CANONICAL_JOBS = frozenset({
    "id", "kind", "state", "params_json", "idempotency_key",
    "reservation_usd", "created_at", "updated_at", "result_json",
    "worker_id", "lease_token", "lease_expires_at", "evidence_id",
})
_CANONICAL_EVIDENCE = frozenset({
    "id", "capability_id", "kind", "collected_at", "sha256", "summary",
    "integrity_status", "verification_status",
})
_LEGACY_JOBS = frozenset({
    "id", "kind", "state", "params", "idempotency_key", "created_at",
    "updated_at", "worker_id", "lease_token", "lease_expires_at",
})
_LEGACY_EVIDENCE = frozenset({
    "id", "job_id", "capability_id", "kind", "collected_at", "sha256",
    "summary",
})


def inspect_schema(path: str) -> dict[str, str | bool]:
    """Return bounded schema classification; never write, create, or authorize.

    A live WAL database is deliberately refused: immutable SQLite reads can
    miss uncheckpointed WAL data. Use an isolated, quiescent snapshot instead.
    """
    result: dict[str, str | bool] = {
        "schema": "UNKNOWN", "canonical_compatible": False,
        "read_only": True, "deployment_authority": "NONE", "release": "HOLD",
    }
    p = Path(path)
    if not p.is_absolute() or p.is_symlink() or not p.is_file():
        result["schema"] = "MISSING_OR_UNSAFE_PATH"
        return result
    if Path(f"{p}-wal").exists() or Path(f"{p}-shm").exists():
        result["schema"] = "LIVE_WAL_SNAPSHOT_REQUIRED"
        return result
    try:
        # immutable + mode=ro avoid creation, even of SQLite sidecars. Never
        # classify a live WAL database: it was explicitly refused above.
        uri = f"file:{quote(str(p), safe='/')}?mode=ro&immutable=1"
        with sqlite3.connect(uri, uri=True) as conn:
            conn.execute("PRAGMA query_only=ON")
            names = {str(row[0]) for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if not names.intersection({"jobs", "evidence", "evidence_records"}):
                result["schema"] = "EMPTY_OR_UNRECOGNIZED"
                return result

            def columns(table: str) -> frozenset[str]:
                return frozenset(str(row[1]) for row in conn.execute(
                    f"PRAGMA table_info({table})"
                ))

            jobs = columns("jobs")
            canonical = (_CANONICAL_JOBS <= jobs and
                         _CANONICAL_EVIDENCE <= columns("evidence_records"))
            legacy = (_LEGACY_JOBS <= jobs and
                      _LEGACY_EVIDENCE <= columns("evidence"))
            if canonical and not legacy and "params" not in jobs and "evidence" not in names:
                result["schema"] = "CANONICAL"
                result["canonical_compatible"] = True
            elif (legacy and not canonical and "params_json" not in jobs
                  and "evidence_records" not in names):
                result["schema"] = "LEGACY_MIGRATION_REQUIRED"
            elif canonical or legacy or ("params" in jobs and "params_json" in jobs):
                result["schema"] = "MIXED_MIGRATION_REQUIRED"
            else:
                result["schema"] = "INCOMPATIBLE"
    except (sqlite3.Error, OSError, ValueError):
        result["schema"] = "UNREADABLE"
    return result
