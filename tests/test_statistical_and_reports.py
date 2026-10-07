"""Tests for paired statistical evaluation layer and machine-readable experiment reports."""

from aurex.evals.experiment_report import build_experiment_report
from aurex.evals.statistical import PairedItemOutcome, analyze_paired_outcomes
from aurex.experiments.admission import AdmissionDecision
from aurex.experiments.contracts import ArmSpec, ExperimentManifest, ResultStatus, VerifierSpec
from aurex.experiments.runner import RunReport


def make_manifest() -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="exp-stat-01",
        track="benchmark_lab",
        dataset_revision="v1",
        dataset_sha256="a" * 64,
        protocol_sha256="b" * 64,
        item_ids=("q1", "q2", "q3", "q4"),
        baseline=ArmSpec(arm_id="b1", provider="p", model="m", config_sha256="1" * 64),
        experimental=ArmSpec(arm_id="e1", provider="p", model="m", config_sha256="2" * 64),
        verifier=VerifierSpec(verifier_id="v1", family="f", reference_access="blind"),
        dataset_authorized=True,
        contamination_checked=True,
    )


def test_paired_statistical_analysis_basics() -> None:
    outcomes = (
        PairedItemOutcome(
            item_id="q1", baseline_correct=False, experimental_correct=True
        ),  # improved
        PairedItemOutcome(
            item_id="q2", baseline_correct=True, experimental_correct=True
        ),  # unchanged
        PairedItemOutcome(
            item_id="q3", baseline_correct=False, experimental_correct=False
        ),  # unchanged
        PairedItemOutcome(
            item_id="q4", baseline_correct=True, experimental_correct=False
        ),  # regressed
    )

    stat = analyze_paired_outcomes(outcomes, total_items=5)
    assert stat.total_items == 5
    assert stat.evaluated_items == 4
    assert stat.abstentions == 1
    assert stat.coverage == 0.8
    assert stat.baseline_correct_count == 2
    assert stat.experimental_correct_count == 2
    assert stat.baseline_score == 0.5
    assert stat.experimental_score == 0.5
    assert stat.percentage_point_delta == 0.0
    assert stat.improved_count == 1
    assert stat.regressed_count == 1
    assert stat.unchanged_count == 2
    assert stat.relative_uplift == 0.0


def test_relative_uplift_zero_denominator_handled() -> None:
    outcomes = (PairedItemOutcome(item_id="q1", baseline_correct=False, experimental_correct=True),)
    stat = analyze_paired_outcomes(outcomes)
    assert stat.baseline_score == 0.0
    assert stat.experimental_score == 1.0
    assert stat.percentage_point_delta == 100.0
    assert stat.relative_uplift is None


def test_machine_readable_report_generation() -> None:
    manifest = make_manifest()
    admission = AdmissionDecision(status=ResultStatus.PASS, rationale="All requirements met")
    run_report = RunReport(
        experiment_id=manifest.experiment_id,
        manifest_sha256="m" * 64,
        items=(),
        complete=True,
        run_sha256="r" * 64,
    )

    report = build_experiment_report(
        manifest=manifest,
        manifest_sha256="m" * 64,
        run_report=run_report,
        admission_decision=admission,
    )

    assert report.overall_status == ResultStatus.PASS
    assert report.manifest.experiment_id == "exp-stat-01"
    assert len(report.report_digest) == 64


def test_statistical_edge_cases_and_boundary_conditions() -> None:
    # Edge Case 1: Baseline = 1.0, Experimental = 1.0 (No discordant pairs)
    all_correct = (
        PairedItemOutcome(item_id="q1", baseline_correct=True, experimental_correct=True),
        PairedItemOutcome(item_id="q2", baseline_correct=True, experimental_correct=True),
    )
    stat1 = analyze_paired_outcomes(all_correct)
    assert stat1.baseline_score == 1.0
    assert stat1.experimental_score == 1.0
    assert stat1.percentage_point_delta == 0.0
    assert stat1.relative_uplift == 0.0
    assert stat1.improved_count == 0
    assert stat1.regressed_count == 0
    assert stat1.mcnemar_p_value is None

    # Edge Case 2: All abstentions / empty outcomes
    stat2 = analyze_paired_outcomes((), total_items=10)
    assert stat2.total_items == 10
    assert stat2.evaluated_items == 0
    assert stat2.abstentions == 10
    assert stat2.coverage == 0.0
    assert stat2.relative_uplift is None

    # Edge Case 3: Total regression (1.0 -> 0.0)
    all_regressed = (
        PairedItemOutcome(item_id="q1", baseline_correct=True, experimental_correct=False),
        PairedItemOutcome(item_id="q2", baseline_correct=True, experimental_correct=False),
    )
    stat3 = analyze_paired_outcomes(all_regressed)
    assert stat3.baseline_score == 1.0
    assert stat3.experimental_score == 0.0
    assert stat3.percentage_point_delta == -100.0
    assert stat3.relative_uplift == -1.0
    assert stat3.regressed_count == 2
    assert stat3.improved_count == 0
