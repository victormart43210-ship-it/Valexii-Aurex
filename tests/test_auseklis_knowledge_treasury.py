"""AUSEKLIS treasury candidate tests; synthetic and read-only."""
from copy import deepcopy

from aurex.auseklis.knowledge_treasury import load_seed, validate_treasury


def test_seed_is_candidate_only():
    assert validate_treasury(load_seed()) == ()


def test_registry_cannot_mint_authority_or_start_training():
    for key, value in [("authority", "APPROVED"), ("status", "APPROVED"), ("training_started", True), ("external_inference_spend_authorized", True)]:
        data = deepcopy(load_seed())
        data[key] = value
        assert validate_treasury(data), key


def test_duplicate_or_unverified_training_is_rejected():
    data = deepcopy(load_seed())
    data["entries"].append(deepcopy(data["entries"][0]))
    assert any("duplicate" in e for e in validate_treasury(data))
    data = deepcopy(load_seed())
    data["entries"][0]["training_use"] = "TRAINING_CANDIDATE"
    assert any("unverified training" in e for e in validate_treasury(data))


def test_research_framework_cannot_be_promoted_as_skill():
    data = deepcopy(load_seed())
    entry = next(e for e in data["entries"] if e["id"] == "teth-matrix")
    entry["training_use"] = "SKILL_CANDIDATE"
    assert any("research promoted" in e for e in validate_treasury(data))


def test_required_provenance_fields():
    data = deepcopy(load_seed())
    del data["entries"][0]["source"]
    assert any("missing required" in e for e in validate_treasury(data))
