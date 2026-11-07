"""Synthetic adversarial tests for global research-derived evaluation math.

Passing fixtures do not imply independent real-world verification or deployment.
"""

from datetime import UTC, datetime, timedelta

import pytest

from aurex.evals.anytime_watch import ReviewedOutcome, watch_false_passes
from aurex.evals.behavioral_consensus import ObservedCandidate, group_observed_behaviors
from aurex.evals.conformal_guard import (
    CalibrationCase,
    fit_binary_conformal,
    predict_binary_set,
)
from aurex.evals.holistic_axes import AXES, AxisObservation, summarize_axes
from aurex.evals.research_assurance import review_diagnostics
from aurex.evals.shift_watch import compare_categorical_shift

NOW = datetime(2026, 10, 16, tzinfo=UTC)
RUN = "a" * 64
MODEL = "b" * 64
DATA = "c" * 64
EVIDENCE = "d" * 64


def calibration_case(i: int, *, positive: float = 0.9, label: int = 1) -> CalibrationCase:
    timestamp = NOW - timedelta(days=20 - i)
    return CalibrationCase(
        f"item-{i}", f"independent-group-{i}", RUN, MODEL,
        timestamp, timestamp + timedelta(minutes=1), positive, label,
    )


def good_rows() -> tuple[CalibrationCase, ...]:
    return tuple(calibration_case(i) for i in range(20))


def reviewed(i: int, bad: bool) -> ReviewedOutcome:
    return ReviewedOutcome(
        f"r-{i}", f"lineage-{i}", NOW + timedelta(minutes=i),
        bad, EVIDENCE,
    )


def observed(i: int, outputs: tuple[str, ...]) -> ObservedCandidate:
    return ObservedCandidate(f"candidate-{i}", f"origin-{i}", MODEL, DATA, outputs, EVIDENCE)


def axis(name: str, n: int = 50) -> AxisObservation:
    return AxisObservation(
        name, 0.2 if AXES[name] == "fraction" else 1.5, AXES[name], n, EVIDENCE
    )


def test_split_conformal_high_confidence_returns_label_not_security_pass() -> None:
    fitted = fit_binary_conformal(good_rows(), alpha=0.1, cutoff=NOW + timedelta(days=1))
    assert fitted.calibration_n == 20
    assert fitted.nonconformity_threshold == pytest.approx(0.1)
    assert "NOT_INDEPENDENTLY" in fitted.assumption
    result = predict_binary_set(fitted, 0.95, MODEL)
    assert result.labels == (1,)
    assert result.decision == "CANDIDATE_ONLY"
    assert result.authority == "NOT_A_SECURITY_VERDICT"


def test_split_conformal_abstains_on_ambiguous_or_empty_set() -> None:
    fitted = fit_binary_conformal(good_rows(), alpha=0.1, cutoff=NOW + timedelta(days=1))
    result = predict_binary_set(fitted, 0.5, MODEL)
    assert result.labels == ()
    assert result.decision == "ABSTAIN_HOLD"


def test_too_few_samples_for_requested_error_leads_to_two_label_set() -> None:
    fitted = fit_binary_conformal(
        tuple(calibration_case(i) for i in range(10)),
        alpha=0.01, cutoff=NOW + timedelta(days=1)
    )
    assert fitted.nonconformity_threshold == 1
    result = predict_binary_set(fitted, 0.99, MODEL)
    assert result.labels == (0, 1)
    assert result.decision == "ABSTAIN_HOLD"


def test_conformal_rejects_mixed_models_and_duplicate_lineages() -> None:
    rows = list(good_rows())
    rows[0] = CalibrationCase(
        rows[0].case_id, rows[0].source_group, RUN, DATA,
        rows[0].predicted_at, rows[0].outcome_observed_at,
        0.9, 1
    )
    with pytest.raises(ValueError):
        fit_binary_conformal(rows, alpha=0.1, cutoff=NOW + timedelta(days=1))
    rows = list(good_rows())
    rows[0] = CalibrationCase(
        rows[0].case_id, rows[1].source_group, RUN, MODEL,
        rows[0].predicted_at, rows[0].outcome_observed_at,
        0.9, 1
    )
    with pytest.raises(ValueError):
        fit_binary_conformal(rows, alpha=0.1, cutoff=NOW + timedelta(days=1))


