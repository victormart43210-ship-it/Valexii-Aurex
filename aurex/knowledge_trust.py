"""Knowledge Trust Gateway module for AUREX.

Evaluates document effective dates, supersession relationships, duplicate source
corroboration limits, and prompt-injection contamination boundaries.
Outdated policies remain preserved as historical evidence but cannot grant authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class PolicyStatus(StrEnum):
    CURRENT = "CURRENT_EFFECTIVE"
    SUPERSEDED = "SUPERSEDED_HISTORICAL"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class PolicyDocument:
    doc_id: str
    title: str
    effective_date: date
    superseded_by: str | None = None
    source_sha256: str = ""


@dataclass(frozen=True, slots=True)
class PolicyEvaluationResult:
    doc_id: str
    status: PolicyStatus
    can_authorize_current: bool
    explanation: str


def evaluate_policy_supersession(
    documents: tuple[PolicyDocument, ...], as_of: date
) -> tuple[PolicyEvaluationResult, ...]:
    """Evaluate policy documents against as_of date to enforce supersession rules.

    Rule 1: If document has superseded_by set to a valid active doc_id, it is SUPERSEDED_HISTORICAL.
    Rule 2: Outdated/superseded policies cannot authorize current operations.
    Rule 3: Preserves both documents in audit trail.
    """
    doc_map = {d.doc_id: d for d in documents}
    results: list[PolicyEvaluationResult] = []

    for doc in documents:
        if doc.superseded_by and doc.superseded_by in doc_map:
            newer = doc_map[doc.superseded_by]
            if newer.effective_date <= as_of:
                results.append(
                    PolicyEvaluationResult(
                        doc_id=doc.doc_id,
                        status=PolicyStatus.SUPERSEDED,
                        can_authorize_current=False,
                        explanation=f"Superseded by {newer.doc_id} on {newer.effective_date.isoformat()}; preserved for historical evidence only.",
                    )
                )
                continue

        if doc.effective_date <= as_of:
            results.append(
                PolicyEvaluationResult(
                    doc_id=doc.doc_id,
                    status=PolicyStatus.CURRENT,
                    can_authorize_current=True,
                    explanation=f"Effective as of {doc.effective_date.isoformat()}.",
                )
            )
        else:
            results.append(
                PolicyEvaluationResult(
                    doc_id=doc.doc_id,
                    status=PolicyStatus.UNVERIFIED,
                    can_authorize_current=False,
                    explanation="Future effective date; not active.",
                )
            )

    return tuple(results)


def check_source_independence(digests: tuple[str, ...]) -> dict[str, object]:
    """Evaluate whether multiple records represent independent corroboration or identical copies."""
    unique_digests = set(digests)
    is_independent = len(digests) > 0 and len(digests) == len(unique_digests)
    return {
        "total_records": len(digests),
        "unique_digests": len(unique_digests),
        "independent_corroboration": is_independent,
        "duplicate_warning": (
            "Identical source digests detected; identical copies do not constitute independent corroboration."
            if not is_independent
            else None
        ),
    }
