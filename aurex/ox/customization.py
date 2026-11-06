"""Synthetic customization contracts. No training run and no weight download starts here."""

from __future__ import annotations

METHODS = ("prompt", "tools", "rag", "quantization", "lora", "fine_tune", "package")


class CustomizationError(ValueError):
    """The customization request is not allowed."""


def customization_contract(method: str, *, tenant_id: str, base_entry_id: str) -> dict[str, object]:
    """Record a proposed method. Fine-tuning stays prohibited in this operation."""
    if method not in METHODS:
        raise CustomizationError("unknown customization method")
    if not tenant_id or not base_entry_id:
        raise CustomizationError("tenant and base model are required")
    return {
        "schema": "aurex.ox.customization.v1",
        "tenant_id": tenant_id,
        "base_entry_id": base_entry_id,
        "method": method,
        "dataset": "SYNTHETIC_ONLY",
        "weights_downloaded": False,
        "training_started": False,
        "deployed": False,
        "financial_authority": "NONE",
        "paid_inference": "OFF",
        "rollback_ref": None,
        "approval_state": "PROPOSED",
    }


def promotion_decision(
    *,
    actor: str,
    evaluation_verified_by_other_party: bool,
    method: str,
) -> dict[str, object]:
    """A model actor cannot promote itself, and this operation does not start training."""
    if method not in METHODS:
        raise CustomizationError("unknown customization method")
    allowed = actor == "HUMAN" and evaluation_verified_by_other_party and method != "fine_tune"
    return {
        "actor": actor,
        "method": method,
        "promoted": False,
        "deployed": False,
        "training_started": False,
        "weights_downloaded": False,
        "eligible_for_synthetic_config": allowed,
        "approval_state": "CANDIDATE" if not allowed else "SYNTHETIC_CONFIG_ONLY",
        "financial_authority": "NONE",
    }
