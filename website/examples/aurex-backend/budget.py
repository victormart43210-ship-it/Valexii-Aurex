"""Dev-only SQLite budget reservation ledger. Standard library only.

Reserve -> commit/release inside a BEGIN IMMEDIATE transaction so concurrent
writers serialize and cannot overspend. Limit 0 means no spend (default).
"""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK (id = 1), limit_usd REAL NOT NULL CHECK (limit_usd >= 0));
CREATE TABLE IF NOT EXISTS reservations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  amount_usd REAL NOT NULL CHECK (amount_usd >= 0),
  state TEXT NOT NULL CHECK (state IN ('reserved','committed','released'))
);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, state TEXT NOT NULL,
  idempotency_key TEXT UNIQUE NOT NULL, reservation_id INTEGER, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY, capability_id TEXT NOT NULL, kind TEXT NOT NULL,
  collected_at TEXT NOT NULL, sha256 TEXT NOT NULL, summary TEXT NOT NULL
);
"""


def connect(path: str = ":memory:", limit_usd: float = 0.0) -> sqlite3.Connection:
    con = sqlite3.connect(path, isolation_level=None, timeout=5, check_same_thread=False)
    con.executescript(SCHEMA)
    con.execute("INSERT OR IGNORE INTO budget (id, limit_usd) VALUES (1, ?)", (max(0.0, float(limit_usd)),))
    return con


def reserve(con: sqlite3.Connection, amount_usd: float):
    if not (amount_usd > 0):
        return None, "invalid_amount"
    con.execute("BEGIN IMMEDIATE")
    try:
        (limit,) = con.execute("SELECT limit_usd FROM budget WHERE id = 1").fetchone()
        if limit <= 0:
            con.execute("ROLLBACK")
            return None, "no_spend_default"
        (used,) = con.execute(
            "SELECT COALESCE(SUM(amount_usd), 0) FROM reservations WHERE state IN ('reserved','committed')"
        ).fetchone()
        if used + amount_usd > limit + 1e-9:
            con.execute("ROLLBACK")
            return None, "budget_exceeded"
        cur = con.execute("INSERT INTO reservations (amount_usd, state) VALUES (?, 'reserved')", (amount_usd,))
        con.execute("COMMIT")
        return cur.lastrowid, "ok"
    except Exception:
        con.execute("ROLLBACK")
        raise


def commit(con: sqlite3.Connection, rid: int, actual_usd: float) -> bool:
    con.execute("BEGIN IMMEDIATE")
    row = con.execute("SELECT amount_usd, state FROM reservations WHERE id = ?", (rid,)).fetchone()
    if not row or row[1] != "reserved" or actual_usd < 0 or actual_usd > row[0]:
        con.execute("ROLLBACK")
        return False
    con.execute("UPDATE reservations SET amount_usd = ?, state = 'committed' WHERE id = ?", (actual_usd, rid))
    con.execute("COMMIT")
    return True


def release(con: sqlite3.Connection, rid: int) -> bool:
    con.execute("BEGIN IMMEDIATE")
    cur = con.execute("UPDATE reservations SET state = 'released' WHERE id = ? AND state = 'reserved'", (rid,))
    con.execute("COMMIT")
    return cur.rowcount == 1
