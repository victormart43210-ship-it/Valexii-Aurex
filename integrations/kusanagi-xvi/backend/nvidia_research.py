"""Optional NVIDIA synthesis on aggregate-only, non-sensitive triage data.

No tools, autonomous calls, evidence promotion, or vendor-dependent inference.
This is a constrained adapter wrapper, NOT NousResearch Hermes Agent itself.
Official Hermes Agent can separately use NVIDIA NIM (operator-only sandbox).
"""
from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

ALLOWED_KEYS = frozenset({"sourceFamilyCount", "supportFamilies", "contradictFamilies", "conflictingFamilies"})


def optional_nvidia_explanation(summary: dict[str, Any], *, reserve: Callable[[], bool], answer: Callable[[str], dict[str, str]]) -> dict[str, Any]:
    """No model call until five independent flags & atomic quota reservation.

    Production caller MUST bind 'reserve' to durable SQLite quota and 'answer'
    to the fixed-host NVIDIA llm.answer adapter, within owner-only service API.
    Does not authorize model output as evidence. Summaries contain counts only.
    """
    gates = (
        os.environ.get("RAILWAY_ENVIRONMENT_NAME") == "aurex-staging",
        os.environ.get("AUREX_RESEARCH_LAB_ENABLED") == "true",
        os.environ.get("AUREX_NVIDIA_SYNTHESIS_ENABLED") == "true",
        os.environ.get("AUREX_NVIDIA_ALLOW_TEXT_EGRESS") == "true",
        os.environ.get("AUREX_LLM_PROVIDER") == "nvidia",
        os.environ.get("AUREX_LLM_ENABLED") == "true",
        os.environ.get("AUREX_LLM_ALLOW_BILLING") == "true",
    )
    hold = {"status": "HOLD", "reply": None, "authority": "NONE", "verification": "NOT_VERIFIED"}
    if not all(gates):
        return hold
    if not isinstance(summary, dict) or set(summary) != ALLOWED_KEYS:
        raise ValueError("Only permitted aggregate counts can leave the service")
    counts = [summary[key] for key in sorted(ALLOWED_KEYS)]
    if any(type(n) is not int or n < 0 or n > 16 for n in counts):
        raise ValueError("Invalid aggregate counters")
    if not reserve():
        return hold
    q = ("Explain possible reasons for disagreement between unverified evidence "
         "sources and propose manual checks. No determination, no tools, and "
         "no claim of proof. Aggregates only: " + ", ".join(f"{k}={summary[k]}" for k in sorted(ALLOWED_KEYS)))
    try:
        r = answer(q)
        if not isinstance(r, dict) or r.get("authority") != "NONE" or r.get("verification") != "NOT_VERIFIED" or not isinstance(r.get("reply"), str):
            return hold
        return {"status": "UNVERIFIED_NVIDIA_NARRATIVE", "reply": r["reply"][:1200], "authority": "NONE", "verification": "NOT_VERIFIED"}
    except Exception:  # noqa: BLE001 (untrusted opt-in provider fails closed)
        return hold
