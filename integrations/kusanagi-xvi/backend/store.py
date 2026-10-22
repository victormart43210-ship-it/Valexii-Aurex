"""Minimal deterministic SQLite job/evidence store; never self-verifies authority."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

LEASE_S = 60
HEARTBEAT_S = 90


def iso() -> str:
    return datetime.now(UTC).isoformat()


def path_from_env() -> str:
    return os.getenv("AUREX_DB_PATH", str(Path(__file__).parent.parent / ".runtime" / "aurex.sqlite3"))


def initialize(path: str) -> None:
    if path == ":memory:":
        raise ValueError("Durable SQLite is mandatory; :memory: is forbidden")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not p.exists():
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    with connect(path) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, state TEXT NOT NULL,
          params TEXT NOT NULL, idempotency_key TEXT UNIQUE NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          worker_id TEXT, lease_token TEXT, lease_expires_at TEXT,
          lease_generation INTEGER NOT NULL DEFAULT 0, evidence_id TEXT,
          result_json TEXT, reservation_usd REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS evidence (
          id TEXT PRIMARY KEY, job_id TEXT UNIQUE NOT NULL REFERENCES jobs(id),
          capability_id TEXT NOT NULL, kind TEXT NOT NULL, collected_at TEXT NOT NULL,
          sha256 TEXT NOT NULL, summary TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS workers (
          worker_id TEXT PRIMARY KEY, last_seen TEXT NOT NULL
        );
        """)


@contextmanager
def connect(path: str) -> Iterator[sqlite3.Connection]:
    c = sqlite3.connect(path, isolation_level=None, timeout=5)
    c.row_factory = sqlite3.Row
    try:
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=5000")
        c.execute("PRAGMA journal_mode=WAL")
        yield c
    finally:
        c.close()


def row_job(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in ("id", "kind", "state", "created_at", "updated_at", "reservation_usd")}


def public_job(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"], "kind": row["kind"], "state": row["state"],
        "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        "reservationUsd": row["reservation_usd"],
    }


def list_jobs(path: str) -> list[dict[str, Any]]:
    with connect(path) as c:
        rows = c.execute("SELECT * FROM jobs ORDER BY created_at DESC,id DESC LIMIT 200").fetchall()
        return [public_job(r) for r in rows]


def get_job(path: str, job_id: str) -> dict[str, Any] | None:
    with connect(path) as c:
        r = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return public_job(r) if r else None


def create_job(path: str, kind: str, params: dict[str, Any], key: str) -> dict[str, Any]:
    if kind != "regression_scan" or params != {"probe": "sqlite_roundtrip_v1"}:
        raise ValueError("Unsupported job kind/params")
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            existing = c.execute("SELECT * FROM jobs WHERE idempotency_key=?", (key,)).fetchone()
            if existing:
                if existing["kind"] != kind or json.loads(existing["params"]) != params:
                    raise ValueError("Idempotency key reused for a different request")
                c.commit()
                return public_job(existing)
            job_id, now = uuid4().hex, iso()
            c.execute("""INSERT INTO jobs (id,kind,state,params,idempotency_key,created_at,updated_at)
                         VALUES (?,?, 'queued', ?,?,?,?)""", (job_id, kind, json.dumps(params, sort_keys=True), key, now, now))
            r = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            c.commit()
            return public_job(r)
        except BaseException:
            c.rollback()
            raise


def heartbeat(path: str, worker_id: str) -> None:
    with connect(path) as c:
        c.execute("INSERT INTO workers(worker_id,last_seen) VALUES(?,?) ON CONFLICT(worker_id) DO UPDATE SET last_seen=excluded.last_seen", (worker_id, iso()))


def worker_recent(path: str) -> bool:
    with connect(path) as c:
        since = (datetime.now(UTC) - timedelta(seconds=HEARTBEAT_S)).isoformat()
        return c.execute("SELECT 1 FROM workers WHERE last_seen>=? LIMIT 1", (since,)).fetchone() is not None


def claim(path: str, worker_id: str) -> dict[str, Any] | None:
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            now = iso()
            r = c.execute("SELECT * FROM jobs WHERE state='queued' OR (state='running' AND lease_expires_at<?) ORDER BY created_at LIMIT 1", (now,)).fetchone()
            if not r:
                c.commit()
                return None
            token = secrets.token_hex(24)
            expires = (datetime.now(UTC) + timedelta(seconds=LEASE_S)).isoformat()
            c.execute("""UPDATE jobs SET state='running',updated_at=?,worker_id=?,lease_token=?,
                         lease_expires_at=?,lease_generation=lease_generation+1 WHERE id=?""", (now,worker_id,token,expires,r["id"]))
            out = c.execute("SELECT * FROM jobs WHERE id=?", (r["id"],)).fetchone()
            c.commit()
            return dict(out)
        except BaseException:
            c.rollback()
            raise


