"""Persisted, tenant-scoped recovery claims governed by the Evidence Integrity Kernel.

Each claim is one underlying obligation (unique per tenant + finding_id, so the same
discrepancy can never be claimed twice across runs). The whole claim, including state, history
and submitted evidence, is stored as one HMAC-signed JSON document: unsigned columns are
identifiers only and are cross-checked against the verified document on every read.

Evidence conflicts (same source record, different content digest) are never merged into a claim.
The submission is preserved in a bounded quarantine table for review and the transition is refused.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from aurex import dispater_store
from aurex.dispater_receipt import sign_report, verify_mac
from aurex.evidence_kernel import (
    ActorKind,
    EvidenceGraph,
    EvidenceRecord,
    Freshness,
    Outcome,
    QualificationError,
    RecoveryClaim,
    challenge_finding,
    digest,
    freshness_of,
)

SCHEMA = "dispater.claim.v1"
MAX_EVIDENCE_PER_CALL = 20
MAX_EVIDENCE_PER_CLAIM = 100
MAX_QUARANTINE_PER_TENANT = 500
MAX_EVIDENCE_AGE = timedelta(days=90)

_DDL = """
CREATE TABLE IF NOT EXISTS dispater_claims (
    claim_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    claim_json TEXT NOT NULL,
    UNIQUE (tenant_id, finding_id)
);
CREATE TABLE IF NOT EXISTS dispater_quarantine (
    q_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    claim_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dispater_quarantine_tenant ON dispater_quarantine (tenant_id, q_id);
"""


class ClaimNotFound(LookupError):
    """No such claim for this tenant (also used for cross-tenant ids)."""


class EvidenceConflict(RuntimeError):
    """Submitted evidence contradicts evidence already held for the same source record."""


class ClaimInputError(ValueError):
    """Malformed request content."""


def _connect() -> sqlite3.Connection:
    conn = dispater_store._connect()
    conn.executescript(_DDL)
    return conn


def _load(conn: sqlite3.Connection, tenant_id: str, claim_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM dispater_claims WHERE tenant_id=? AND claim_id=?", (tenant_id, claim_id)
    ).fetchone()
    if row is None:
        raise ClaimNotFound(claim_id)
    doc: dict[str, Any] = json.loads(row["claim_json"])
    if (
        not verify_mac(doc)
        or doc.get("schema") != SCHEMA
        or doc.get("tenant_id") != row["tenant_id"]
        or doc.get("claim_id") != row["claim_id"]
        or doc.get("finding_id") != row["finding_id"]
    ):
        raise dispater_store.IntegrityError("stored recovery claim failed integrity verification")
    return doc


def _store(conn: sqlite3.Connection, doc: dict[str, Any], *, insert: bool) -> dict[str, Any]:
    signed = sign_report(doc)
    payload = json.dumps(signed, sort_keys=True)
    if insert:
        conn.execute(
            "INSERT INTO dispater_claims VALUES (?,?,?,?)",
            (signed["claim_id"], signed["tenant_id"], signed["finding_id"], payload),
        )
    else:
        conn.execute(
            "UPDATE dispater_claims SET claim_json=? WHERE claim_id=? AND tenant_id=?",
            (payload, signed["claim_id"], signed["tenant_id"]),
        )
    return signed


def create_claim(tenant_id: str, run_id: str, finding_id: str) -> tuple[dict[str, Any], bool]:
    """Open a claim for a finding of a MAC-verified run. Idempotent per (tenant, finding)."""
    run = dispater_store.get_run(tenant_id, run_id)
    if run is None:
        raise ClaimNotFound(run_id)
    finding = next((f for f in run.get("findings", []) if f.get("finding_id") == finding_id), None)
    if finding is None:
        raise ClaimNotFound(finding_id)
    problems = challenge_finding(finding, tenant_id, set())
    if problems:
        raise QualificationError("finding failed deterministic challenge: " + "; ".join(problems))
    try:
        amount = Decimal(str(finding["exposure_usd"]))
    except (InvalidOperation, KeyError) as exc:
        raise QualificationError("finding exposure is not a valid amount") from exc
    if amount <= 0:
        raise QualificationError("finding has no positive exposure to claim")
    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = conn.execute(
                "SELECT claim_id FROM dispater_claims WHERE tenant_id=? AND finding_id=?",
                (tenant_id, finding_id),
            ).fetchone()
            if existing:
                doc = _load(conn, tenant_id, existing["claim_id"])
                conn.execute("COMMIT")
                return doc, False
            doc = {
                "schema": SCHEMA,
                "claim_id": f"clm-{uuid.uuid4().hex}",
                "tenant_id": tenant_id,
                "finding_id": finding_id,
                "run_id": run_id,
                "finding_sha256": finding["finding_sha256"],
                "amount": str(amount),
                "state": Outcome.DETECTED_EXPOSURE.value,
                "recovered_amount": "0",
                "history": [],
                "evidence": [],
                "created_at": datetime.now(UTC).isoformat(),
            }
            signed = _store(conn, doc, insert=True)
            conn.execute("COMMIT")
            return signed, True
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise


def get_claim(tenant_id: str, claim_id: str) -> dict[str, Any]:
    with closing(_connect()) as conn:
        return _load(conn, tenant_id, claim_id)


def list_claims(tenant_id: str) -> dict[str, Any]:
    with closing(_connect()) as conn:
        ids = [
            r["claim_id"]
            for r in conn.execute(
                "SELECT claim_id FROM dispater_claims WHERE tenant_id=? ORDER BY rowid LIMIT 200",
                (tenant_id,),
            )
        ]
        claims = [_load(conn, tenant_id, i) for i in ids]
    recovered = sum((Decimal(c["recovered_amount"]) for c in claims if c["state"] == Outcome.CONFIRMED_RECOVERED.value), Decimal("0"))
    return {
        "tenant_id": tenant_id,
        "count": len(claims),
        "claims": claims,
        "confirmed_recovered_usd": str(recovered),
        "note": "Only claims in CONFIRMED_RECOVERED with independent payment evidence count as recovered.",
    }


def _record(tenant_id: str, item: dict[str, Any], now: datetime) -> EvidenceRecord:
    try:
        system, rid, content = str(item["source_system"]), str(item["source_record_id"]), str(item["content_sha256"])
        event = datetime.fromisoformat(str(item["event_time"]))
    except (KeyError, ValueError) as exc:
        raise ClaimInputError("evidence needs source_system, source_record_id, content_sha256, event_time") from exc
    if not system or not rid or len(content) != 64 or any(c not in "0123456789abcdef" for c in content):
        raise ClaimInputError("evidence identifiers or content_sha256 are malformed")
    parents = tuple(f"{p['source_system']}|{p['source_record_id']}" for p in item.get("derived_from", []) if isinstance(p, dict) and "source_system" in p and "source_record_id" in p)
    return EvidenceRecord(
        evidence_id=f"{system}|{rid}",
        tenant_id=tenant_id,
        source_system=system,
        source_record_id=rid,
        content_sha256=content,
        acquired_at=now,
        event_time=event,
        parents=parents,
        transformations=tuple(str(t) for t in item.get("transformations", [])),
    )


def _quarantine(tenant_id: str, claim_id: str, reason: str, items: list[dict[str, Any]], now: datetime) -> None:
    with closing(_connect()) as conn:
        n = conn.execute("SELECT COUNT(*) FROM dispater_quarantine WHERE tenant_id=?", (tenant_id,)).fetchone()[0]
        if n >= MAX_QUARANTINE_PER_TENANT:
            return  # bounded: the transition is still refused, only the copy is dropped
        conn.execute(
            "INSERT INTO dispater_quarantine (tenant_id, claim_id, reason, payload_json, created_at) VALUES (?,?,?,?,?)",
            (tenant_id, claim_id, reason, json.dumps(items, sort_keys=True)[:20000], now.isoformat()),
        )


def list_quarantine(tenant_id: str) -> list[dict[str, Any]]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT q_id, claim_id, reason, created_at FROM dispater_quarantine WHERE tenant_id=? ORDER BY q_id LIMIT 200",
            (tenant_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def advance_claim(
    tenant_id: str,
    claim_id: str,
    target: Outcome,
    evidence: list[dict[str, Any]],
    reviewer: str,
    received_amount: str | None = None,
) -> dict[str, Any]:
    """Advance one step. Human actor only; the kernel refuses skips, reversals and weak evidence."""
    if not reviewer:
        raise QualificationError("an identified reviewer is required")
    if len(evidence) > MAX_EVIDENCE_PER_CALL:
        raise ClaimInputError("too much evidence in one call")
    now = datetime.now(UTC)
    submitted = [_record(tenant_id, e, now) for e in evidence]
    conflict_reason: str | None = None
    result: dict[str, Any] | None = None
    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")  # serialises concurrent advances and replays
        try:
            doc = _load(conn, tenant_id, claim_id)
            held = {r["evidence_id"]: r for r in doc["evidence"]}
            for rec in submitted:
                prior = held.get(rec.evidence_id)
                if prior is not None and prior["content_sha256"] != rec.content_sha256:
                    conflict_reason = f"conflicting content for {rec.evidence_id}"
                    break
            if conflict_reason is None:
                graph = EvidenceGraph(tenant_id)
                stored_records = [
                    EvidenceRecord(
                        r["evidence_id"], tenant_id, r["source_system"], r["source_record_id"], r["content_sha256"],
                        datetime.fromisoformat(r["acquired_at"]), datetime.fromisoformat(r["event_time"]),
                        tuple(r["parents"]), tuple(r["transformations"]),
                    )
                    for r in doc["evidence"]
                ]
                for rec in stored_records:
                    graph.add(rec)
                new_ids: list[str] = []
                for rec in submitted:
                    if rec.evidence_id not in held:
                        graph.add(rec)
                        stored_records.append(rec)
                        held[rec.evidence_id] = {}
                    if rec.evidence_id not in new_ids:
                        new_ids.append(rec.evidence_id)
                if len(stored_records) > MAX_EVIDENCE_PER_CLAIM:
                    raise ClaimInputError("claim evidence limit reached")
                for eid in new_ids:
                    if freshness_of(graph.get(eid), now, MAX_EVIDENCE_AGE) is not Freshness.CURRENT:
                        raise QualificationError(f"evidence {eid} is not CURRENT")
                claim = RecoveryClaim(
                    tenant_id, doc["finding_id"], Decimal(doc["amount"]), Outcome(doc["state"]),
                    [dict(h) for h in doc["history"]], Decimal(doc["recovered_amount"]),
                )
                source_ids: tuple[str, ...] = ()
                for h in doc["history"]:
                    if h["to"] == Outcome.VERIFIED_DISCREPANCY.value:
                        source_ids = tuple(h["evidence"])
                try:
                    received = Decimal(received_amount) if received_amount is not None else None
                except InvalidOperation as exc:
                    raise ClaimInputError("received_amount is not a decimal") from exc
                claim.advance(
                    target, actor=ActorKind.HUMAN, evidence_ids=tuple(new_ids), graph=graph,
                    reviewer=reviewer, received_amount=received, claim_source_ids=source_ids, now=now,
                )
                doc["state"] = claim.state.value
                doc["recovered_amount"] = str(claim.recovered_amount)
                doc["history"] = [{**h, "from": str(h["from"]), "to": str(h["to"]), "actor": str(h["actor"])} for h in claim.history]
                doc["evidence"] = [
                    {
                        "evidence_id": r.evidence_id, "source_system": r.source_system,
                        "source_record_id": r.source_record_id, "content_sha256": r.content_sha256,
                        "acquired_at": r.acquired_at.isoformat(), "event_time": (r.event_time or r.acquired_at).isoformat(),
                        "parents": list(r.parents), "transformations": list(r.transformations),
                    }
                    for r in stored_records
                ]
                doc["version"] = int(doc.get("version", 0)) + 1
                result = _store(conn, doc, insert=False)
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
    if conflict_reason is not None:
        _quarantine(tenant_id, claim_id, conflict_reason, evidence, now)
        raise EvidenceConflict(conflict_reason)
    assert result is not None
    return result


__all__ = ["ClaimInputError", "ClaimNotFound", "EvidenceConflict", "advance_claim", "create_claim",
           "digest", "get_claim", "list_claims", "list_quarantine"]
