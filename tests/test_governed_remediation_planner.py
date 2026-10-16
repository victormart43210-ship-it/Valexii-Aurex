"""CUSTOS tests: every outcome has an immediate governed remedy."""
from __future__ import annotations

import json
from decimal import Decimal

import pytest

from aurex.remediation import (
    ActionOutcome,
    CATALOG,
    FOLLOW_UPS,
    Outcome,
    beta_lower_bound,
    main,
    matrix,
    plan,
)


def test_all_defined_outcomes_have_immediate_safe_response() -> None:
    plans = matrix()
    assert len(plans) == len(Outcome)
    assert {p.detected_outcome for p in plans} == set(Outcome)
    for p in plans:
        assert p.immediate_response
        assert p.execution == "PROPOSE_ONLY_NOT_EXECUTED"
        assert p.gate in {"HOLD", "REVIEW_REQUIRED", "NO_ACTION_NOT_AUTHORITY"}
        assert len(p.contingencies) == len(ActionOutcome)
        assert {c.result for c in p.contingencies} == set(ActionOutcome)
        assert all(c.fix_immediately_after for c in p.contingencies)


def test_every_known_problem_gets_specific_fix_and_verification() -> None:
    for code in Outcome:
        result = plan(code)
        if code in (Outcome.HEALTHY, Outcome.UNKNOWN):
            assert result.selection is None
            continue
        assert result.selection is not None, code
        assert result.selection.fix
        assert result.selection.verification
        assert result.selection.rollback
        assert result.gate == "REVIEW_REQUIRED"


def test_no_unsupported_outcome_is_treated_as_success() -> None:
    for value in ("new_zero_day_outcome", "", "success", "WAITING_FOR_GODOT"):
        result = plan(value)
        assert result.detected_outcome == Outcome.UNKNOWN
        assert result.gate == "HOLD"
        assert result.selection is None
        assert "review" in " ".join(result.immediate_response).lower()


def test_healthy_is_not_security_authority() -> None:
    result = plan("HEALTHY")
    assert result.selection is None
    assert result.gate == "NO_ACTION_NOT_AUTHORITY"


def test_rank_is_deterministic() -> None:
    a = plan(Outcome.TEST_FAILURE)
    b = plan(Outcome.TEST_FAILURE)
    assert a == b
    assert a.selection is not None
    assert a.selection.key == "tests_isolate_patch"


def test_risk_gate_filters_revert_even_with_favorable_history() -> None:
    result = plan(Outcome.TEST_FAILURE, max_risk=2,
                  history={"tests_revert_candidate": (500, 0)})
    assert result.selection is not None
    assert result.selection.key == "tests_isolate_patch"
    assert all(x.key != "tests_revert_candidate" for x in result.alternatives)


def test_high_quality_history_changes_advisory_rank_not_authority() -> None:
    result = plan(Outcome.TEST_FAILURE, max_risk=3, severity=10,
                  history={"tests_isolate_patch": (0, 30),
                           "tests_revert_candidate": (200, 1)})
    assert result.selection is not None
    assert result.selection.key == "tests_revert_candidate"
    assert result.gate == "REVIEW_REQUIRED"


def test_zero_spend_policy_is_default() -> None:
    result = plan(Outcome.MODEL_UNAVAILABLE)
    assert result.selection is not None
    selected = next(r for r in CATALOG if r.key == result.selection.key)
    assert selected.spend_usd == Decimal("0")


def test_inconclusive_and_failure_results_fail_closed() -> None:
    result = plan(Outcome.API_CONTRACT_FAILURE)
    contingencies = {c.result: c for c in result.contingencies}
    assert contingencies[ActionOutcome.SUCCEEDED].next_state == "AWAIT_INDEPENDENT_VERIFICATION"
    assert contingencies[ActionOutcome.FAILED].next_state == "ROLLBACK_PENDING_APPROVAL"
    assert contingencies[ActionOutcome.UNKNOWN].next_state == "HOLD"
    assert contingencies[ActionOutcome.INTEGRITY_FAILED].next_state == "QUARANTINE"


def test_beta_bound_is_conservative_and_bounded() -> None:
    assert 0 < beta_lower_bound(0, 0) < 0.5
    assert beta_lower_bound(200, 0) > beta_lower_bound(0, 200)
    assert 0 <= beta_lower_bound(100, 100) < 1


@pytest.mark.parametrize("s,f", [(-1, 0), (0, -1), (1.2, 3), (True, 0)])
def test_invalid_history_counts_fail(s: int, f: int) -> None:
    with pytest.raises(ValueError):
        beta_lower_bound(s, f)


@pytest.mark.parametrize("severity,max_risk", [(0, 2), (11, 2), (5, 0), (5, 6), (True, 2)])
def test_invalid_policy_limits_fail(severity: int, max_risk: int) -> None:
    with pytest.raises(ValueError):
        plan(Outcome.TEST_FAILURE, severity=severity, max_risk=max_risk)


def test_invalid_budget_rejected() -> None:
    for amount in (Decimal("NaN"), Decimal("-1"), Decimal("Infinity")):
        with pytest.raises(ValueError):
            plan(Outcome.TEST_FAILURE, max_spend_usd=amount)


def test_invalid_history_counts_rejected() -> None:
    with pytest.raises(ValueError):
        plan(Outcome.TEST_FAILURE, history={"bad": (-1, 0)})


def test_cli_emits_complete_matrix(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["aurex.remediation", "--matrix"])
    main()
    data = json.loads(capsys.readouterr().out)
    assert len(data) == len(Outcome)
    assert all(row["execution"] == "PROPOSE_ONLY_NOT_EXECUTED" for row in data)


def test_catalog_followup_contracts_remain_complete() -> None:
    assert all(x.fix and x.verification and x.rollback for x in CATALOG)
    assert set(FOLLOW_UPS) == set(ActionOutcome)
    assert {r.outcome for r in CATALOG} == set(Outcome) - {Outcome.HEALTHY, Outcome.UNKNOWN}
