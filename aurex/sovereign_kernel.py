"""Pure, fail-closed eligibility checks for the proposed VALEXII Sovereign Kernel.

This module NEVER grants execution authority. It evaluates a proposal against
caller-supplied facts; an independently authenticated authority must still
authorize any effect. No I/O, network calls, model calls, or secrets.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    ELIGIBLE_FOR_AUTHORITY_REVIEW = "ELIGIBLE_FOR_AUTHORITY_REVIEW"
    HOLD = "HOLD"


@dataclass(frozen=True, slots=True)
class ActionProposal:
    tenant_id: str
    ghost_id: str
    shell_id: str
    action: str
    evidence_roots: frozenset[str]
    independent_witness_id: str | None
    evidence_current: bool
    evidence_integrity_ok: bool
    shell_capabilities: frozenset[str]


@dataclass(frozen=True, slots=True)
class Evaluation:
    decision: Decision
    reasons: tuple[str, ...]
    authority_granted: bool = False


def evaluate_proposal(proposal: ActionProposal) -> Evaluation:
    """Check prerequisites without authorizing or performing the action."""
    reasons: list[str] = []
    if not all((proposal.tenant_id, proposal.ghost_id, proposal.shell_id, proposal.action)):
        reasons.append("MISSING_IDENTITY_OR_ACTION")
    if not proposal.evidence_current:
        reasons.append("EVIDENCE_NOT_CURRENT")
    if not proposal.evidence_integrity_ok:
        reasons.append("EVIDENCE_INTEGRITY_FAILURE")
    if len(proposal.evidence_roots) < 2 or any(not root for root in proposal.evidence_roots):
        reasons.append("INSUFFICIENT_INDEPENDENT_ROOTS")
    if not proposal.independent_witness_id or proposal.independent_witness_id == proposal.ghost_id:
        reasons.append("INDEPENDENT_WITNESS_REQUIRED")
    if proposal.action not in proposal.shell_capabilities:
        reasons.append("SHELL_CAPABILITY_DENIED")
    if proposal.action == "EXECUTE_FINANCIAL":
        reasons.append("FINANCIAL_EXECUTION_PROHIBITED")
    return Evaluation(
        decision=Decision.HOLD if reasons else Decision.ELIGIBLE_FOR_AUTHORITY_REVIEW,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True, slots=True)
class ShellTransition:
    tenant_id: str
    ghost_id: str
    from_shell: str
    to_shell: str
    old_capabilities_revoked: bool
    new_shell_attested: bool
    continuity_verified: bool
    independently_reviewed: bool


def evaluate_shell_transition(transition: ShellTransition) -> Evaluation:
    """Bian-Lian preflight: a transition is never a permission grant."""
    reasons: list[str] = []
    if not all((transition.tenant_id, transition.ghost_id, transition.from_shell, transition.to_shell)):
        reasons.append("MISSING_TRANSITION_IDENTITY")
    if transition.from_shell == transition.to_shell:
        reasons.append("NO_SHELL_CHANGE")
    if not transition.old_capabilities_revoked:
        reasons.append("OLD_CAPABILITIES_NOT_REVOKED")
    if not transition.new_shell_attested:
        reasons.append("NEW_SHELL_NOT_ATTESTED")
    if not transition.continuity_verified:
        reasons.append("CONTINUITY_NOT_VERIFIED")
    if not transition.independently_reviewed:
        reasons.append("INDEPENDENT_REVIEW_REQUIRED")
    return Evaluation(
        decision=Decision.HOLD if reasons else Decision.ELIGIBLE_FOR_AUTHORITY_REVIEW,
        reasons=tuple(reasons),
    )
