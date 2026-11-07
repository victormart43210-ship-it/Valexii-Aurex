"""Dry-run-only training modernization review, with zero execution authority.

SFT LoRA/QLoRA, DPO LoRA and asynchronous GRPO LoRA are *candidate recipes*
from publicly documented training research, NOT features activated here.
The actual trainer remains training/train_lora.py with its own --execute gate.
A source's hash, or a bool supplied by the proposer, is NOT signed admission.
No model/dataset download, job launch, GPU allocation, training or cost.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

_SHA64 = re.compile(r"^[0-9a-f]{64}$")
_REV40 = re.compile(r"^[0-9a-f]{40}$")
_METHODS = {"SFT_LORA", "SFT_QLORA", "DPO_LORA", "ASYNC_GRPO_LORA"}
_MAX_MANIFEST_BYTES = 16 * 1024


@dataclass(frozen=True, slots=True)
class CandidateRecipe:
    recipe_id: str
    method: str
    base_model: str
    revision: str
    training_data_sha256: str
    heldout_data_sha256: str
    provenance_sha256: str
    training_rows: int
    heldout_rows: int
    max_steps: int
    python_version: str = "3.12"
    hardware: str = "CPU"
    estimated_cost_usd: Decimal = Decimal("0")
    model_license_reviewed: bool = False
    data_license_reviewed: bool = False
    contamination_reviewed: bool = False
    independent_holdout_reserved: bool = False
    resource_evidence_sha256: str | None = None
    preference_pairs: int = 0
    preference_data_sha256: str | None = None
    reward_verifier_sha256: str | None = None
    rollout_provenance_sha256: str | None = None
    weight_version_policy_sha256: str | None = None
    sandbox_policy_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class TrainingReview:
    status: str
    method: str
    blockers: tuple[str, ...]
    independent_verification: str = "NOT VERIFIED"
    model_trained: bool = False
    benchmark_run: bool = False
    effect_authority: str = "NONE"
    estimated_cost_is_verified: bool = False


def _sha(value: str | None) -> bool:
    return isinstance(value, str) and _SHA64.fullmatch(value) is not None


def review_recipe(spec: CandidateRecipe) -> TrainingReview:
    """Return HOLD or operator-review only; never certify a recipe as ready.

    Source attestations are caller assertions until evidence admission checks
    run independently. Even an empty blockers list never authorizes execution.
    """
    if not isinstance(spec, CandidateRecipe):
        raise ValueError("candidate required")
    issues: list[str] = []
    if (
        not isinstance(spec.method, str) or spec.method not in _METHODS
        or not isinstance(spec.recipe_id, str) or not 0 < len(spec.recipe_id) <= 128
        or not isinstance(spec.base_model, str) or not 0 < len(spec.base_model) <= 256
    ):
        issues.append("INVALID_METHOD_OR_MODEL_ID")
    if not isinstance(spec.revision, str) or _REV40.fullmatch(spec.revision) is None:
        issues.append("EXACT_BASE_MODEL_REVISION_REQUIRED")
    if not all(_sha(s) for s in (
        spec.training_data_sha256, spec.heldout_data_sha256, spec.provenance_sha256
    )):
        issues.append("DATA_PROVENANCE_DIGEST_REQUIRED")
    if spec.training_data_sha256 == spec.heldout_data_sha256:
        issues.append("TRAIN_AND_HOLDOUT_CANNOT_SHARE_DATASET_DIGEST")
    if (
        isinstance(spec.training_rows, bool) or not isinstance(spec.training_rows, int)
        or spec.training_rows < 16 or spec.training_rows > 1_000_000
        or isinstance(spec.heldout_rows, bool) or not isinstance(spec.heldout_rows, int)
        or spec.heldout_rows < 8 or spec.heldout_rows > 1_000_000
    ):
        issues.append("INSUFFICIENT_OR_UNBOUNDED_DATA")
    if (
        isinstance(spec.max_steps, bool) or not isinstance(spec.max_steps, int)
        or not 1 <= spec.max_steps <= 10_000
    ):
        issues.append("UNBOUNDED_TRAINING_STEPS")
    if (
        not isinstance(spec.estimated_cost_usd, Decimal)
        or not spec.estimated_cost_usd.is_finite()
        or spec.estimated_cost_usd != Decimal("0")
    ):
        issues.append("ZERO_COST_CEILING_NOT_ESTABLISHED")
    if any(
        type(flag) is not bool
        for flag in (
            spec.model_license_reviewed, spec.data_license_reviewed,
            spec.contamination_reviewed, spec.independent_holdout_reserved,
        )
    ):
        issues.append("INVALID_DECLARATION_TYPES")
    if spec.model_license_reviewed is not True or spec.data_license_reviewed is not True:
        issues.append("COMMERCIAL_LICENSING_REVIEW_MISSING")
    if spec.contamination_reviewed is not True or spec.independent_holdout_reserved is not True:
        issues.append("INDEPENDENT_EVAL_OR_CONTAMINATION_REVIEW_MISSING")
    if spec.python_version != "3.12":
        # New Python 3.15 cannot be claimed compatible with old GPU libs or
        # pinned Transformers/PEFT on the strength of a language release alone.
        issues.append("RUNTIME_DEPENDENCY_COMPATIBILITY_NOT_VERIFIED")
    if spec.hardware not in {"CPU", "GPU"}:
        issues.append("INVALID_HARDWARE")
    if spec.hardware == "GPU" and not _sha(spec.resource_evidence_sha256):
        issues.append("GPU_RESOURCE_AND_BUDGET_EVIDENCE_REQUIRED")
    if spec.method == "SFT_QLORA":
        if spec.hardware != "GPU":
            issues.append("QLORA_QUANTIZATION_COMPATIBILITY_NOT_ESTABLISHED")
        if not _sha(spec.resource_evidence_sha256):
            issues.append("QUANTIZATION_RUNTIME_NOT_BENCHMARKED")
    if spec.method == "DPO_LORA":
        if (
            isinstance(spec.preference_pairs, bool)
            or not isinstance(spec.preference_pairs, int)
            or spec.preference_pairs < 16
            or not _sha(spec.preference_data_sha256)
        ):
            issues.append("DPO_PREFERENCE_DATA_PROVENANCE_MISSING")
    if spec.method == "ASYNC_GRPO_LORA":
        if not all(_sha(s) for s in (
            spec.reward_verifier_sha256,
            spec.rollout_provenance_sha256,
            spec.weight_version_policy_sha256,
            spec.sandbox_policy_sha256,
        )):
            issues.append("GRPO_VERIFIABLE_REWARDS_ISOLATION_AND_VERSIONING_MISSING")
        if spec.hardware != "GPU":
            issues.append("ASYNC_GRPO_GPU_ENVIRONMENT_NOT_REVIEWED")
    return TrainingReview(
        "HOLD" if issues else "OPERATOR_REVIEW_REQUIRED_NOT_EXECUTED",
        spec.method,
        tuple(issues),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AUREX no-execution training research gate")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    path: Path = args.input
    if path.is_symlink() or not path.is_file() or path.stat().st_size > _MAX_MANIFEST_BYTES:
        parser.error("missing, linked or oversized proposal JSON")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        parser.error("proposal must be a JSON object")
    fields = set(CandidateRecipe.__dataclass_fields__)
    if not set(raw) <= fields:
        parser.error("unknown training proposal fields")
    if "estimated_cost_usd" in raw:
        if not isinstance(raw["estimated_cost_usd"], str):
            parser.error("estimated_cost_usd must be a decimal string")
        try:
            raw["estimated_cost_usd"] = Decimal(raw["estimated_cost_usd"])
        except Exception:
            parser.error("invalid decimal cost string")
    try:
        spec = CandidateRecipe(**raw)
        review = review_recipe(spec)
    except (TypeError, ValueError):
        parser.error("invalid training proposal")
    print(json.dumps({
        "status": review.status,
        "method": review.method,
        "blockers": review.blockers,
        "independent_verification": review.independent_verification,
        "model_trained": False,
        "benchmark_run": False,
        "effect_authority": "NONE",
    }, indent=2))


if __name__ == "__main__":
    main()
