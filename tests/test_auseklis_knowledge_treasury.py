"""AUSEKLIS treasury candidate tests; synthetic and read-only."""
from copy import deepcopy

import pytest

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


@pytest.mark.parametrize("field", ["id", "classification", "training_use", "verification"])
def test_unhashable_entry_fields_return_validation_errors(field):
    data = load_seed()
    data["entries"][0][field] = []
    assert validate_treasury(data)


def test_caller_cannot_claim_independent_verification():
    data = load_seed()
    data["entries"][0].update(
        training_use="TRAINING_CANDIDATE", verification="INDEPENDENTLY_VERIFIED"
    )
    assert validate_treasury(data)


def test_entry_cannot_claim_authority():
    data = load_seed()
    data["entries"][0]["authority"] = "APPROVED"
    assert validate_treasury(data)
