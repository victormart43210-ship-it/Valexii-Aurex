"""Immutable, domain-neutral lineage checks; structural independence is not truth.

This kernel has no trusted ingestion or external verifier. Caller-supplied labels,
including VERIFIED_OUTCOME, never establish verification or action authority.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceState(StrEnum):
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    DEGRADED = "DEGRADED"
    HIGH_CONFLICT = "HIGH_CONFLICT"
    PARTIAL = "PARTIAL"
    VERIFIED = "VERIFIED"


class Qualification(StrEnum):
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    CALCULATED = "CALCULATED"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"
    AUTHORIZED_ACTION = "AUTHORIZED_ACTION"
    VERIFIED_OUTCOME = "VERIFIED_OUTCOME"


class ImmutableModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class EvidenceNode(ImmutableModel):
    node_id: str = Field(min_length=1, max_length=256)
    tenant_id: str = Field(min_length=1, max_length=256)
    domain: str = Field(min_length=1, max_length=256)
    content_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    parent_ids: tuple[str, ...] = Field(default=(), max_length=10000)
    observed_at: datetime | None = None
    expires_at: datetime | None = None
    claimed_qualification: Qualification = Qualification.OBSERVATION


class EvidenceGraph(ImmutableModel):
    nodes: tuple[EvidenceNode, ...] = Field(max_length=10000)


class EvidenceAssessment(ImmutableModel):
    state: EvidenceState
    qualification: Qualification
    root_digests: tuple[str, ...] = ()
    structural_root_count: int = 0
    reasons: tuple[str, ...] = ()
    independently_verified: bool = False


def _aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def evaluate_evidence(
    graph: EvidenceGraph,
    node_id: str,
    *,
    tenant_id: str,
    domain: str,
    now: datetime,
    max_age: timedelta = timedelta(days=30),
    conflict: bool = False,
) -> EvidenceAssessment:
    """Walk ALL ancestors and deduplicate roots by content, never caller IDs.

    Missing/cyclic/foreign lineage invalidates the entire root count. Distinct
    content is only structural diversity: fabricated or correlated sources can
    still have different digests. VERIFIED requires an external verifier and is
    deliberately unreachable here. Every timestamp must be timezone aware.
    """
    nodes = {node.node_id: node for node in graph.nodes}
    if len(nodes) != len(graph.nodes):
        return EvidenceAssessment(state=EvidenceState.DEGRADED,
                                  qualification=Qualification.HYPOTHESIS,
                                  reasons=("duplicate_node_id",))
    colors: dict[str, int] = {}
    roots: set[str] = set()
    reasons: set[str] = set()
    stack = [(node_id, False)]
    while stack:
        current, exiting = stack.pop()
        if exiting:
            colors[current] = 2
            continue
        color = colors.get(current, 0)
        if color == 1:
            reasons.add("cyclic_lineage")
            continue
        if color == 2:
            continue
        node = nodes.get(current)
        if node is None:
            reasons.add("missing_lineage")
            continue
        if node.tenant_id != tenant_id or node.domain != domain:
            reasons.add("foreign_boundary")
            continue
        colors[current] = 1
        stack.append((current, True))
        if not node.parent_ids:
            roots.add(node.content_digest)
        for parent in sorted(set(node.parent_ids), reverse=True):
            stack.append((parent, False))
        observed, expiry = node.observed_at, node.expires_at
        if not _aware(now) or max_age <= timedelta(0):
            reasons.add("invalid_clock_policy")
        elif observed is None or not _aware(observed):
            reasons.add("unknown_timestamp")
        elif observed > now:
            reasons.add("future_timestamp")
        else:
            if now - observed >= max_age:
                reasons.add("stale_timestamp")
            if expiry is not None:
                if not _aware(expiry) or expiry < observed:
                    reasons.add("invalid_expiry")
                elif now >= expiry:
                    reasons.add("expired_timestamp")
    structural_errors = {"missing_lineage", "cyclic_lineage", "foreign_boundary"}
    if reasons & structural_errors:
        roots.clear()
        state = (EvidenceState.UNAVAILABLE if "missing_lineage" in reasons
                 else EvidenceState.DEGRADED)
        qualification = Qualification.HYPOTHESIS
    else:
        qualification = (Qualification.CALCULATED if nodes[node_id].parent_ids
                         else Qualification.OBSERVATION)
        if conflict:
            state = EvidenceState.HIGH_CONFLICT
            reasons.add("conflicting_evidence")
        elif reasons & {"invalid_clock_policy", "unknown_timestamp", "future_timestamp",
                        "invalid_expiry"}:
            state = EvidenceState.UNKNOWN
        elif reasons & {"stale_timestamp", "expired_timestamp"}:
            state = EvidenceState.STALE
        else:
            state = EvidenceState.PARTIAL
        reasons.add("no_independent_verification")
    return EvidenceAssessment(state=state, qualification=qualification,
                              root_digests=tuple(sorted(roots)),
                              structural_root_count=len(roots), reasons=tuple(sorted(reasons)))


class TrustedCallerContext(ImmutableModel):
    """Server-created authentication context; NEVER deserialize from request payloads.

    This value is a policy input, not a credential or authentication mechanism.
    The host must derive it from its existing authenticated principal and grants.
    """
    tenant_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    capabilities: frozenset[str] = frozenset()
    authenticated: bool = False
    production_hold: bool = True


class CapabilityDecision(ImmutableModel):
    permitted: bool
    reason: str


def evaluate_capability(
    capability: str, *, context: TrustedCallerContext | None,
    tenant_id: str, domain: str,
) -> CapabilityDecision:
    """Only read/analyze/export are in scope; all effect capabilities are denied."""
    if context is None or not context.authenticated:
        return CapabilityDecision(permitted=False, reason="authenticated_context_required")
    if context.tenant_id != tenant_id or context.domain != domain:
        return CapabilityDecision(permitted=False, reason="foreign_boundary")
    if capability not in {"read", "analyze", "export"}:
        return CapabilityDecision(permitted=False, reason="effect_capability_out_of_scope")
    if capability not in context.capabilities:
        return CapabilityDecision(permitted=False, reason="capability_not_granted")
    return CapabilityDecision(permitted=True, reason="bounded_read_only_capability")


class CrossDomainCandidate(ImmutableModel):
    """Content-free hypothesis requiring new evidence in its destination domain."""
    target_domain: str = Field(min_length=1)
    qualification: Literal[Qualification.HYPOTHESIS] = Qualification.HYPOTHESIS
    state: Literal[EvidenceState.UNKNOWN] = EvidenceState.UNKNOWN


def stripped_cross_domain_candidate(*, target_domain: str) -> CrossDomainCandidate:
    """Carry no tenant, source identifier, digest, content, verification or authority."""
    return CrossDomainCandidate(target_domain=target_domain)
