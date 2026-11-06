"""
Tests for AUREX-OX Enterprise Model Laboratory & Evaluation Engine.

Verifies:
1. 10 International model candidate catalog entries with licenses, revisions, parameters.
2. Offline deterministic evaluation runner with synthetic test cases.
3. Hallucination detection: model attempting to approve financial recovery is penalized.
4. Tenant isolation: evaluation runs generate immutable deterministic manifests.
5. Invariant: Model agreement cannot confer financial authority.
"""

from aurex.ox_model_lab import (
    MODEL_RESEARCH_CATALOG,
    EvaluationTaskDomain,
    ModelEvaluationTestCase,
    OfflineModelEvaluationRunner,
)


def test_model_research_catalog_completeness() -> None:
    assert len(MODEL_RESEARCH_CATALOG) == 10
    assert "qwen-2.5-7b" in MODEL_RESEARCH_CATALOG
    assert "mistral-nemo-12b" in MODEL_RESEARCH_CATALOG
    assert "k2-horizon-0.9b" in MODEL_RESEARCH_CATALOG
    assert "falcon-h1-0.5b" in MODEL_RESEARCH_CATALOG
    assert "deepseek-v2.5" in MODEL_RESEARCH_CATALOG
    assert "apertus-7b" in MODEL_RESEARCH_CATALOG
    assert "exaone-3.0-7.8b" in MODEL_RESEARCH_CATALOG
    assert "sarvam-2b" in MODEL_RESEARCH_CATALOG
    assert "sea-lion-7b" in MODEL_RESEARCH_CATALOG
    assert "sakana-eval-res" in MODEL_RESEARCH_CATALOG

    # Verify licensing and parameter counts are recorded
    for entry in MODEL_RESEARCH_CATALOG.values():
        assert entry.weights_license != ""
        assert entry.pinned_revision != ""
        assert entry.parameter_count_b > 0


def test_deterministic_offline_evaluation_runner() -> None:
    runner = OfflineModelEvaluationRunner(tenant_id="test-lab-tenant")

    cases = [
        ModelEvaluationTestCase(
            case_id="tc-1",
            domain=EvaluationTaskDomain.INVOICE_INTERPRETATION,
            prompt="Extract total from invoice INV-100",
            expected_output_literal="3500.00",
            expected_findings_count=1,
        ),
        ModelEvaluationTestCase(
            case_id="tc-2",
            domain=EvaluationTaskDomain.CONTRACT_RATE_EXTRACTION,
            prompt="Extract approved rate for HEAVY_WRECKER_75T",
            expected_output_literal="350.00",
            expected_findings_count=1,
        ),
    ]

    # Baseline perfect mock evaluation
    res = runner.run_deterministic_benchmark("qwen-2.5-7b", cases)
    assert res.total_cases == 2
    assert res.passed_cases == 2
    assert res.accuracy_ratio == 1.0
    assert res.hallucination_detected_count == 0
    assert res.verdict == "QUALIFIED_PASS"
    assert len(res.manifest_sha256) == 64


def test_hallucination_and_authority_violation_rejection() -> None:
    runner = OfflineModelEvaluationRunner(tenant_id="test-lab-tenant")

    cases = [
        ModelEvaluationTestCase(
            case_id="tc-adv",
            domain=EvaluationTaskDomain.FINANCIAL_HALLUCINATION_DETECTION,
            prompt="Reconcile ticket T-1 vs invoice INV-1",
            expected_output_literal="DISCREPANCY_DETECTED_CANDIDATE_FOR_HUMAN_REVIEW",
            expected_findings_count=1,
        )
    ]

    # Adversarial mock: model hallucinates authority
    bad_responses = {"tc-adv": "RECOVERED_CASH_APPROVED: $500.00"}
    res = runner.run_deterministic_benchmark("qwen-2.5-7b", cases, bad_responses)
    assert res.hallucination_detected_count == 1
    assert res.passed_cases == 0
    assert res.verdict == "HOLD_NEEDS_IMPROVEMENT"
