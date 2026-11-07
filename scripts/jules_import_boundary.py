#!/usr/bin/env python3
"""Typed gate for a future Jules recovery diff.

This does not import Jules's work. It rejects a name-status diff that deletes
or rewrites the current financial and evidence safeguards. A diff that only
adds new files is acceptable for a later review. It is not an automatic merge.
"""

from __future__ import annotations

PROTECTED = frozenset(
    {
        "aurex/customer_sovereignty.py",
        "aurex/dispater_api.py",
        "aurex/dispater_intelligence.py",
        "aurex/dispater_receipt.py",
        "aurex/dispater_store.py",
        "aurex/egress.py",
        "aurex/evidence_kernel.py",
    }
)


def review_name_status(text: str) -> dict[str, object]:
    protected: list[str] = []
    added: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        paths = parts[1:]
        if status.startswith("A") and len(paths) == 1:
            added.append(paths[0])
        if status[:1] in {"D", "M", "R"}:
            for path in paths:
                if path in PROTECTED:
                    protected.append(f"{status} {path}")
    if protected:
        return {
            "decision": "REJECTED",
            "auto_merge": False,
            "protected_changes": protected,
            "added": added,
            "owner": "PENDING_JULES_RECOVERY",
        }
    return {
        "decision": "ACCEPTABLE_FOR_REVIEW",
        "auto_merge": False,
        "protected_changes": [],
        "added": added,
        "owner": "PENDING_JULES_RECOVERY",
    }
