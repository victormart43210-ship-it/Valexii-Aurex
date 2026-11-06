"""AUREX Evidence Integrity Kernel.

One small, dependency-free module that DISPATER (and later AUREX services) use to decide
what evidence supports a claim. It deliberately has no I/O and no model calls.

Invariants (each has an adversarial test in tests/test_evidence_kernel.py):
- Independent corroboration is counted per *evidence root*, never per record: an invoice PDF,
  its OCR text and a DB row derived from it share one root.
- Only CURRENT evidence supports a claim; STALE/UNKNOWN/UNAVAILABLE/DEGRADED/CONFLICTED never do.
- Claim state moves only along allowed transitions, and only a non-model actor can verify.
- Financial execution is never granted to any actor.
- Recovered cash requires payment evidence from a root independent of the claim's own sources.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Any


def canonical_json(value: object) -> bytes:
    """Deterministic encoding for hashing/signing (sorted keys, no NaN, UTF-8)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


class Freshness(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    DEGRADED = "DEGRADED"
    CONFLICTED = "CONFLICTED"


class ClaimState(StrEnum):
    DETECTED = "DETECTED"
    SUSPECTED = "SUSPECTED"
    CORROBORATED = "CORROBORATED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    REJECTED = "REJECTED"


class ActorKind(StrEnum):
    MODEL = "MODEL"
    SYSTEM = "SYSTEM"
    HUMAN = "HUMAN"


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    tenant_id: str
    source_system: str
    source_record_id: str
    content_sha256: str
    acquired_at: datetime
    event_time: datetime | None = None
    parents: tuple[str, ...] = ()
    transformations: tuple[str, ...] = ()
    integrity_failed: bool = False
    available: bool = True
    degraded: bool = False


class EvidenceGraph:
    """Tenant-scoped evidence records with parent links."""

    def __init__(self, tenant_id: str, records: Iterable[EvidenceRecord] = ()) -> None:
        self.tenant_id = tenant_id
        self._records: dict[str, EvidenceRecord] = {}
        for r in records:
            self.add(r)

    def add(self, record: EvidenceRecord) -> None:
        if record.tenant_id != self.tenant_id:
            raise ValueError("evidence tenant mismatch")
        if record.evidence_id in self._records:
            raise ValueError("duplicate evidence id")
        self._records[record.evidence_id] = record

    def get(self, evidence_id: str) -> EvidenceRecord:
        return self._records[evidence_id]

    def roots(self, evidence_id: str) -> frozenset[tuple[str, str]]:
        """Origin (source_system, source_record_id) pairs reachable via parents.

        A parent that is missing from the graph is treated as its own unknown root, so a
        dangling reference can never make two records look independent *or* dependent by luck.
        Cycles are rejected.
        """
        out: set[tuple[str, str]] = set()
        stack = [(evidence_id, frozenset[str]())]
        while stack:
            eid, path = stack.pop()
            if eid in path:
                raise ValueError("evidence parent cycle")
            rec = self._records.get(eid)
            if rec is None:
                raise ValueError(f"unresolved evidence parent: {eid}")
            if not rec.parents:
                out.add((rec.source_system, rec.source_record_id))
                continue
            stack.extend((p, path | {eid}) for p in rec.parents)
        return frozenset(out)

    def independent_root_count(self, evidence_ids: Iterable[str]) -> int:
        """Number of mutually disjoint root sets among the given evidence."""
        groups: list[set[tuple[str, str]]] = []
        for eid in evidence_ids:
            merged = set(self.roots(eid))
            rest = []
            for g in groups:
                if g & merged:
                    merged |= g
                else:
                    rest.append(g)
            groups = [*rest, merged]
        return len(groups)


def freshness_of(
    record: EvidenceRecord,
    now: datetime,
    max_age: timedelta,
    conflicting_hashes: Iterable[str] = (),
) -> Freshness:
    """Fail-closed freshness: anything not provably current is not CURRENT."""
    if record.integrity_failed:
        return Freshness.DEGRADED
    if not record.available:
        return Freshness.UNAVAILABLE
    if any(h != record.content_sha256 for h in conflicting_hashes):
        return Freshness.CONFLICTED
    if record.degraded:
        return Freshness.DEGRADED
    ts = record.event_time or record.acquired_at
    if ts.tzinfo is None or now.tzinfo is None or ts > now + timedelta(minutes=5):
        return Freshness.UNKNOWN
    return Freshness.CURRENT if now - ts <= max_age else Freshness.STALE


_TRANSITIONS: dict[ClaimState, frozenset[ClaimState]] = {
    ClaimState.DETECTED: frozenset({ClaimState.SUSPECTED, ClaimState.REJECTED}),
    ClaimState.SUSPECTED: frozenset({ClaimState.CORROBORATED, ClaimState.DISPUTED, ClaimState.REJECTED}),
    ClaimState.CORROBORATED: frozenset({ClaimState.VERIFIED, ClaimState.DISPUTED, ClaimState.REJECTED}),
    ClaimState.VERIFIED: frozenset({ClaimState.DISPUTED}),
    ClaimState.DISPUTED: frozenset({ClaimState.SUSPECTED, ClaimState.REJECTED}),
    ClaimState.REJECTED: frozenset(),
}


class QualificationError(ValueError):
    """A claim transition was refused."""


def qualify(
    current: ClaimState,
    target: ClaimState,
    *,
    actor: ActorKind,
    graph: EvidenceGraph,
    evidence_ids: Iterable[str],
    now: datetime,
    max_age: timedelta = timedelta(days=90),
    reviewer: str | None = None,
) -> ClaimState:
    """Return ``target`` if allowed, else raise. Never silently upgrades."""
    ids = list(evidence_ids)
    if target not in _TRANSITIONS[current]:
        raise QualificationError(f"transition {current}->{target} not allowed")
    if target in (ClaimState.CORROBORATED, ClaimState.VERIFIED):
        if actor is ActorKind.MODEL:
            raise QualificationError("a model cannot corroborate or verify a claim")
        try:
            if not ids or any(freshness_of(graph.get(e), now, max_age) is not Freshness.CURRENT for e in ids):
                raise QualificationError("all supporting evidence must be CURRENT")
            if graph.independent_root_count(ids) < 2:
                raise QualificationError("at least two independent evidence roots are required")
        except (KeyError, ValueError) as exc:
            raise QualificationError("supporting evidence has unresolved provenance") from exc
    if target is ClaimState.VERIFIED and (actor is not ActorKind.HUMAN or not reviewer):
        raise QualificationError("verification requires an identified human reviewer")
    return target


class Capability(StrEnum):
    READ_EVIDENCE = "read_evidence"
    ANALYZE = "analyze"
    GENERATE_FINDING = "generate_finding"
    PROPOSE_ADJUSTMENT = "propose_adjustment"
    REQUEST_REVIEW = "request_review"
    EXPORT_REPORT = "export_report"
    EXECUTE_FINANCIAL = "execute_financial"


# Financial execution is not grantable, whatever the grant table says.
NEVER_GRANTABLE: frozenset[Capability] = frozenset({Capability.EXECUTE_FINANCIAL})

ADVISORY_DEFAULT: frozenset[Capability] = frozenset(
    {Capability.READ_EVIDENCE, Capability.ANALYZE, Capability.REQUEST_REVIEW}
)


def authorize(actor: ActorKind, granted: Iterable[Capability], required: Capability) -> bool:
    """Deny by default; models never export or propose adjustments."""
    if required in NEVER_GRANTABLE:
        return False
    if actor is ActorKind.MODEL and required in (Capability.EXPORT_REPORT, Capability.PROPOSE_ADJUSTMENT):
        return False
    return required in set(granted)


class Outcome(StrEnum):
    DETECTED_EXPOSURE = "DETECTED_EXPOSURE"
    VERIFIED_DISCREPANCY = "VERIFIED_DISCREPANCY"
    SUBMITTED_CLAIM = "SUBMITTED_CLAIM"
    APPROVED_CLAIM = "APPROVED_CLAIM"
    CONFIRMED_RECOVERED = "CONFIRMED_RECOVERED"


_ORDER = list(Outcome)


@dataclass
class RecoveryClaim:
    """WEST-style outcome chain; one claim per underlying obligation."""

    tenant_id: str
    obligation_id: str
    amount: Decimal
    state: Outcome = Outcome.DETECTED_EXPOSURE
    history: list[dict[str, Any]] = field(default_factory=list)
    recovered_amount: Decimal = Decimal("0")

    def advance(
        self,
        target: Outcome,
        *,
        actor: ActorKind,
        evidence_ids: tuple[str, ...],
        graph: EvidenceGraph,
        reviewer: str | None = None,
        received_amount: Decimal | None = None,
        claim_source_ids: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> None:
        now = now or datetime.now(UTC)
        if graph.tenant_id != self.tenant_id:
            raise QualificationError("tenant mismatch")
        if _ORDER.index(target) != _ORDER.index(self.state) + 1:
            raise QualificationError("outcome states cannot be skipped or reversed")
        if actor is ActorKind.MODEL:
            raise QualificationError("a model cannot advance a recovery claim")
        if not evidence_ids:
            raise QualificationError("each transition needs supporting evidence")
        if target is not Outcome.VERIFIED_DISCREPANCY and (actor is not ActorKind.HUMAN or not reviewer):
            raise QualificationError("an identified human reviewer is required")
        try:
            if any(freshness_of(graph.get(e), now, timedelta(days=90)) is not Freshness.CURRENT for e in evidence_ids):
                raise QualificationError("transition evidence must be CURRENT")
            if target is Outcome.VERIFIED_DISCREPANCY and graph.independent_root_count(evidence_ids) < 2:
                raise QualificationError("verified discrepancy needs two independent evidence roots")
        except (KeyError, ValueError) as exc:
            raise QualificationError("transition evidence has unresolved provenance") from exc
        if target is Outcome.CONFIRMED_RECOVERED:
            if received_amount is None or received_amount <= 0 or received_amount > self.amount:
                raise QualificationError("received amount must be positive and not exceed the claim")
            if not claim_source_ids:
                raise QualificationError("claim source evidence is required to confirm recovery")
            try:
                if any(freshness_of(graph.get(e), now, timedelta(days=90)) is not Freshness.CURRENT for e in claim_source_ids):
                    raise QualificationError("claim source evidence must be CURRENT")
                own = set().union(*(graph.roots(e) for e in claim_source_ids))
                if any(graph.roots(e) & own for e in evidence_ids):
                    raise QualificationError("payment evidence must be independent of the claim sources")
            except (KeyError, ValueError) as exc:
                raise QualificationError("claim or payment evidence has unresolved provenance") from exc
            self.recovered_amount = received_amount
        self.history.append(
            {"from": self.state, "to": target, "actor": actor, "reviewer": reviewer,
             "evidence": list(evidence_ids), "at": now.isoformat()}
        )
        self.state = target


def challenge_finding(finding: dict[str, Any], tenant_id: str, known_obligations: set[str]) -> list[str]:
    """Deterministic KAGAMI/EMET-style challenges. Empty list means no challenge raised.

    Absence of challenges is not proof; it only means these specific checks passed.
    """
    problems: list[str] = []
    if not finding.get("evidence"):
        problems.append("missing evidence")
    if finding.get("tenant_id", tenant_id) != tenant_id:
        problems.append("tenant attribution mismatch")
    ob = finding.get("obligation_id")
    if ob is not None and ob in known_obligations:
        problems.append("duplicate obligation")
    try:
        exposure = Decimal(str(finding.get("exposure_usd", "0")))
        if exposure < 0:
            problems.append("negative exposure")
        recovered = Decimal(str(finding.get("recovered_usd", "0")))
        if recovered > exposure:
            problems.append("recovery exceeds exposure")
    except ArithmeticError:
        problems.append("invalid amount")
    ts = finding.get("evidence_timestamp")
    if ts is not None:
        try:
            if datetime.fromisoformat(str(ts)).tzinfo is None:
                problems.append("timestamp without timezone")
        except ValueError:
            problems.append("invalid timestamp")
    return problems