def finalize(path: str, claimed: dict[str, Any], worker_id: str) -> dict[str, Any]:
    # Only a bounded, literal SQLite round-trip; no shell, URL, model or API calls.
    if claimed["kind"] != "regression_scan" or json.loads(claimed["params"]) != {"probe": "sqlite_roundtrip_v1"}:
        raise ValueError("Unsupported worker task")
    payload = b"aurex-offline-roundtrip-v1"
    with closing(sqlite3.connect(":memory:")) as tmp:
        tmp.execute("CREATE TABLE probe(v BLOB NOT NULL)")
        tmp.execute("INSERT INTO probe(v) VALUES (?)", (payload,))
        echoed = tmp.execute("SELECT v FROM probe").fetchone()[0]
        if echoed != payload:
            raise RuntimeError("Roundtrip mismatch")
    digest, evidence_id = hashlib.sha256(echoed).hexdigest(), uuid4().hex
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            now = iso()
            live = c.execute("SELECT * FROM jobs WHERE id=?", (claimed["id"],)).fetchone()
            if (not live or live["state"] != "running" or live["worker_id"] != worker_id
               or live["lease_token"] != claimed["lease_token"] or live["lease_generation"] != claimed["lease_generation"]
               or not live["lease_expires_at"] or live["lease_expires_at"] <= now):
                raise ValueError("Lease expired, revoked or superseded")
            c.execute("""INSERT INTO evidence(id,job_id,capability_id,kind,collected_at,sha256,summary)
                         VALUES (?,?, 'regression_scan','offline_probe',?,?,?)""",
                      (evidence_id, claimed["id"], now, digest, "SQLite round-trip observed; independently NOT VERIFIED"))
            c.execute("""UPDATE jobs SET state='succeeded',updated_at=?,lease_token=NULL,lease_expires_at=NULL,
                         evidence_id=?,result_json=? WHERE id=?""",
                      (now,evidence_id,json.dumps({"sha256":digest,"independentVerification":"NOT VERIFIED"}),claimed["id"]))
            c.commit()
        except BaseException:
            c.rollback()
            raise
    out = get_job(path, claimed["id"])
    assert out is not None
    return out



def fail_claim(path: str, claimed: dict[str, Any], worker_id: str) -> dict[str, Any] | None:
    """Atomically fail only a still-owned lease and release its token.

    A cancellation, expiry, or a newer lease generation must not be overwritten.
    No evidence is inserted and no model/financial authority is asserted.
    """
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            live = c.execute(
                "SELECT state,worker_id,lease_token,lease_generation,lease_expires_at "
                "FROM jobs WHERE id=?", (claimed["id"],),
            ).fetchone()
            now = iso()
            if (
                live is None
                or live["state"] != "running"
                or live["worker_id"] != worker_id
                or live["lease_token"] != claimed["lease_token"]
                or live["lease_generation"] != claimed["lease_generation"]
                or not live["lease_expires_at"]
                or live["lease_expires_at"] <= now
            ):
                c.commit()
                return None
            c.execute(
                """UPDATE jobs SET state='failed', updated_at=?,
                   worker_id=NULL, lease_token=NULL, lease_expires_at=NULL,
                   lease_generation=lease_generation+1, evidence_id=NULL,
                   result_json=NULL WHERE id=?""",
                (now, claimed["id"]),
            )
            c.commit()
        except BaseException:
            c.rollback()
            raise
    return get_job(path, claimed["id"])


def cancel(path: str, job_id: str) -> dict[str, Any] | None:
    with connect(path) as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            r=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if not r or r["state"] not in ("queued","running"):
                c.commit(); return None
            c.execute("""UPDATE jobs SET state='cancelled',updated_at=?,lease_generation=lease_generation+1,
                         lease_token=NULL,lease_expires_at=NULL WHERE id=?""",(iso(),job_id))
            c.commit()
        except BaseException:
            c.rollback(); raise
    return get_job(path,job_id)


def evidence(path: str) -> list[dict[str, Any]]:
    with connect(path) as c:
        rows = c.execute("SELECT * FROM evidence ORDER BY collected_at DESC LIMIT 200").fetchall()
        return [{"id": r["id"],"capabilityId":r["capability_id"],"kind":r["kind"],
                 "collectedAt":r["collected_at"],"sha256":r["sha256"],"summary":r["summary"]}
                for r in rows]


def reserve_llm_call(path: str, now: datetime | None = None) -> bool:
    """Best-effort bound (not a guaranteed dollar billing cap): 4/min, 20/day.

    Count reservations even if a provider request fails: never retry or refund.
    """
    timestamp=now or datetime.now(UTC)
    minute=timestamp.strftime('%Y-%m-%dT%H:%M')
    day=timestamp.strftime('%Y-%m-%d')
    with connect(path) as c:
        c.execute('BEGIN IMMEDIATE')
        try:
            c.execute('CREATE TABLE IF NOT EXISTS llm_quotas (period TEXT PRIMARY KEY, used INTEGER NOT NULL)')
            for key,limit in (('minute:'+minute,4),('day:'+day,20)):
                seen=c.execute('SELECT used FROM llm_quotas WHERE period=?',(key,)).fetchone()
                if seen and seen['used']>=limit:
                    c.commit();return False
            for key in ('minute:'+minute,'day:'+day):
                c.execute('INSERT INTO llm_quotas(period,used) VALUES(?,1) ON CONFLICT(period) DO UPDATE SET used=used+1',(key,))
            cutoff=(timestamp-timedelta(days=2)).strftime('%Y-%m-%d')
            c.execute("DELETE FROM llm_quotas WHERE (period LIKE 'day:%' AND period < ?) OR (period LIKE 'minute:%' AND period < ?)",('day:'+cutoff,'minute:'+cutoff))
            c.commit();return True
        except BaseException:
            c.rollback();raise
