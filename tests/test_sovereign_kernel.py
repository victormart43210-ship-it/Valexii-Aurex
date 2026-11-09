"""Regression contracts for the non-authoritative Sovereign Kernel preflight."""
from dataclasses import replace

from aurex.sovereign_kernel import (
    ActionProposal,
    Decision,
    ShellTransition,
    evaluate_proposal,
    evaluate_shell_transition,
)


def proposal() -> ActionProposal:
    return ActionProposal(
        tenant_id="synthetic-tenant",
        ghost_id="ghost-1",
        shell_id="shell-a",
        action="READ_SYNTHETIC",
        evidence_roots=frozenset({"source-a", "source-b"}),
        independent_witness_id="reviewer-2",
        evidence_current=True,
        evidence_integrity_ok=True,
        shell_capabilities=frozenset({"READ_SYNTHETIC"}),
    )


def test_valid_proposal_only_eligible_not_authorized() -> None:
    result = evaluate_proposal(proposal())
    assert result.decision == Decision.ELIGIBLE_FOR_AUTHORITY_REVIEW
    assert result.authority_granted is False


def test_stale_evidence_holds() -> None:
    assert evaluate_proposal(replace(proposal(), evidence_current=False)).decision == Decision.HOLD


def test_tampered_evidence_holds() -> None:
    assert evaluate_proposal(replace(proposal(), evidence_integrity_ok=False)).decision == Decision.HOLD


def test_missing_independent_root_holds() -> None:
    assert evaluate_proposal(replace(proposal(), evidence_roots=frozenset({"source-a"}))).decision == Decision.HOLD


def test_self_witness_holds() -> None:
    assert evaluate_proposal(replace(proposal(), independent_witness_id="ghost-1")).decision == Decision.HOLD


def test_missing_shell_capability_holds() -> None:
    assert evaluate_proposal(replace(proposal(), shell_capabilities=frozenset())).decision == Decision.HOLD


def test_financial_execution_always_holds() -> None:
    result = evaluate_proposal(replace(proposal(), action="EXECUTE_FINANCIAL", shell_capabilities=frozenset({"EXECUTE_FINANCIAL"})))
    assert result.decision == Decision.HOLD


def transition() -> ShellTransition:
    return ShellTransition(
        tenant_id="synthetic-tenant",
        ghost_id="ghost-1",
        from_shell="shell-a",
        to_shell="shell-b",
        old_capabilities_revoked=True,
        new_shell_attested=True,
        continuity_verified=True,
        independently_reviewed=True,
    )


def test_transition_requires_old_permissions_revoked() -> None:
    assert evaluate_shell_transition(replace(transition(), old_capabilities_revoked=False)).decision == Decision.HOLD


def test_transition_requires_independent_review() -> None:
    assert evaluate_shell_transition(replace(transition(), independently_reviewed=False)).decision == Decision.HOLD


def test_transition_never_grants_authority() -> None:
    result = evaluate_shell_transition(transition())
    assert result.decision == Decision.ELIGIBLE_FOR_AUTHORITY_REVIEW
    assert result.authority_granted is False