def test_conformal_rejects_hindsight_leakage_and_wrong_model() -> None:
    rows = list(good_rows())
    rows[0] = CalibrationCase(
        rows[0].case_id, rows[0].source_group, RUN, MODEL,
        rows[0].predicted_at, NOW + timedelta(days=2), 0.9, 1
    )
    with pytest.raises(ValueError):
        fit_binary_conformal(rows, alpha=0.1, cutoff=NOW + timedelta(days=1))
    fitted = fit_binary_conformal(good_rows(), alpha=0.1, cutoff=NOW + timedelta(days=1))
    with pytest.raises(ValueError):
        predict_binary_set(fitted, 0.95, DATA)


@pytest.mark.parametrize("bad_alpha", [0, 1, -0.1, 1.1, float("nan"), True])
def test_conformal_rejects_invalid_alpha(bad_alpha: float) -> None:
    with pytest.raises(ValueError):
        fit_binary_conformal(good_rows(), alpha=bad_alpha, cutoff=NOW)


def test_anytime_alarm_on_repeated_verified_false_passes() -> None:
    result = watch_false_passes([reviewed(i, True) for i in range(12)])
    assert result.gate == "REVIEW_EXCESS_FALSE_PASSES"
    assert result.first_crossing_index is not None
    assert result.first_crossing_index <= 12
    assert result.errors == 12
    assert result.authority == "ADVISORY_ONLY_NO_PASS"


def test_anytime_no_signal_is_not_proof_of_safety() -> None:
    result = watch_false_passes([reviewed(i, False) for i in range(25)])
    assert result.gate == "NO_SIGNAL_NOT_PROOF"
    assert result.first_crossing_index is None
    assert result.log_e_final < 0


def test_anytime_zero_factor_remains_defeated() -> None:
    result = watch_false_passes(
        [reviewed(0, False), reviewed(1, True)],
        allowed_error=0.5, stake=2
    )
    assert result.log_e_final == float("-inf")


def test_anytime_invalid_bets_or_duplicate_evidence_fail() -> None:
    with pytest.raises(ValueError):
        watch_false_passes([reviewed(0, True)], allowed_error=0.05, stake=25)
    with pytest.raises(ValueError):
        watch_false_passes([reviewed(0, True), reviewed(0, True)])
    with pytest.raises(ValueError):
        watch_false_passes([reviewed(2, True), reviewed(1, False)])


def test_helm_style_axes_never_manufacture_missing_metrics() -> None:
    result = summarize_axes(MODEL, RUN, DATA, (axis("accuracy"), axis("calibration_brier")))
    assert result.coverage == pytest.approx(0.2)
    assert result.gate == "INCOMPLETE_METRIC_COVERAGE"
    assert "robustness_pass_rate" in result.missing
    assert result.independent_verification == "NOT VERIFIED"


def test_even_complete_holistic_axes_not_certified() -> None:
    result = summarize_axes(MODEL, RUN, DATA, tuple(axis(name) for name in AXES))
    assert not result.missing
    assert result.coverage == 1.0
    assert result.gate == "REVIEW_UNVERIFIED_METRICS"
    assert result.authority == "METRICS_ONLY"


def test_holistic_rejects_fake_scores_bad_units_and_duplicate_metrics() -> None:
    with pytest.raises(ValueError):
        summarize_axes(MODEL, RUN, DATA, (AxisObservation("accuracy", 1.1, "fraction", 5, EVIDENCE),))
    with pytest.raises(ValueError):
        summarize_axes(MODEL, RUN, DATA, (AxisObservation("median_latency_seconds", 1, "fraction", 5, EVIDENCE),))
    with pytest.raises(ValueError):
        summarize_axes(MODEL, RUN, DATA, (axis("accuracy"), axis("accuracy")))


