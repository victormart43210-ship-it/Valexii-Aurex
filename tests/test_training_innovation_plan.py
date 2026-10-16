"""No-cost, no-training rehearsal of modern LLM candidate planning."""

from dataclasses import replace
from decimal import Decimal

import pytest

from training.innovation_plan import CandidateRecipe, review_recipe

SHA = "a" * 64
EVAL = "b" * 64
PROV = "c" * 64
REV = "d" * 40


def recipe(**changes: object) -> CandidateRecipe:
    params: dict[str, object] = {
        "recipe_id": "baseline-lora",
        "method": "SFT_LORA",
        "base_model": "Qwen/Qwen2.5-0.5B-Instruct",
        "revision": REV,
        "training_data_sha256": SHA,
        "heldout_data_sha256": EVAL,
        "provenance_sha256": PROV,
        "training_rows": 40,
        "heldout_rows": 16,
        "max_steps": 20,
        "model_license_reviewed": True,
        "data_license_reviewed": True,
        "contamination_reviewed": True,
        "independent_holdout_reserved": True,
    }
    params.update(changes)
    return CandidateRecipe(**params)  # type: ignore[arg-type]


def test_sft_lora_only_proposes_operator_review_never_execution() -> None:
    report = review_recipe(recipe())
    assert report.status == "OPERATOR_REVIEW_REQUIRED_NOT_EXECUTED"
    assert not report.blockers
    assert not report.model_trained
    assert report.benchmark_run is False
    assert report.independent_verification == "NOT VERIFIED"
    assert report.effect_authority == "NONE"


def test_unsafe_defaults_and_paid_gpu_rejected() -> None:
    result = review_recipe(recipe(
        model_license_reviewed=False,
        contamination_reviewed=False,
        hardware="GPU",
        estimated_cost_usd=Decimal("1.23"),
    ))
    assert result.status == "HOLD"
    assert "ZERO_COST_CEILING_NOT_ESTABLISHED" in result.blockers
    assert "INDEPENDENT_EVAL_OR_CONTAMINATION_REVIEW_MISSING" in result.blockers
    assert "GPU_RESOURCE_AND_BUDGET_EVIDENCE_REQUIRED" in result.blockers


def test_dpo_requires_independent_preference_data() -> None:
    result = review_recipe(recipe(method="DPO_LORA"))
    assert "DPO_PREFERENCE_DATA_PROVENANCE_MISSING" in result.blockers
    good = recipe(
        method="DPO_LORA", preference_pairs=80, preference_data_sha256=SHA
    )
    assert review_recipe(good).status == "OPERATOR_REVIEW_REQUIRED_NOT_EXECUTED"


def test_grpo_requires_verifiable_rewards_versions_sandbox_and_gpu() -> None:
    result = review_recipe(recipe(method="ASYNC_GRPO_LORA"))
    assert "GRPO_VERIFIABLE_REWARDS_ISOLATION_AND_VERSIONING_MISSING" in result.blockers
    assert "ASYNC_GRPO_GPU_ENVIRONMENT_NOT_REVIEWED" in result.blockers
    complete = recipe(
        method="ASYNC_GRPO_LORA",
        hardware="GPU",
        resource_evidence_sha256=SHA,
        reward_verifier_sha256=SHA,
        rollout_provenance_sha256=SHA,
        weight_version_policy_sha256=SHA,
        sandbox_policy_sha256=SHA,
    )
    report = review_recipe(complete)
    assert report.status == "OPERATOR_REVIEW_REQUIRED_NOT_EXECUTED"
    assert report.effect_authority == "NONE"


def test_qlora_requires_quantized_gpu_runtime_proof() -> None:
    result = review_recipe(recipe(method="SFT_QLORA"))
    assert result.status == "HOLD"
    assert "QLORA_QUANTIZATION_COMPATIBILITY_NOT_ESTABLISHED" in result.blockers
    assert "QUANTIZATION_RUNTIME_NOT_BENCHMARKED" in result.blockers


def test_latest_python_not_assumed_safe_for_pinned_gpu_stack() -> None:
    report = review_recipe(recipe(python_version="3.15"))
    assert "RUNTIME_DEPENDENCY_COMPATIBILITY_NOT_VERIFIED" in report.blockers


def test_train_eval_overlap_and_unpinned_checkpoint_hold() -> None:
    report = review_recipe(recipe(heldout_data_sha256=SHA, revision="main"))
    assert "TRAIN_AND_HOLDOUT_CANNOT_SHARE_DATASET_DIGEST" in report.blockers
    assert "EXACT_BASE_MODEL_REVISION_REQUIRED" in report.blockers


def test_empty_or_invalid_outcomes_are_not_success() -> None:
    report = review_recipe(recipe(training_rows=0, heldout_rows=0, max_steps=0))
    assert report.status == "HOLD"
    assert "INSUFFICIENT_OR_UNBOUNDED_DATA" in report.blockers
    assert "UNBOUNDED_TRAINING_STEPS" in report.blockers


def test_unknown_method_never_delegates_to_a_trainer() -> None:
    result = review_recipe(replace(recipe(), method="AUTONOMOUS_FREE_GPU"))
    assert result.status == "HOLD"
    assert "INVALID_METHOD_OR_MODEL_ID" in result.blockers


@pytest.mark.parametrize("bad_cost", [Decimal("NaN"), Decimal("Infinity"), Decimal("-1")])
def test_nonfinite_negative_cost_is_a_hard_hold(bad_cost: Decimal) -> None:
    assert "ZERO_COST_CEILING_NOT_ESTABLISHED" in review_recipe(
        recipe(estimated_cost_usd=bad_cost)
    ).blockers
