"""Exact bounded search over reversible remediation sequences.

This is a safe *candidate selector*, not an executor or authority layer.
It complements existing immutable experiment remediation lineage without
rewriting historical FAIL or touching workers, databases or remote systems.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

MAX_ACTIONS = 12
MAX_STEPS = 4


@dataclass(frozen=True, slots=True)
class FixStep:
    key: str
    problem_code: str
    lineage_group: str
    fix: tuple[str, ...]
    verify: tuple[str, ...]
    rollback: tuple[str, ...]
    minutes: int
    risk: int
    cost_usd: Decimal
    impact: float
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    reversible: bool = True
    historical_successes: int = 0
    historical_failures: int = 0
    independently_admitted_history: bool = False


@dataclass(frozen=True, slots=True)
class PlanCandidate:
    steps: tuple[FixStep, ...]
    utility: float
    conservative_success: float


@dataclass(frozen=True, slots=True)
class SearchResult:
    problem_code: str
    status: str
    proposed: PlanCandidate | None
    alternatives: tuple[PlanCandidate, ...]
    evaluated: int
    next_on_success: str = "AWAIT_INDEPENDENT_RETEST_NOT_PASS"
    next_on_failure: str = "HOLD_REVIEW_ROLLBACK"
    next_on_unknown: str = "HOLD_ESCALATE"
    authority: str = "ANALYSIS_ONLY_NO_EFFECT"


def beta_conservative(successes: int, failures: int) -> float:
    """Beta(1,1) one-sigma lower bound: ranking heuristic, not guaranteed CI."""
    if (
        isinstance(successes, bool) or isinstance(failures, bool)
        or not isinstance(successes, int) or not isinstance(failures, int)
        or successes < 0 or failures < 0 or successes + failures > 1_000_000
    ):
        raise ValueError("invalid independent history counts")
    a = successes + 1
    b = failures + 1
    n = a + b
    mean = a / n
    variance = a * b / (n * n * (n + 1))
    return max(0.0, mean - math.sqrt(variance))


def _validate(steps: Sequence[FixStep]) -> None:
    if len(steps) > MAX_ACTIONS:
        raise ValueError("maximum 12 proposed actions")
    keys: set[str] = set()
    for step in steps:
        if not isinstance(step, FixStep) or not step.key or step.key in keys:
            raise ValueError("duplicate/invalid proposed action")
        keys.add(step.key)
        if (
            not step.problem_code or not step.lineage_group
            or not step.fix or not all(step.fix)
            or not step.verify or not all(step.verify)
            or not step.rollback or not all(step.rollback)
            or not isinstance(step.reversible, bool)
            or not isinstance(step.independently_admitted_history, bool)
            or isinstance(step.minutes, bool) or not isinstance(step.minutes, int)
            or not 1 <= step.minutes <= 86_400
            or isinstance(step.risk, bool) or not isinstance(step.risk, int)
            or not 0 <= step.risk <= 5
            or not isinstance(step.cost_usd, Decimal)
            or not step.cost_usd.is_finite() or step.cost_usd < 0
            or not isinstance(step.impact, (int, float)) or isinstance(step.impact, bool)
            or not math.isfinite(step.impact) or not 0 <= step.impact <= 100
            or step.key in step.requires or step.key in step.conflicts
            or len(set(step.requires)) != len(step.requires)
            or len(set(step.conflicts)) != len(step.conflicts)
        ):
            raise ValueError("invalid action scope, instructions, resources or evidence")
        beta_conservative(step.historical_successes, step.historical_failures)


def _sequence(selected: Sequence[FixStep]) -> tuple[FixStep, ...] | None:
    by_key = {s.key: s for s in selected}
    if any(any(key not in by_key for key in s.requires) for s in selected):
        return None
    if any(any(key in by_key for key in s.conflicts) for s in selected):
        return None
    if len({s.lineage_group for s in selected}) < len(selected):
        # Don't treat multiple correlated remedy proposals as independent gain.
        return None
    ordered: list[FixStep] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> bool:
        if key in visiting:
            return False
        if key in visited:
            return True
        visiting.add(key)
        for predecessor in sorted(by_key[key].requires):
            if not visit(predecessor):
                return False
        visiting.remove(key)
        visited.add(key)
        ordered.append(by_key[key])
        return True

    for key in sorted(by_key):
        if not visit(key):
            return None
    return tuple(ordered)


def choose_remediation(
    problem_code: str,
    steps: Sequence[FixStep],
    *,
    max_total_minutes: int = 60,
    max_total_risk: int = 3,
    max_cost_usd: Decimal = Decimal("0"),
    max_steps: int = MAX_STEPS,
) -> SearchResult:
    """Return the best *eligible* sequence across the supplied finite catalog.

    Selection is exhaustive over <=12 candidates and <=4 steps. Its heuristic
    utility is not a calibrated probability or a claim of global real-world
    optimality. Every proposed fix includes verify and rollback instructions.
    """
    if not isinstance(problem_code, str) or not problem_code.strip() or len(problem_code) > 80:
        raise ValueError("problem_code required")
    _validate(steps)
    if (
        isinstance(max_total_minutes, bool) or not isinstance(max_total_minutes, int)
        or not 0 < max_total_minutes <= 86_400
        or isinstance(max_total_risk, bool) or not isinstance(max_total_risk, int)
        or not 0 <= max_total_risk <= 20
        or isinstance(max_steps, bool) or not isinstance(max_steps, int)
        or not 1 <= max_steps <= MAX_STEPS
        or not isinstance(max_cost_usd, Decimal) or not max_cost_usd.is_finite()
        or max_cost_usd < 0
    ):
        raise ValueError("invalid governance constraints")
    relevant = [s for s in steps if s.problem_code == problem_code and s.reversible]
    candidates: list[PlanCandidate] = []
    evaluated = 0
    for count in range(1, min(len(relevant), max_steps) + 1):
        for combo in itertools.combinations(relevant, count):
            evaluated += 1
            ordered = _sequence(combo)
            if ordered is None:
                continue
            if (
                sum(s.minutes for s in ordered) > max_total_minutes
                or sum(s.risk for s in ordered) > max_total_risk
                or sum((s.cost_usd for s in ordered), Decimal("0")) > max_cost_usd
            ):
                continue
            lower_bounds = [
                beta_conservative(
                    s.historical_successes if s.independently_admitted_history else 0,
                    s.historical_failures if s.independently_admitted_history else 0,
                )
                for s in ordered
            ]
            # Do not multiply successes as independent probabilities. The
            # minimum lower bound is deliberately conservative for a sequence.
            success = min(lower_bounds)
            impact = max(s.impact for s in ordered)
            minutes = sum(s.minutes for s in ordered)
            risk = sum(s.risk for s in ordered)
            utility = impact * success - 0.7 * risk - 0.01 * minutes
            candidates.append(PlanCandidate(ordered, round(utility, 6), success))
    candidates.sort(
        key=lambda x: (-x.utility, len(x.steps), tuple(step.key for step in x.steps))
    )
    if not candidates:
        return SearchResult(problem_code, "HOLD_NO_ADMISSIBLE_REMEDY", None, (), evaluated)
    return SearchResult(
        problem_code, "REVIEW_REQUIRED", candidates[0], tuple(candidates[1:6]), evaluated
    )