def test_code_behavior_consensus_only_means_observed_agreement() -> None:
    cases = (
        observed(0, ("ok", "error")),
        observed(1, ("ok", "error")),
        observed(2, ("ok", "error")),
        observed(3, ("no", "error")),
    )
    report = group_observed_behaviors(cases, agreement_threshold=0.75)
    assert report.dominant_fraction == 0.75
    assert report.suggested_candidate == "candidate-0"
    assert report.gate == "CONSISTENT_CANDIDATE_REVIEW_REQUIRED"
    assert report.independent_verification == "NOT VERIFIED"
    assert sum(g.count for g in report.clusters) == 4


def test_code_agreement_abstains_when_no_dominant_pattern() -> None:
    cases = (observed(0, ("0",)), observed(1, ("1",)), observed(2, ("2",)))
    report = group_observed_behaviors(cases)
    assert report.suggested_candidate is None
    assert report.gate == "ABSTAIN_HOLD"


def test_behavioral_consensus_blocks_mixed_test_suites_and_correlated_sources() -> None:
    cases = [
        observed(0, ("ok",)),
        ObservedCandidate("candidate-1", "origin-0", MODEL, DATA, ("ok",), EVIDENCE),
    ]
    with pytest.raises(ValueError):
        group_observed_behaviors(cases)
    cases[1] = ObservedCandidate("candidate-1", "origin-1", MODEL, RUN, ("ok",), EVIDENCE)
    with pytest.raises(ValueError):
        group_observed_behaviors(cases)


def test_total_variation_shift_computation_is_exact_and_conservative() -> None:
    result = compare_categorical_shift({"A": 80, "B": 20}, {"A": 20, "B": 80})
    assert result.total_variation == pytest.approx(0.6)
    assert result.gate == "DRIFT_REVIEW_HOLD"
    stable = compare_categorical_shift({"A": 60, "B": 40}, {"A": 60, "B": 40})
    assert stable.gate == "NO_DRIFT_SIGNAL_NOT_PROOF"
    assert stable.authority == "DIAGNOSTIC_ONLY"


def test_shift_handles_unseen_categories_and_rejects_small_samples() -> None:
    result = compare_categorical_shift({"A": 50}, {"B": 50})
    assert result.total_variation == pytest.approx(1)
    with pytest.raises(ValueError):
        compare_categorical_shift({"A": 1}, {"A": 1})
    with pytest.raises(ValueError):
        compare_categorical_shift({"A": 50}, {"A": 50}, review_threshold=float("nan"))


def test_governance_synthesis_demotes_missing_or_adverse_signals() -> None:
    assert review_diagnostics().state == "HOLD"
    fitted = fit_binary_conformal(good_rows(), alpha=0.1, cutoff=NOW + timedelta(days=1))
    binset = predict_binary_set(fitted, 0.95, MODEL)
    sequence = watch_false_passes([reviewed(i, False) for i in range(10)])
    metrics = summarize_axes(MODEL, RUN, DATA, tuple(axis(name) for name in AXES))
    consensus = group_observed_behaviors((observed(0, ("a",)), observed(1, ("a",))))
    shift = compare_categorical_shift({"A": 50}, {"A": 50})
    report = review_diagnostics(
        conformal=binset, sequential=sequence, holistic=metrics,
        behaviors=consensus, shift=shift
    )
    assert report.state == "INDEPENDENT_REVIEW_REQUIRED"
    assert report.signed_independent_admission == "NOT VERIFIED"
    assert report.authority == "NONE"
    assert not report.automatic_execution
    flagged = compare_categorical_shift({"A": 50}, {"B": 50})
    assert review_diagnostics(
        conformal=binset, sequential=sequence, holistic=metrics,
        behaviors=consensus, shift=flagged
    ).state == "HOLD"
