"""Bounded, deterministic, real SQLite roundtrip probe.

An execution observation is not independent verification.
"""
import hashlib
import sqlite3


def execute_sqlite_roundtrip(params: dict[str, object]) -> dict[str, object]:
    if params != {"probe": "sqlite_roundtrip_v1"}:
        raise ValueError("Only sqlite_roundtrip_v1 with exact parameters is allowed")
    payload = b"aurex-offline-roundtrip-v1"
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE probe (id INTEGER PRIMARY KEY, payload BLOB NOT NULL)")
        conn.execute("INSERT INTO probe (id, payload) VALUES (?, ?)", (1, payload))
        conn.commit()
        row = conn.execute("SELECT payload FROM probe WHERE id = ?", (1,)).fetchone()
        if row is None or row[0] != payload:
            raise RuntimeError("SQLite roundtrip mismatch")
        return {
            "probe": "sqlite_roundtrip_v1",
            "executed": True,
            "passed": True,
            "sha256": hashlib.sha256(row[0]).hexdigest(),
            "verification": "NOT VERIFIED",
        }
    finally:
        conn.close()
