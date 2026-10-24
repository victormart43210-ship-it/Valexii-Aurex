"""Fail-closed, dependency-free policy boundary for synthetic integration pilots.

This module never grants authority. It only evaluates whether a request may
proceed to the existing AUREX authority gate.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PilotDecision:
    permitted_for_review: bool
    reason: str
    authority: str = "NONE"


def review_synthetic_pilot(
    *,
    synthetic: bool,
    explicit_operator_approval: bool,
    policy_response: object | None,
) -> PilotDecision:
    """Interpret an external OPA decision without granting execution authority.

    OPA responses are untrusted. Only the exact shape
    {"result": {"allow": true}} is accepted as a policy *review* pass.
    Missing, malformed, or unavailable policy responses fail closed.
    """
    if not synthetic:
        return PilotDecision(False, "non_synthetic_input")
    if not explicit_operator_approval:
        return PilotDecision(False, "operator_approval_missing")
    if not isinstance(policy_response, dict):
        return PilotDecision(False, "policy_unavailable")
    result = policy_response.get("result")
    if not isinstance(result, dict) or result.get("allow") is not True:
        return PilotDecision(False, "policy_denied_or_invalid")
    return PilotDecision(True, "policy_review_pass_authority_still_required")
