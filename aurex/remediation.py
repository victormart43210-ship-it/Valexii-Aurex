"""Governed outcome-to-remediation planner for the VALEXII AUREX kernel.

Each recognized outcome is immediately paired with a ranked proposed fix,
independent verification steps, rollback, and a post-action contingency.
Unknown outcomes fail closed. This module NEVER performs side effects or grants
authority. All estimates are *heuristics*, not validated success probabilities.

Run: python -m aurex.remediation --matrix
     python -m aurex.remediation --outcome API_CONTRACT_FAILURE
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any


class Outcome(StrEnum):
    HEALTHY = "HEALTHY"
    TEST_FAILURE = "TEST_FAILURE"
    TYPE_LINT_FAILURE = "TYPE_LINT_FAILURE"
    API_CONTRACT_FAILURE = "API_CONTRACT_FAILURE"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    EVIDENCE_INTEGRITY_FAILURE = "EVIDENCE_INTEGRITY_FAILURE"
    WORKER_LEASE_CONFLICT = "WORKER_LEASE_CONFLICT"
    BUDGET_DENIED = "BUDGET_DENIED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    FRONTEND_PROXY_FAILURE = "FRONTEND_PROXY_FAILURE"
    RELEASE_REGRESSION = "RELEASE_REGRESSION"
    TIMEOUT = "TIMEOUT"
    STALE_EVIDENCE = "STALE_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    UNVERIFIED = "UNVERIFIED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class ActionOutcome(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    INCONCLUSIVE = "INCONCLUSIVE"
    CANCELLED = "CANCELLED"
    REVOKED = "REVOKED"
    INTEGRITY_FAILED = "INTEGRITY_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Remedy:
    key: str
    outcome: Outcome
    fix: tuple[str, ...]
    verification: tuple[str, ...]
    rollback: tuple[str, ...]
    risk: int
    minutes: int
    hypothesized_effectiveness: float
    reversible: bool = True
    spend_usd: Decimal = Decimal("0")
    requires_approval: bool = True


@dataclass(frozen=True)
class Option:
    key: str
    rank_score: float
    bayesian_success_lower_bound: float
    fix: tuple[str, ...]
    verification: tuple[str, ...]
    rollback: tuple[str, ...]
    requires_approval: bool


@dataclass(frozen=True)
class Contingency:
    result: ActionOutcome
    next_state: str
    fix_immediately_after: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    detected_outcome: Outcome
    gate: str
    selection: Option | None
    alternatives: tuple[Option, ...]
    immediate_response: tuple[str, ...]
    contingencies: tuple[Contingency, ...]
    explanation: str
    execution: str = "PROPOSE_ONLY_NOT_EXECUTED"


def _remedy(
    key: str,
    outcome: Outcome,
    fix: tuple[str, ...],
    verification: tuple[str, ...],
    rollback: tuple[str, ...],
    *,
    risk: int = 1,
    minutes: int = 15,
    effectiveness: float = 0.7,
    reversible: bool = True,
) -> Remedy:
    return Remedy(key, outcome, fix, verification, rollback, risk, minutes, effectiveness, reversible)


# Curated response *templates*, NOT shell commands or live write access.
# Explicit operator approval and independent evidence are required separately.
CATALOG: tuple[Remedy, ...] = (
    _remedy("tests_isolate_patch", Outcome.TEST_FAILURE,
            ("Reproduce the failing test at the exact SHA in an isolated branch.",
             "Implement the smallest targeted code change with a regression test."),
            ("Rerun failing case, full pytest, Ruff, Mypy and independent review.",
             "Confirm no unrelated behavior changed."),
            ("Discard the branch change and preserve the original failure evidence.",)),
    _remedy("tests_revert_candidate", Outcome.TEST_FAILURE,
            ("Prepare a revert of the candidate commit; do not alter protected main.",
             "Request reviewer approval before applying the revert."),
            ("Rerun exact-SHA CI and compare pre/post behavior.",),
            ("Restore candidate branch from recorded SHA if independently justified.",),
            risk=3, minutes=8, effectiveness=0.85),
    _remedy("types_fix", Outcome.TYPE_LINT_FAILURE,
            ("Collect exact mypy/Ruff diagnostics and fix their root causes without silencing checks.",),
            ("Run mypy aurex, ruff check . and affected tests.",),
            ("Revert only the proposed fix in the isolated worktree.",)),
    _remedy("contract_fix", Outcome.API_CONTRACT_FAILURE,
            ("Diff versioned OpenAPI schemas between deployed backend and website proxy.",
             "Correct the incompatible implementation on an isolated branch; retain auth boundaries."),
            ("Run independent schema contract and authenticated integration tests.",),
            ("Restore the prior versioned contract and client from exact SHAs.",),
            effectiveness=0.85),
    _remedy("contract_hold", Outcome.API_CONTRACT_FAILURE,
            ("Disable affected frontend action; retain an honest unavailable/read-only state.",
             "Do not forge success responses."),
            ("Verify that unverified capabilities display unavailable and no mutating requests run.",),
            ("Reenable only after independent backend/proxy contract proof.",),
            minutes=3, effectiveness=0.6),
    _remedy("auth_contain", Outcome.AUTHENTICATION_FAILURE,
            ("Deny the request and audit the failure without logging secrets.",
             "Check proxy header handling and secret configuration in a controlled environment."),
            ("Independently confirm missing/invalid tokens return 401 and no privileged side effects.",),
            ("Keep endpoint disabled; restore last known good secret configuration under approval.",),
            risk=1, effectiveness=0.9),
    _remedy("db_recover", Outcome.DATABASE_UNAVAILABLE,
            ("Hold writes and check volume mount, SQLite path, permissions and backups.",
             "Prepare a read-only recovery plan against a copy, not the sole production database."),
            ("Independently verify persistence across restart and SQLite integrity on the copy.",),
            ("Return to read-only HOLD and preserve backups and WAL evidence.",),
            effectiveness=0.8),
    _remedy("evidence_quarantine", Outcome.EVIDENCE_INTEGRITY_FAILURE,
            ("Quarantine conflicting or digest-mismatched evidence; prevent promotion to authority.",
             "Recompute hashes from immutable source bytes and request independent provenance audit."),
            ("Require independent exact-digest and provenance verification.",),
            ("Maintain quarantine; never rewrite historical evidence to hide discrepancies.",),
            effectiveness=0.95),
    _remedy("lease_fence", Outcome.WORKER_LEASE_CONFLICT,
            ("Stop conflicting finalizations and capture job, lease generation and token audit metadata.",
             "Propose a fenced state-transition fix in an isolated worktree."),
            ("Independently test concurrent claim, expiry, cancellation, revocation and stale completion.",),
            ("Reject stale writes and revoke the affected lease; preserve job history.",),
            effectiveness=0.9),
    _remedy("budget_zero", Outcome.BUDGET_DENIED,
            ("Keep external paid execution disabled; select a bounded offline or cached alternative.",
             "Request separate approval if funding is truly necessary."),
            ("Verify $0 reservation and spending, and absence of remote calls.",),
            ("Abort the alternative and retain the $0 policy.",),
            effectiveness=0.9),
    _remedy("model_fallback", Outcome.MODEL_UNAVAILABLE,
            ("Return explicit worker-unavailable/HOLD and preserve queued work safely.",
             "Offer an offline deterministic analysis path where supported."),
            ("Confirm HTTP 503 or equivalent honest state, bounded timeouts and no hidden model fallback.",),
            ("Keep execution disabled until a separately authorized provider is verified.",)),
    _remedy("proxy_repair", Outcome.FRONTEND_PROXY_FAILURE,
            ("Keep bearer credentials on the server and block the affected website action.",
             "Repair only proxy routing, auth propagation, CORS and versioned request mapping."),
            ("Use independent server-to-server auth tests and browser E2E without exposing tokens.",),
            ("Restore read-only website state and prior proxy configuration.",),
            effectiveness=0.85),
    _remedy("release_contain", Outcome.RELEASE_REGRESSION,
            ("Pause rollout and propose reverting to the independently verified deployment SHA.",
             "Preserve error telemetry and evidence before any change."),
            ("Run canary and post-rollback health, functional and persistence checks.",),
            ("Stop deployment and enter incident HOLD if previous version is unsafe.",),
            risk=2, minutes=5, effectiveness=0.9),
    _remedy("release_patch", Outcome.RELEASE_REGRESSION,
            ("Isolate regression, prepare minimal corrective patch and new exact-head CI run.",),
            ("Rerun full regression suite, canary and independent release check.",),
            ("Discard candidate patch and retain rollback plan.",),
            risk=1, minutes=30, effectiveness=0.7),
    _remedy("timeout_guard", Outcome.TIMEOUT,
            ("Stop automatic retries and inspect idempotency key, existing job and lease state.",
             "Propose a bounded retry only after duplicate-side-effect risk is excluded."),
            ("Verify exactly-one finalized effect, timeout budgets and stale lease rejection.",),
            ("Cancel retry, revoke stale lease and retain the original state.",)),
    _remedy("stale_refresh", Outcome.STALE_EVIDENCE,
            ("Demote previous CLEAR to historical status and request fresh external evidence.",),
            ("Verify new witness timestamp, source, SHA and freshness horizon.",),
            ("Remain HOLD; do not reuse stale evidence to authorize current effects.",),
            effectiveness=0.85),
    _remedy("conflict_challenge", Outcome.CONFLICTING_EVIDENCE,
            ("Preserve all conflicting claims; suspend authority and launch independent challenger review.",),
            ("Trace each claim through ROTAS and check source correlation.",),
            ("Keep both historical records and unresolved HOLD.",),
            effectiveness=0.85),
    _remedy("verify_independent", Outcome.UNVERIFIED,
            ("Collect independent witness proof at the exact source and deployment SHA.",
             "Do not permit the producing agent to be its own sole verifier."),
            ("Validate source identity, integrity and actual deployed behavior independently.",),
            ("Preserve UNVERIFIED and block downstream authority.",)),
    _remedy("cancel_fence", Outcome.CANCELLED,
            ("Preserve cancellation and revoke associated lease generation; do not restart silently.",),
            ("Prove stale workers cannot finalize after cancellation.",),
            ("Keep job cancelled and retain immutable audit history.",),
            effectiveness=0.9),
)


FOLLOW_UPS: dict[ActionOutcome, tuple[str, tuple[str, ...]]] = {
    ActionOutcome.SUCCEEDED: (
        "AWAIT_INDEPENDENT_VERIFICATION",
        ("Re-run independent verification and record exact SHA; do not self-declare PASS.",)),
    ActionOutcome.FAILED: (
        "ROLLBACK_PENDING_APPROVAL",
        ("Stop attempts; prepare the remedy's rollback steps and capture the new failure evidence.",)),
    ActionOutcome.TIMED_OUT: (
        "HOLD",
        ("Stop retries; inspect idempotency and current lease before considering rollback or retry.",)),
    ActionOutcome.INCONCLUSIVE: (
        "HOLD",
        ("Gather additional independent evidence; do not infer success or safety.",)),
    ActionOutcome.CANCELLED: (
        "HOLD",
        ("Revoke active leases and confirm no pending side effects.",)),
    ActionOutcome.REVOKED: (
        "HOLD",
        ("Propagate revocation, fence workers and preserve evidence.",)),
    ActionOutcome.INTEGRITY_FAILED: (
        "QUARANTINE",
        ("Quarantine impacted evidence and request a distinct external audit.",)),
    ActionOutcome.UNAUTHORIZED: (
        "DENY",
        ("Deny the attempted action and escalate approval; do not bypass the authority gate.",)),
    ActionOutcome.UNKNOWN: (
        "HOLD",
        ("Quarantine unknown result and request independent assessment; never assume success.",)),
}


def beta_lower_bound(successes: int, failures: int) -> float:
    """Conservative one-sigma lower bound under a Beta(1,1) prior.

    A heuristic ranking feature: *not* an independently calibrated success
    probability, and never sufficient to grant authority.
    """
    if (isinstance(successes, bool) or isinstance(failures, bool)
            or not isinstance(successes, int) or not isinstance(failures, int)
            or successes < 0 or failures < 0):
        raise ValueError("success/failure counts must be nonnegative integers")
    a = successes + 1
    b = failures + 1
    total = a + b
    mean = a / total
    variance = (a * b) / (total * total * (total + 1))
    return max(0.0, mean - math.sqrt(variance))


def _validated_history(history: dict[str, tuple[int, int]] | None) -> dict[str, tuple[int, int]]:
    if history is None:
        return {}
    if not isinstance(history, dict):
        raise ValueError("history must be an object")
    accepted: dict[str, tuple[int, int]] = {}
    for key, counts in history.items():
        if (not isinstance(key, str) or not isinstance(counts, tuple)
                or len(counts) != 2):
            raise ValueError("history must map remedy key to (successes, failures)")
        beta_lower_bound(counts[0], counts[1])
        accepted[key] = counts
    return accepted


def _rank(remedy: Remedy, severity: int, counts: tuple[int, int]) -> Option:
    lower = beta_lower_bound(*counts)
    # Expected mitigated impact, minus risk, time and uncertainty penalties.
    # Numbers are transparent heuristic weights and require future calibration.
    score = (severity * lower * remedy.hypothesized_effectiveness
             - 0.7 * remedy.risk - 0.015 * remedy.minutes)
    return Option(
        remedy.key, round(score, 5), round(lower, 5),
        remedy.fix, remedy.verification, remedy.rollback,
        remedy.requires_approval,
    )


def _coerce_outcome(value: str | Outcome) -> Outcome:
    if isinstance(value, Outcome):
        return value
    try:
        return Outcome(value.upper())
    except (ValueError, AttributeError):
        return Outcome.UNKNOWN


def plan(
    observed: str | Outcome,
    *,
    severity: int = 5,
    max_risk: int = 2,
    max_spend_usd: Decimal = Decimal("0"),
    history: dict[str, tuple[int, int]] | None = None,
) -> Plan:
    """Propose the best *eligible* recorded runbook, with every result follow-up.

    Does not execute anything, assert independence, or check external authority.
    Unknown/unmapped outcomes get an immediate HOLD + manual-review fix.
    """
    if (isinstance(severity, bool) or not isinstance(severity, int)
            or not 1 <= severity <= 10):
        raise ValueError("severity must be integer from 1 to 10")
    if (isinstance(max_risk, bool) or not isinstance(max_risk, int)
            or not 1 <= max_risk <= 5):
        raise ValueError("max_risk must be integer from 1 to 5")
    if not isinstance(max_spend_usd, Decimal) or not max_spend_usd.is_finite() or max_spend_usd < 0:
        raise ValueError("max_spend_usd must be a finite nonnegative Decimal")
    counts = _validated_history(history)
    incident = _coerce_outcome(observed)
    contingencies = tuple(Contingency(result, state, steps)
                          for result, (state, steps) in FOLLOW_UPS.items())
    if incident == Outcome.HEALTHY:
        return Plan(incident, "NO_ACTION_NOT_AUTHORITY", None, (),
                    ("Maintain observation; require separate freshness and security verification.",),
                    contingencies, "A healthy observation does not prove safety.")
    options = [
        _rank(remedy, severity, counts.get(remedy.key, (0, 0)))
        for remedy in CATALOG
        if remedy.outcome == incident and remedy.risk <= max_risk
        and remedy.spend_usd <= max_spend_usd and remedy.reversible
    ]
    options.sort(key=lambda o: (-o.rank_score, o.key))
    if not options:
        return Plan(
            incident, "HOLD", None, (),
            ("Contain the affected effect, preserve evidence and request independent triage.",
             "Do not guess a fix or grant authority; unknown outcomes require review."),
            contingencies, "No qualifying reversible $0 remediation found.",
        )
    selected = options[0]
    return Plan(
        incident, "REVIEW_REQUIRED", selected, tuple(options[1:]),
        selected.fix, contingencies,
        "Highest conservative eligible heuristic score, NOT proven globally optimal. "
        "All writes require separate authorization, preflight, rollback and independent verification.",
    )


def matrix(**kwargs: Any) -> tuple[Plan, ...]:
    """Exhaustive coverage of the *defined* outcome taxonomy, including UNKNOWN."""
    return tuple(plan(item, **kwargs) for item in Outcome)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--outcome", help="Observed outcome code; unknown codes fail closed")
    group.add_argument("--matrix", action="store_true", help="Generate every defined outcome and its fix")
    parser.add_argument("--severity", type=int, default=5)
    parser.add_argument("--max-risk", type=int, default=2)
    args = parser.parse_args()
    result: Any = (matrix(severity=args.severity, max_risk=args.max_risk)
                   if args.matrix else plan(args.outcome, severity=args.severity, max_risk=args.max_risk))
    payload = [asdict(row) for row in result] if isinstance(result, tuple) else asdict(result)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
