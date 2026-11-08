"""Read-only validation of AUSEKLIS knowledge treasury candidates.

No training, inference, filesystem mutation, or authority promotion.
"""
from __future__ import annotations

import json
from pathlib import Path

ALLOWED_CLASSIFICATIONS = {"DESIGN", "RESEARCH_FRAMEWORK", "TEST_FRAMEWORK", "SYNTHETIC_TEST_REFERENCE", "VERIFIED_IMPLEMENTATION"}
ALLOWED_USES = {"RESEARCH_ONLY", "SKILL_CANDIDATE", "EVALUATION_CANDIDATE", "TRAINING_CANDIDATE"}
ALLOWED_VERIFICATION = {"NOT_RUN", "REVERIFY_EXACT_SHA", "INDEPENDENTLY_VERIFIED"}
REQUIRED = {"id", "owner", "purpose", "source", "classification", "training_use", "verification"}


def validate_treasury(data: dict) -> tuple[str, ...]:
    errors: list[str] = []
    if data.get("schema") != "valexii.auseklis.knowledge_treasury.v1":
        errors.append("invalid schema")
    if data.get("status") != "CANDIDATE_ONLY" or data.get("authority") != "NONE":
        errors.append("registry cannot confer authority")
    if data.get("training_started") is not False:
        errors.append("training must not start through registry")
    if data.get("external_inference_spend_authorized") is not False:
        errors.append("external spending must stay disabled")
    entries = data.get("entries")
    if not isinstance(entries, list):
        return tuple(errors + ["entries must be a list"])
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} is not an object")
            continue
        if not REQUIRED.issubset(entry):
            errors.append(f"entry {index} missing required fields")
            continue
        if any(not isinstance(entry[k], str) or not entry[k].strip() for k in REQUIRED):
            errors.append(f"entry {index} has empty or invalid fields")
        if entry["id"] in seen:
            errors.append(f"duplicate id: {entry['id']}")
        seen.add(entry["id"])
        if entry["classification"] not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"entry {index} invalid classification")
        if entry["training_use"] not in ALLOWED_USES:
            errors.append(f"entry {index} invalid training use")
        if entry["verification"] not in ALLOWED_VERIFICATION:
            errors.append(f"entry {index} invalid verification")
        if entry["training_use"] == "TRAINING_CANDIDATE" and entry["verification"] != "INDEPENDENTLY_VERIFIED":
            errors.append(f"entry {index} unverified training candidate")
        if entry["classification"] == "RESEARCH_FRAMEWORK" and entry["training_use"] != "RESEARCH_ONLY":
            errors.append(f"entry {index} research promoted to training")
    return tuple(errors)


def load_seed() -> dict:
    path = Path(__file__).resolve().parents[2] / "docs/architecture/auseklis_knowledge_treasury_seed_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))
