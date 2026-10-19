"""Owner-only ORCA R8 *status metadata* bridge, not an evidence verification service.

The workstation sends outbound-only status; no raw documents, file paths, prompts,
sensitive rows, or localhost tunneling. Two independent server-only bearer tokens.
Disabled by default; deployment and private-site release require separate gates.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

PUSH_PATH = "/v1/orca/r8/status"
STALE_AFTER_SECONDS = 120
MAX_BODY_BYTES = 2048
push_router = APIRouter(tags=["orca-r8-private"])
read_router = APIRouter(tags=["orca-r8-private"])


class Snapshot(BaseModel):
    """Strictly allowlisted counters only. No private evidence or document bytes."""

    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=True)

    sourceId: Literal["orca-r8"]
    runId: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    sequence: int = Field(ge=1, le=1_000_000_000)
    observedAt: datetime
    status: Literal["RUNNING", "PAUSED", "COMPLETED", "FAILED"]
    completedBatches: int = Field(ge=0, le=1_000_000)
    totalBatches: int = Field(ge=1, le=1_000_000)
    rowsRemaining: int | None = Field(default=None, ge=0, le=100_000_000)
    etaSeconds: int | None = Field(default=None, ge=0, le=31_536_000)
    checkpointAgeSeconds: int | None = Field(default=None, ge=0, le=31_536_000)


def _enabled() -> None:
    if os.getenv("AUREX_ORCA_SYNC_ENABLED") != "1":
        raise HTTPException(503, "ORCA status synchronization disabled")


def authorize_push(authorization: str | None = Header(default=None)) -> None:
    _enabled()
    expected = os.getenv("AUREX_ORCA_PUSH_TOKEN", "")
    # Never accept an empty or short credential. Never log the supplied header.
    if len(expected) < 32 or expected in (
        os.getenv("AUREX_SERVICE_TOKEN"), os.getenv("AUREX_ADMIN_TOKEN")
    ):
        raise HTTPException(503, "ORCA status writer not configured or token scopes overlap")
    supplied = authorization or ""
    if not hmac.compare_digest(supplied, "Bearer " + expected):
        raise HTTPException(401, "unauthorized")


def _db() -> sqlite3.Connection:
    path = os.getenv("AUREX_DB_PATH", "")
    # A temporary default would silently erase status after a deploy. Require an explicit DB.
    if not path.startswith("/") or path == "/tmp/aurex_jobs.db":
        raise HTTPException(503, "ORCA durable database path not configured")
    conn = sqlite3.connect(path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS orca_r8_status (
            source_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            observed_at TEXT NOT NULL,
            received_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            sha256 TEXT NOT NULL
        )"""
    )
    return conn


def _checked_observation(snapshot: Snapshot, now: datetime) -> None:
    when = snapshot.observedAt
    if when.tzinfo is None or when.utcoffset() is None:
        raise HTTPException(422, "observedAt must have timezone")
    instant = when.astimezone(UTC)
    if not now - timedelta(minutes=10) <= instant <= now + timedelta(minutes=1):
        raise HTTPException(422, "observation timestamp outside acceptance window")
    if snapshot.completedBatches > snapshot.totalBatches:
        raise HTTPException(422, "completed batches exceed total")
    if snapshot.status == "COMPLETED" and snapshot.completedBatches != snapshot.totalBatches:
        raise HTTPException(422, "completed run must have all batches")


@push_router.post(PUSH_PATH)
async def push_status(
    request: Request, _: None = Depends(authorize_push),
) -> dict[str, str]:
    # Read incrementally: a forged Content-Length cannot bypass this byte bound.
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY_BYTES:
            raise HTTPException(413, "status message too large")
    try:
        snapshot = Snapshot.model_validate_json(bytes(body))
    except (ValidationError, ValueError):
        raise HTTPException(422, "invalid status schema") from None
    now = datetime.now(UTC)
    _checked_observation(snapshot, now)

    data = snapshot.model_dump_json(exclude_none=True)
    digest = hashlib.sha256(data.encode("utf-8")).hexdigest()
    observed = snapshot.observedAt.astimezone(UTC).isoformat()
    received = now.isoformat()
    conn = _db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        old = conn.execute(
            "SELECT run_id, sequence, observed_at FROM orca_r8_status WHERE source_id = ?",
            ("orca-r8",),
        ).fetchone()
        if old is not None:
            if old["run_id"] == snapshot.runId:
                if snapshot.sequence <= old["sequence"]:
                    raise HTTPException(409, "duplicate or out-of-order sequence")
            elif observed <= old["observed_at"]:
                raise HTTPException(409, "older run cannot replace latest snapshot")
        conn.execute(
            """INSERT INTO orca_r8_status
             (source_id, run_id, sequence, observed_at, received_at, payload_json, sha256)
             VALUES (?, ?, ?, ?, ?, ?, ?)
             ON CONFLICT(source_id) DO UPDATE SET
               run_id=excluded.run_id, sequence=excluded.sequence,
               observed_at=excluded.observed_at, received_at=excluded.received_at,
               payload_json=excluded.payload_json, sha256=excluded.sha256""",
            ("orca-r8", snapshot.runId, snapshot.sequence, observed, received, data, digest),
        )
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
    # Receipt confirms server storage only, NOT independent validity of workstation claims.
    return {"result": "STORED_UNVERIFIED", "receivedAt": received, "sha256": digest}


@read_router.get(PUSH_PATH)
def read_status(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = "private, no-store"
    _enabled()
    now = datetime.now(UTC)
    conn = _db()
    try:
        row = conn.execute(
            "SELECT payload_json, observed_at, received_at, sha256 FROM orca_r8_status WHERE source_id = ?",
            ("orca-r8",),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return {
            "state": "NO_DATA", "checkedAt": now.isoformat(), "snapshot": None,
            "receivedAt": None, "sha256": None,
            "evidenceStatus": "NOT VERIFIED", "authority": "NONE",
        }
    received = datetime.fromisoformat(row["received_at"]).astimezone(UTC)
    observed = datetime.fromisoformat(row["observed_at"]).astimezone(UTC)
    receipt_age = (now - received).total_seconds()
    observation_age = (now - observed).total_seconds()
    # A delayed/backfilled status is NOT live, even if it only just arrived.
    fresh = (0 <= receipt_age <= STALE_AFTER_SECONDS
             and 0 <= observation_age <= STALE_AFTER_SECONDS)
    return {
        "state": "OBSERVED" if fresh else "STALE",
        "checkedAt": now.isoformat(), "snapshot": json.loads(row["payload_json"]),
        "receivedAt": received.isoformat(), "sha256": row["sha256"],
        "evidenceStatus": "NOT VERIFIED", "authority": "NONE",
    }
