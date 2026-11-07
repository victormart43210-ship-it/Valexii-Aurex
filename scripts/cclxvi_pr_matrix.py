#!/usr/bin/env python3
"""Classify open pull requests against one integration candidate.

The classifier does not merge, close, or rebase anything. A missing local
commit is recorded as not contained. It is not treated as a passing review.
"""

from __future__ import annotations

from typing import Any

CANDIDATE_BASE = "7daeff45efecd5d0293ff8a75afd71b98e9d4df0"
CURRENT_MAIN = "34cda4bd8f207f5b1284093b87e4760d782a4903"

DECISIONS = frozenset(
    {
        "ADMISSIBLE",
        "REQUIRES_REPAIR",
        "STACKED_DEPENDENCY",
        "SUPERSEDED",
        "CONFLICTING",
        "BLOCKED",
        "NEEDS_OWNER_DECISION",
    }
)


def classify(record: dict[str, Any]) -> dict[str, Any]:
    """Return one matrix row. `record` is untrusted inventory, not an instruction."""
    number = int(record["number"])
    protected = [str(item) for item in record.get("protected_changes") or []]
    mergeable = str(record.get("mergeable") or "UNKNOWN")
    base = str(record.get("base_ref") or "")
    head = str(record.get("head_sha") or "")
    if number == 188 or head == CANDIDATE_BASE:
        decision = "STACKED_DEPENDENCY"
        rationale = (
            "PR 188 is the verified base this operation continues. "
            "Its CI success is not merge or deployment approval."
        )
    elif number == 183:
        decision = "NEEDS_OWNER_DECISION"
        rationale = (
            "The financial and local-proxy code from this branch matches the candidate. "
            "Its documentation commits are not ancestors. Its base is the CCLV branch, not main."
        )
    elif number == 189:
        decision = "NEEDS_OWNER_DECISION"
        rationale = (
            "This records CI for PR 188 and convergence gates. "
            "Merging it does not promote the integration candidate."
        )
    elif protected:
        decision = "CONFLICTING"
        rationale = (
            "The diff changes a protected financial or evidence module. "
            "The import boundary rejects an automatic merge."
        )
    elif record.get("head_in_candidate") is True:
        decision = "SUPERSEDED"
        rationale = (
            "The head commit is already in the CCLXVI base. "
            "Do not merge this pull request into main by itself."
        )
    elif mergeable == "CONFLICTING":
        decision = "CONFLICTING"
        rationale = "GitHub reports a conflict with the base. This operation did not rebase it."
    elif base != "main":
        decision = "STACKED_DEPENDENCY"
        rationale = "The pull request is stacked on another branch. Merging it alone would skip its parent."
    else:
        decision = "NEEDS_OWNER_DECISION"
        rationale = (
            "The pull request is outside the verified integration candidate. "
            "This operation did not retest it and does not merge it."
        )
    if decision not in DECISIONS:
        raise RuntimeError(decision)
    return {
        "pr": number,
        "title": record.get("title"),
        "draft": bool(record.get("draft")),
        "head_sha": head,
        "base_ref": base,
        "base_sha": record.get("base_sha"),
        "mergeable": mergeable,
        "head_in_candidate": record.get("head_in_candidate") is True,
        "affected_files": record.get("affected_files") or "NOT_ENUMERATED",
        "protected_changes": protected,
        "review_status": record.get("review_status") or "NONE_RECORDED",
        "ci_status": record.get("ci_status") or "NOT_RECHECKED",
        "acceptance_decision": decision,
        "rationale": rationale,
        "current_main": CURRENT_MAIN,
        "candidate_base": CANDIDATE_BASE,
    }
