"""A recorded observation proposal. This module does not execute one."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

SCHEMA = "aurex.proposal.v1"
_OBSERVATION = "aurex.observation.v1"


def propose(observation: dict[str, Any], *, now: datetime, max_age: timedelta) -> dict[str, Any]:
    """Record a hypothesis only when its evidence is fresh and contested.

    An empty counterevidence list abstains. A requested effect is refused.
    The result never launches work, moves money, or changes production.
    """
    problems: list[str] = []
    if observation.get("schema") != _OBSERVATION:
        problems.append("SCHEMA_REQUIRED")
    source = observation.get("source_sha256")
    if not isinstance(source, str) or len(source) != 64:
        problems.append("SOURCE_DIGEST_REQUIRED")
    observed = observation.get("observed_at")
    if not isinstance(observed, datetime) or observed.tzinfo is None or now.tzinfo is None:
        problems.append("TIMESTAMP_REQUIRED")
    elif observed > now + timedelta(minutes=5):
        problems.append("FUTURE_OBSERVATION")
    elif now - observed > max_age:
        problems.append("STALE_EVIDENCE")
    if observation.get("effect") not in (None, "NONE"):
        problems.append("EFFECT_REFUSED")
    counter = observation.get("counterevidence")
    if not isinstance(counter, list):
        problems.append("COUNTEREVIDENCE_REQUIRED")
        contested = False
    else:
        contested = bool(counter)
    if problems:
        decision = "REFUSED"
    elif not contested:
        decision = "ABSTAIN"
    else:
        decision = "RECORDED"
    return {
        "schema": SCHEMA,
        "decision": decision,
        "effect": "NONE",
        "authority": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "launch": "NOT_STARTED",
        "independent_verification": "NOT_VERIFIED",
        "problems": problems,
    }
