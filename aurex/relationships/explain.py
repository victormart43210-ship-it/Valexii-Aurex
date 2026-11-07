"""Restate one stored DISPATER finding without adding authority.

Observed record hashes, the calculated or suspected amount, and confirmed
recovery stay in separate fields. Confirmed recovery from this path is 0.00.
"""

from __future__ import annotations

from typing import Any

from aurex.evidence_classes import evidence_class_for_claim
from aurex.relationships.contracts import CLAIM_BY_QUALIFICATION, EXPLANATION_VERSION


def explain_finding(finding: dict[str, Any]) -> dict[str, Any]:
    qualification = finding.get("qualification")
    claim = CLAIM_BY_QUALIFICATION.get(str(qualification))
    if claim is None:
        raise ValueError(f"finding qualification is outside the frozen map: {qualification!r}")
    evidence = finding.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("a material finding requires retrievable evidence")
    observed = []
    for item in evidence:
        if not isinstance(item, dict) or "kind" not in item or "record_sha256" not in item:
            raise ValueError("evidence item is missing its source reference")
        observed.append({"kind": item["kind"], "record_sha256": item["record_sha256"]})
    exposure = finding.get("exposure_usd")
    if not isinstance(exposure, str):
        raise ValueError("exposure must be the stored decimal string")
    workflow = finding.get("xaeli_explanation")
    if not isinstance(workflow, dict):
        raise ValueError("finding is missing the NOW CHANGED NEXT WHY PROOF text")
    return {
        "schema": EXPLANATION_VERSION,
        "finding_id": finding.get("finding_id"),
        "finding_sha256": finding.get("finding_sha256"),
        "authority": "NONE",
        "effect": "NONE",
        "independent_verification": "NOT_VERIFIED",
        "observed_facts": observed,
        "calculated_discrepancy_usd": exposure if claim == "CALCULATED_DISCREPANCY" else None,
        "suspected_exposure_usd": exposure if claim == "SUSPECTED_EXPOSURE" else None,
        "confirmed_recovery_usd": "0.00",
        "unverified_interpretation": claim == "UNVERIFIED_INTERPRETATION",
        "claim_class": claim,
        "evidence_class": evidence_class_for_claim(
            claim,
            withheld=str(finding.get("exposure_class") or "") == "WITHHELD_UNRESOLVED",
        ),
        "workflow": {
            "now": workflow.get("now"),
            "changed": workflow.get("changed"),
            "next": workflow.get("next"),
            "why": workflow.get("why"),
            "proof": workflow.get("proof"),
        },
        "limits": (
            "This explanation restates a stored DISPATER finding. "
            "It does not confirm recovery, authorize payment, or call a model."
        ),
    }
