"""CXXXII source-only regression: refuse ambiguous legacy SQLite layouts."""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "aurex" / "staging_schema_preflight.py"
spec = importlib.util.spec_from_file_location("cxxxii_schema_preflight", MODULE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _db(tmp_path: Path, layout: str) -> Path:
    path = tmp_path / "audit.sqlite3"
    with sqlite3.connect(path) as conn:
        if layout in ("canonical", "mixed"):
            conn.execute("""CREATE TABLE jobs (
                id TEXT, kind TEXT, state TEXT, params_json TEXT,
                idempotency_key TEXT, reservation_usd REAL, created_at TEXT,
                updated_at TEXT, result_json TEXT, worker_id TEXT,
                lease_token TEXT, lease_expires_at TEXT, evidence_id TEXT,
                request_id TEXT, trace_id TEXT, error_json TEXT)""")
            conn.execute("""CREATE TABLE evidence_records (
                id TEXT, capability_id TEXT, kind TEXT, collected_at TEXT,
                sha256 TEXT, summary TEXT, source_ref TEXT,
                integrity_status TEXT, verification_status TEXT)""")
            if layout == "mixed":
                conn.execute("ALTER TABLE jobs ADD COLUMN params TEXT")
        elif layout == "legacy":
            conn.execute("""CREATE TABLE jobs (
                id TEXT, kind TEXT, state TEXT, params TEXT,
                idempotency_key TEXT, created_at TEXT, updated_at TEXT,
                worker_id TEXT, lease_token TEXT, lease_expires_at TEXT)""")
            conn.execute("""CREATE TABLE evidence (
                id TEXT, job_id TEXT, capability_id TEXT, kind TEXT,
                collected_at TEXT, sha256 TEXT, summary TEXT)""")
        else:
            conn.execute("CREATE TABLE unknown_table (id TEXT)")
    return path


def test_canonical_source_compatible_but_release_always_hold(tmp_path):
    p = _db(tmp_path, "canonical")
    before = p.read_bytes()
    v = module.inspect_schema(str(p))
    assert v == {"schema": "CANONICAL", "canonical_compatible": True,
                 "read_only": True, "deployment_authority": "NONE", "release": "HOLD"}
    assert p.read_bytes() == before
    assert sorted(x.name for x in tmp_path.iterdir()) == [p.name]


def test_legacy_requires_migration(tmp_path):
    p = _db(tmp_path, "legacy")
    assert module.inspect_schema(str(p))["schema"] == "LEGACY_MIGRATION_REQUIRED"
    assert module.inspect_schema(str(p))["canonical_compatible"] is False


def test_mixed_rejected(tmp_path):
    p = _db(tmp_path, "mixed")
    assert module.inspect_schema(str(p))["schema"] == "MIXED_MIGRATION_REQUIRED"


def test_missing_and_symlink_paths_fail_closed(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    assert module.inspect_schema(str(missing))["schema"] == "MISSING_OR_UNSAFE_PATH"
    assert not missing.exists()
    p = _db(tmp_path, "legacy")
    link = tmp_path / "link.sqlite3"
    link.symlink_to(p)
    assert module.inspect_schema(str(link))["schema"] == "MISSING_OR_UNSAFE_PATH"


def test_live_wal_sidecar_forces_hold(tmp_path):
    p = _db(tmp_path, "canonical")
    sidecar = Path(str(p) + "-wal")
    sidecar.write_bytes(b"uncheckpointed")
    assert module.inspect_schema(str(p))["schema"] == "LIVE_WAL_SNAPSHOT_REQUIRED"


def test_other_sqlite_and_invalid_input_rejected(tmp_path):
    p = _db(tmp_path, "unknown")
    assert module.inspect_schema(str(p))["schema"] == "EMPTY_OR_UNRECOGNIZED"
    p.write_bytes(b"not-a-database")
    assert module.inspect_schema(str(p))["schema"] == "UNREADABLE"


def test_canonical_looking_incomplete_schema_is_not_compatible(tmp_path):
    path = tmp_path / "partial.sqlite3"
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE jobs (
            id TEXT, kind TEXT, state TEXT, params_json TEXT,
            idempotency_key TEXT, reservation_usd REAL,
            created_at TEXT, updated_at TEXT, result_json TEXT,
            worker_id TEXT, lease_token TEXT, lease_expires_at TEXT,
            evidence_id TEXT)""")
        conn.execute("""CREATE TABLE evidence_records (
            id TEXT, capability_id TEXT, kind TEXT, collected_at TEXT,
            sha256 TEXT, summary TEXT, integrity_status TEXT,
            verification_status TEXT)""")
    original = path.read_bytes()
    classification = module.inspect_schema(str(path))
    assert classification["schema"] == "INCOMPATIBLE"
    assert classification["canonical_compatible"] is False
    assert classification["deployment_authority"] == "NONE"
    assert classification["release"] == "HOLD"
    assert path.read_bytes() == original
