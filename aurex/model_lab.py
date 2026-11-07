"""Synthetic model-lab gates. This module does not download weights or start training."""

from __future__ import annotations

import re
from typing import Any

# Names and statuses copied from CCLXIV commit 5d156ab. That branch was not merged.
# None of these rows were re-measured here.
CANDIDATES: tuple[dict[str, Any], ...] = (
    {"name": "Qwen3.5-0.8B", "role": "general_assistant"},
    {"name": "Falcon-H1-1.5B-Instruct", "role": "challenger"},
    {"name": "Granite-4.0-Micro", "role": "compact_inference"},
    {"name": "Ministral-3-3B-Reasoning-2512-GGUF", "role": "reasoning"},
    {"name": "PaddleOCR-VL", "role": "document_ocr"},
    {"name": "DeepSeek-OCR-2", "role": "document_ocr"},
    {"name": "EXAONE-4.0-1.2B", "role": "compact_inference"},
)

_INSTRUCTION = re.compile(
    r"(?i)^\s*(ignore\b.*\binstructions\b|you are now\b|system:|developer:)"
)


def inventory() -> dict[str, Any]:
    rows = [
        {
            **candidate,
            "installed": False,
            "weights_sha256": None,
            "revision": None,
            "benchmark_status": "NOT_RUN",
            "runtime_status": "NOT_VERIFIED",
            "license_status": "REVIEW_REQUIRED",
            "score": None,
        }
        for candidate in CANDIDATES
    ]
    return {
        "schema": "aurex.model_lab.inventory.v1",
        "source_note": "CCLXIV names only. That commit is not an ancestor of this tree.",
        "downloads": "NOT_STARTED",
        "training": "NOT_STARTED",
        "paid_inference": "OFF",
        "candidates": rows,
    }


def training_decision(manifest: dict[str, Any], *, authorized: bool, budget_usd: str) -> dict[str, Any]:
    """Decide whether a job may be launched. This function never launches one."""
    problems: list[str] = []
    if manifest.get("dataset_type") != "SYNTHETIC_ONLY":
        problems.append("CUSTOMER_DATA_PROHIBITED")
    if not manifest.get("base_revision"):
        problems.append("BASE_REVISION_REQUIRED")
    if manifest.get("license_reviewed") is not True:
        problems.append("LICENSE_REVIEW_REQUIRED")
    if set(manifest.get("splits") or []) != {"train", "validation", "test"}:
        problems.append("SPLITS_REQUIRED")
    if manifest.get("leakage_check") != "PASS":
        problems.append("LEAKAGE_CHECK_REQUIRED")
    if budget_usd not in {"0", "0.0", "0.00"}:
        problems.append("PAID_BUDGET_REFUSED")
    if not authorized:
        problems.append("OWNER_AUTHORIZATION_REQUIRED")
    return {
        "decision": "REFUSED" if problems else "READY_NOT_LAUNCHED",
        "launch": "NOT_STARTED",
        "problems": problems,
        "financial_authority": "NONE",
    }


def retrieve(records: list[dict[str, str]], query: str) -> dict[str, Any]:
    """Cite approved records. Instruction lines in a document are not authority."""
    hits: list[dict[str, str]] = []
    for record in records:
        kept = "\n".join(line for line in record.get("text", "").splitlines() if not _INSTRUCTION.match(line))
        if query and query.casefold() in kept.casefold():
            hits.append({"doc_id": record["doc_id"], "sha256": record["sha256"]})
    if not hits:
        return {"status": "ABSTAIN", "citations": [], "authority": "NONE", "instructions_are_not_authority": True}
    return {
        "status": "CITED",
        "citations": hits,
        "authority": "NONE",
        "instructions_are_not_authority": True,
    }
