"""Railway staging-only SQLite longevity proof; no customer content or auth data.

The proof is two distinct SSH invocations on the same staging /data volume
separated by a Railway staging-only restart. No model calls or job execution.
"""
from __future__ import annotations

import argparse
import os
import secrets
import sqlite3
from datetime import UTC, datetime

DB = "/data/aurex.sqlite3"
TABLE = "aurex_staging_qa_markers"


def guard() -> None:
    if os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        raise RuntimeError("HOLD: staging-only QA probe")
    if os.environ.get("AUREX_DB_PATH") != DB:
        raise RuntimeError("HOLD: unexpected database path")


def check(mode: str, marker: str = "") -> dict[str, object]:
    guard()
    with sqlite3.connect(DB, timeout=5) as con:
        row = con.execute("PRAGMA quick_check(1)").fetchone()
        if row is None or row[0] != "ok":
            raise RuntimeError("SQLite quick_check failed; HOLD")
        if mode == "write":
            marker = secrets.token_hex(12)
            con.execute(
                f"CREATE TABLE IF NOT EXISTS {TABLE} (marker TEXT PRIMARY KEY, observed_at TEXT NOT NULL)"
            )
            con.execute(
                f"INSERT INTO {TABLE}(marker,observed_at) VALUES (?,?)",
                (marker, datetime.now(UTC).isoformat()),
            )
            con.commit()
            return {"result": "STAGING_MARKER_WRITTEN", "marker": marker, "authority": "NONE"}
        if mode == "verify":
            if len(marker) != 24 or any(c not in "0123456789abcdef" for c in marker):
                raise ValueError("Invalid marker: 24 lowercase hex characters required")
            try:
                row = con.execute(
                    f"SELECT observed_at FROM {TABLE} WHERE marker=?", (marker,)
                ).fetchone()
            except sqlite3.OperationalError:
                row = None
            if not row:
                raise RuntimeError("HOLD: marker absent or not durable")
            return {"result": "STAGING_MARKER_SURVIVED", "marker": marker, "authority": "NONE"}
        raise ValueError("Unknown mode")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["write", "verify"])
    p.add_argument("marker", nargs="?", default="")
    args = p.parse_args()
    try:
        print(check(args.mode, args.marker))
    except (ValueError, RuntimeError, sqlite3.Error) as ex:
        print(f"{type(ex).__name__}: HOLD")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
