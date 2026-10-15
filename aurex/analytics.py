"""Minimal event counts, never identity tracking or security evidence.

Routes must authenticate their callers before invoking these storage helpers.
No helper accepts prompts, user IDs, arbitrary properties, or raw user agents.
"""

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta

from aurex.database import get_db

EVENTS = frozenset({
    "page_view", "navigation", "job_submitted", "job_completed", "job_failed", "job_cancelled",
})
ROUTES = frozenset({
    "/", "/aurex", "/bcxmet", "/xaeli", "/system", "/research", "/about", "/contact",
    "/privacy", "/terms",
})
DEVICES = frozenset({"unknown", "mobile", "tablet", "desktop"})


def _schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id TEXT PRIMARY KEY, event TEXT NOT NULL, route TEXT NOT NULL,
            device TEXT NOT NULL, created_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS analytics_created ON analytics_events(created_at)")


def record_event(db_path: str, event: str, route: str = "/", device: str = "unknown") -> str:
    """Store one bounded observation. Duplicate calls count as separate observations."""
    if not isinstance(event, str) or event not in EVENTS:
        raise ValueError("Unsupported analytics event")
    if not isinstance(device, str) or device not in DEVICES:
        raise ValueError("Unsupported device category")
    if not isinstance(route, str) or len(route) > 2048 or any(ord(c) < 32 for c in route):
        raise ValueError("Unsupported analytics route")
    # Strip query/fragment before persistence; never accept arbitrary URL/path dimensions.
    safe_route = route.split("?", 1)[0].split("#", 1)[0]
    if safe_route not in ROUTES:
        raise ValueError("Unsupported analytics route")
    event_id = str(uuid.uuid4())
    with closing(get_db(db_path)) as conn, conn:
        _schema(conn)
        conn.execute(
            "INSERT INTO analytics_events VALUES (?, ?, ?, ?, ?)",
            (event_id, event, safe_route, device, datetime.now(UTC).isoformat()),
        )
    return event_id


def summary(db_path: str) -> dict[str, int]:
    """Return counts actually stored, not estimates of visitors, sessions, or efficacy."""
    with closing(get_db(db_path)) as conn, conn:
        _schema(conn)
        rows = conn.execute("SELECT event, COUNT(*) FROM analytics_events GROUP BY event")
        return {str(row[0]): int(row[1]) for row in rows}


def retention(db_path: str, days: int = 30) -> int:
    """Explicitly remove only analytics older than 1–365 days; return removed count."""
    if type(days) is not int or not 1 <= days <= 365:
        raise ValueError("Analytics retention must be 1–365 whole days")
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    with closing(get_db(db_path)) as conn, conn:
        _schema(conn)
        return conn.execute("DELETE FROM analytics_events WHERE created_at < ?", (cutoff,)).rowcount
