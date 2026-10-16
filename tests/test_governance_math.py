"""Independent fixture checks for VALEXII Helsinki-inspired mathematical baselines.

Tests only use invented local data; these do not verify live probability
calibration, research superiority, or production deployment.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from aurex.governance_math.calibration import (
    Prediction,
    calibration_report,
    temporal_holdout,
)
from aurex.governance_math.information_gain import (
    Probe,
    entropy,
    information_gain,
    rank_next_tests,
)
from aurex.governance_math.optimization import (
    FixStep,
    beta_conservative,
    choose_remediation,
)
from aurex.governance_math.retrieval import Incident, retrieve_incidents
from aurex.governance_math.spine import advise

NOW = datetime(2026, 10, 16, tzinfo=UTC)
SHA = "a" * 64


def case(identifier: str, description: str, group: str) -> Incident:
    return Incident(identifier, description, "remedy-example", SHA, group)


def prediction(
    identifier: str, days: int, probability: float, actual: int, group: str | None = None
) -> Prediction:
    return Prediction(
        identifier, group or identifier, NOW + timedelta(days=days), probability, actual
    )


def fix(
    key: str,
    *,
    group: str | None = None,
    requires: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    risk: int = 1,
    minutes: int = 5,
    impact: float = 10.0,
    reversible: bool = True,
    cost: str = "0",
    problem: str = "TEST_FAILURE",
    admitted: bool = False,
    successes: int = 0,
    failures: int = 0,
) -> FixStep:
    return FixStep(
        key, problem, group or key, (f"Prepare isolated patch {key}",),
        ("Run independent exact-SHA regression",), ("Revert candidate branch",),
        minutes, risk, Decimal(cost), impact, requires, conflicts, reversible,
        successes, failures, admitted,
    )


def probe(
    key: str, sensitivity: float = 1, specificity: float = 1, *, cost: str = "0",
    reviewed: bool = True, risk: int = 1, duration: int = 2,
) -> Probe:
    return Probe(key, sensitivity, specificity, duration, risk, Decimal(cost), reviewed)


def test_retrieval_is_relevant_repeatable_and_only_advisory() -> None:
    docs = (
        case("b", "mypy module import errors in Python", "shared-runner"),
        case("a", "mypy module import errors in Python", "shared-runner"),
        case("c", "SQLite storage unavailable after restart", "database"),
    )
    result = retrieve_incidents("Python mypy import error", docs)
    assert result == retrieve_incidents("Python mypy import error", docs)
    assert len(result) == 1  # Correlated case family counted at most once by default.
    assert result[0].case_id == "a"  # Stable lexical ID tie-break.
    assert result[0].status == "CANDIDATE_ONLY_NOT_VERIFIED"
    assert 0 < result[0].similarity <= 1
    assert retrieve_incidents("wholly unrelated galaxy", docs) == ()


def test_retrieval_can_surface_correlated_cases_without_claiming_independence() -> None:
    docs = (case("a", "type checking failed", "same-source"),
            case("b", "type checking failed", "same-source"))
    assert len(retrieve_incidents("type checking", docs, distinct_lineages=False)) == 2


@pytest.mark.parametrize(
    "records", [
        (case("a", "one", "g"), case("a", "two", "h")),
        (Incident("a", "x", "m", "bad", "g"),),
        (case("a", "X" * 4097, "g"),),
    ],
)
def test_bad_incident_corpus_fails_closed(records: tuple[Incident, ...]) -> None:
    with pytest.raises(ValueError):
        retrieve_incidents("query", records)


def test_retrieval_rejects_bad_limits_and_large_query() -> None:
    with pytest.raises(ValueError):
        retrieve_incidents("q" * 513, ())
    with pytest.raises(ValueError):
        retrieve_incidents("q", (), limit=0)


def test_calibration_perfect_and_imperfect_brier() -> None:
    perfect = (prediction("a", 0, 1.0, 1), prediction("b", 0, 0.0, 0))
    imperfect = (prediction("a", 0, 0.8, 1), prediction("b", 0, 0.2, 0))
    assert calibration_report(perfect).brier == pytest.approx(0.0)
    assert calibration_report(imperfect).brier == pytest.approx(0.04)
    assert calibration_report(imperfect).log_loss > 0
    assert sum(b.count for b in calibration_report(imperfect).reliability) == 2
    assert calibration_report(imperfect).authority == "ANALYSIS_ONLY_NOT_VERIFIED"


def test_group_safe_temporal_holdout_uses_train_prior_only() -> None:
    rows = (
        prediction("a", -5, 0.1, 0),
        prediction("b", -4, 0.9, 1),
        prediction("c", 1, 0.9, 1),
        prediction("d", 2, 0.1, 0),
    )
    report = temporal_holdout(rows, NOW)
    assert report.train_n == 2 and report.holdout_n == 2
    assert report.model.brier == pytest.approx(0.01)
    assert report.prior_only.brier == pytest.approx(0.25)
    assert report.brier_improvement == pytest.approx(0.24)
    assert report.authority == "ANALYSIS_ONLY_NOT_VERIFIED"


def test_temporal_holdout_blocks_duplicate_lineage_leakage() -> None:
    rows = (
        prediction("a", -1, 0.7, 1, "same-evidence"),
        prediction("b", 1, 0.9, 1, "same-evidence"),
    )
    with pytest.raises(ValueError, match="lineage leakage"):
        temporal_holdout(rows, NOW)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.01, 1.01, True])
def test_invalid_probability_rejected(bad: float) -> None:
    with pytest.raises(ValueError):
        calibration_report((prediction("a", 0, bad, 1),))


def test_calibration_requires_labeled_data_and_valid_cutoff() -> None:
    with pytest.raises(ValueError):
        calibration_report(())
    with pytest.raises(ValueError):
        temporal_holdout((prediction("a", 1, 0.5, 1),), NOW)


def test_entropy_and_expected_information_gain() -> None:
    assert entropy(0.5) == pytest.approx(1.0)
    assert entropy(1.0) == 0.0
    useful, outcome_p = information_gain(0.5, 1, 1)
    assert useful == pytest.approx(1.0) and outcome_p == pytest.approx(0.5)
    useless, _ = information_gain(0.5, 0.5, 0.5)
    assert useless == pytest.approx(0.0)
    assert information_gain(0.0, 1, 1)[0] == 0


def test_uncalibrated_paid_and_high_risk_probes_are_not_suggested() -> None:
    result = rank_next_tests(
        0.5,
        (
            probe("safe"),
            probe("uncalibrated", reviewed=False),
            probe("paid", cost="0.01"),
            probe("danger", risk=4),
        ),
    )
    assert [c.probe_id for c in result] == ["safe"]
    assert result[0].status == "ADVISORY_NOT_AUTHORIZED"


def test_more_informative_test_ranked_first() -> None:
    results = rank_next_tests(
        0.5, (probe("weak", 0.65, 0.65), probe("strong", 0.95, 0.95))
    )
    assert results[0].probe_id == "strong"
    assert results[0].information_gain_bits > results[1].information_gain_bits


def test_invalid_and_duplicate_probes_rejected() -> None:
    with pytest.raises(ValueError):
        rank_next_tests(0.5, (probe("bad", float("nan"), 0.5),))
    with pytest.raises(ValueError):
        rank_next_tests(0.5, (probe("a"), probe("a")))


def test_optimization_exact_search_respects_prerequisites_and_cost() -> None:
    options = (
        fix("plan", impact=1),
        fix("patch", requires=("diagnose",), impact=50, group="patch-lineage"),
        fix("diagnose", risk=0, impact=5),
        fix("paid", impact=99, cost="4.99"),
    )
    result = choose_remediation("TEST_FAILURE", options)
    assert result.status == "REVIEW_REQUIRED"
    assert result.proposed is not None
    assert all(s.cost_usd == Decimal("0") for s in result.proposed.steps)
    keys = [s.key for s in result.proposed.steps]
    if "patch" in keys:
        assert keys.index("diagnose") < keys.index("patch")
    assert "paid" not in keys
    assert all(s.verify and s.rollback for s in result.proposed.steps)


def test_optimization_cycle_or_missing_dependency_blocks_candidate() -> None:
    loop = (fix("a", requires=("b",)), fix("b", requires=("a",)))
    assert choose_remediation("TEST_FAILURE", loop).proposed is None
    assert choose_remediation("TEST_FAILURE", (fix("a", requires=("missing",)),)).status.startswith("HOLD")


def test_correlated_fixes_never_multiply_gain() -> None:
    options = (fix("a", group="same"), fix("b", group="same"))
    result = choose_remediation("TEST_FAILURE", options)
    assert result.proposed is not None
    assert len(result.proposed.steps) == 1


def test_mutually_exclusive_actions_never_combined() -> None:
    options = (fix("a", conflicts=("b",)), fix("b"))
    result = choose_remediation("TEST_FAILURE", options)
    assert result.proposed is not None
    assert len(result.proposed.steps) == 1


def test_nonreversible_or_wrong_problem_proposals_never_enter_plan() -> None:
    options = (fix("destructive", reversible=False), fix("wrong", problem="API_FAILURE"))
    result = choose_remediation("TEST_FAILURE", options)
    assert result.status == "HOLD_NO_ADMISSIBLE_REMEDY"
    assert result.proposed is None


def test_invalid_spending_and_actions_fail_closed() -> None:
    with pytest.raises(ValueError):
        choose_remediation("FAIL", (fix("broken", cost="-0.01"),))
    with pytest.raises(ValueError):
        choose_remediation("FAIL", (), max_cost_usd=Decimal("NaN"))
    with pytest.raises(ValueError):
        choose_remediation("", ())


def test_beta_ranking_improves_only_with_admitted_history() -> None:
    assert beta_conservative(50, 0) > beta_conservative(0, 50)
    candidates = (
        fix("admitted", admitted=True, successes=50),
        fix("unadmitted", admitted=False, successes=500),
    )
    result = choose_remediation("TEST_FAILURE", candidates, max_total_risk=1)
    assert result.proposed is not None
    assert result.proposed.steps[0].key == "admitted"
    assert result.authority == "ANALYSIS_ONLY_NO_EFFECT"


def test_spine_puts_reversible_fix_immediately_behind_outcome() -> None:
    result = advise(
        "TEST_FAILURE", "mypy errors on API types",
        incidents=(case("historical-1", "mypy errors on API types", "ledger-a"),),
        fixes=(fix("patch"),),
        probes=(probe("offline-check"),),
        prior=0.5,
    )
    assert result.gate == "REVIEW_REQUIRED"
    assert result.similar_cases[0].case_id == "historical-1"
    assert result.remediation.proposed is not None
    assert result.remediation.proposed.steps[0].fix
    assert result.remediation.proposed.steps[0].verify
    assert result.remediation.proposed.steps[0].rollback
    assert result.test_next[0].probe_id == "offline-check"
    assert result.authority == "ADVISORY_ONLY_NO_EXECUTION"


def test_spine_does_not_pretend_unknown_failure_has_fix() -> None:
    result = advise("UNKNOWN_FAILURE", "completely new failure")
    assert result.gate == "HOLD"
    assert result.remediation.proposed is None
    assert result.test_next == ()
