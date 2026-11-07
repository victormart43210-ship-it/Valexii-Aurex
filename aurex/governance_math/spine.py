"""Read-only AUREX research reasoning spine: retrieve → plan → test next.

No effect path, privileged endpoint, execution, or automatic certification.
Records supplied here remain caller assertions until checked separately by the
existing signed-witness/experiment-admission pipeline.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from .information_gain import Probe, TestChoice, rank_next_tests
from .optimization import FixStep, SearchResult, choose_remediation
from .retrieval import Incident, Match, retrieve_incidents


@dataclass(frozen=True, slots=True)
class ResearchAdvice:
    problem_code: str
    similar_cases: tuple[Match, ...]
    remediation: SearchResult
    test_next: tuple[TestChoice, ...]
    gate: str
    authority: str = "ADVISORY_ONLY_NO_EXECUTION"


def advise(
    problem_code: str,
    description: str,
    *,
    incidents: Sequence[Incident] = (),
    fixes: Sequence[FixStep] = (),
    probes: Sequence[Probe] = (),
    prior: float | None = None,
    max_cost_usd: Decimal = Decimal("0"),
    max_risk: int = 2,
) -> ResearchAdvice:
    """Combine explainable incident retrieval, bounded safe planning and EIG.

    Unknown outcomes and uncalibrated test choices demote to HOLD. A remedy
    recommendation is a *proposal* even when all supplied inputs look valid.
    """
    if not isinstance(description, str) or not 0 < len(description) <= 512:
        raise ValueError("bounded incident description is required")
    matches = retrieve_incidents(description, incidents) if incidents else ()
    proposed = choose_remediation(
        problem_code, fixes, max_cost_usd=max_cost_usd, max_total_risk=max_risk
    )
    tests = (
        rank_next_tests(prior, probes, max_risk=max_risk, max_cost_usd=max_cost_usd)
        if prior is not None else ()
    )
    return ResearchAdvice(
        problem_code=problem_code,
        similar_cases=matches,
        remediation=proposed,
        test_next=tests,
        gate="REVIEW_REQUIRED" if proposed.proposed is not None else "HOLD",
    )
