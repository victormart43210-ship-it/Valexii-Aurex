"""Tenant-scoped SQLite storage for object-centric projections.

Tables are created beside the existing DISPATER tables in the same database
file. They do not alter ``dispater_runs`` or ``dispater_findings``.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from aurex.dispater_store import db_path, validate_storage_mount

_SCHEMA = """
CREATE TABLE IF NOT EXISTS industrial_objects (
    tenant_id TEXT NOT NULL,
    dataset_sha256 TEXT NOT NULL,
    object_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    attributes_json TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    PRIMARY KEY (tenant_id, dataset_sha256, object_id)
);
CREATE TABLE IF NOT EXISTS industrial_events (
    tenant_id TEXT NOT NULL,
    dataset_sha256 TEXT NOT NULL,
    event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_time TEXT NOT NULL,
    object_ids_json TEXT NOT NULL,
    qualifier TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    PRIMARY KEY (tenant_id, dataset_sha256, event_id)
);
CREATE TABLE IF NOT EXISTS industrial_relations (
    tenant_id TEXT NOT NULL,
    dataset_sha256 TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    qualifier TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    PRIMARY KEY (tenant_id, dataset_sha256, source_id, target_id, qualifier)
);
CREATE INDEX IF NOT EXISTS idx_industrial_objects_tenant
    ON industrial_objects (tenant_id, object_type);
"""


def connect() -> sqlite3.Connection:
    path = db_path()
    validate_storage_mount(path)
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.executescript(_SCHEMA)
    return conn


def save_projection(tenant_id: str, projection: dict[str, Any]) -> dict[str, Any]:
    dataset_sha256 = str(projection["dataset_sha256"])
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        for table in ("industrial_relations", "industrial_events", "industrial_objects"):
            conn.execute(
                f"DELETE FROM {table} WHERE tenant_id = ? AND dataset_sha256 = ?",
                (tenant_id, dataset_sha256),
            )
        conn.executemany(
            """
            INSERT INTO industrial_objects
                (tenant_id, dataset_sha256, object_id, object_type, attributes_json, source_sha256)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    tenant_id,
                    dataset_sha256,
                    item["object_id"],
                    item["object_type"],
                    json.dumps(item["attributes"], sort_keys=True, separators=(",", ":")),
                    item["source_sha256"],
                )
                for item in projection["objects"]
            ],
        )
        conn.executemany(
            """
            INSERT INTO industrial_events
                (tenant_id, dataset_sha256, event_id, event_type, event_time,
                 object_ids_json, qualifier, source_sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    tenant_id,
                    dataset_sha256,
                    item["event_id"],
                    item["event_type"],
                    item["event_time"],
                    json.dumps(item["object_ids"], separators=(",", ":")),
                    item["qualifier"],
                    item["source_sha256"],
                )
                for item in projection["events"]
            ],
        )
        conn.executemany(
            """
            INSERT INTO industrial_relations
                (tenant_id, dataset_sha256, source_id, target_id, qualifier, source_sha256)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    tenant_id,
                    dataset_sha256,
                    item["source_id"],
                    item["target_id"],
                    item["qualifier"],
                    item["source_sha256"],
                )
                for item in projection["relations"]
            ],
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
    return read_projection(tenant_id, dataset_sha256)


def read_projection(tenant_id: str, dataset_sha256: str) -> dict[str, Any]:
    conn = connect()
    try:
        objects = conn.execute(
            """
            SELECT object_id, object_type, attributes_json, source_sha256
            FROM industrial_objects
            WHERE tenant_id = ? AND dataset_sha256 = ?
            ORDER BY object_id
            """,
            (tenant_id, dataset_sha256),
        ).fetchall()
        events = conn.execute(
            """
            SELECT event_id, event_type, event_time, qualifier
            FROM industrial_events
            WHERE tenant_id = ? AND dataset_sha256 = ?
            ORDER BY event_time, event_id
            """,
            (tenant_id, dataset_sha256),
        ).fetchall()
        relations = conn.execute(
            """
            SELECT source_id, target_id, qualifier
            FROM industrial_relations
            WHERE tenant_id = ? AND dataset_sha256 = ?
            ORDER BY qualifier, source_id, target_id
            """,
            (tenant_id, dataset_sha256),
        ).fetchall()
    finally:
        conn.close()
    return {
        "tenant_id": tenant_id,
        "dataset_sha256": dataset_sha256,
        "objects": [dict(row) for row in objects],
        "events": [dict(row) for row in events],
        "relations": [dict(row) for row in relations],
        "effect": "NONE",
        "financial_authority": "NONE",
    }
