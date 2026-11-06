"""Registry honesty checks: a registry label is not proof of an installed, working runtime."""

from __future__ import annotations

import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "docs/operations/INTERNATIONAL_OPEN_SOURCE_REGISTRY.json"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _load() -> dict:
    return json.loads(REGISTRY.read_text())


def test_every_candidate_has_a_copilot_assurance_record() -> None:
    reg = _load()
    recorded = set(reg["copilot_assurance"]["components"])
    declared = {c["candidate_id"] for c in reg["candidates"]}
    assert declared <= recorded
    for name, rec in reg["copilot_assurance"]["components"].items():
        assert {"installed", "runtime_verification", "commercial_use", "security_limitations"} <= set(rec), name


def test_proposed_components_are_never_reported_as_verified() -> None:
    reg = _load()
    by_id = {c["candidate_id"]: c for c in reg["candidates"]}
    for name, rec in reg["copilot_assurance"]["components"].items():
        candidate = by_id.get(name)
        if candidate and candidate["classification"] == "PROPOSED":
            assert rec["runtime_verification"] == "NOT_VERIFIED", name
            assert not rec["installed"].startswith("YES"), name


def test_placeholder_empty_input_digests_are_called_out() -> None:
    reg = _load()
    for c in reg["candidates"]:
        if EMPTY_SHA256 in c["artifact_or_model_digest"]:
            note = reg["copilot_assurance"]["components"][c["candidate_id"]]["security_limitations"]
            assert "placeholder" in note, c["candidate_id"]


def test_registry_invariants_keep_authority_closed() -> None:
    inv = _load()["invariants"]
    assert inv["financial_authority"] == "NONE" and inv["external_paid_inference"] == "OFF"
    assert inv["model_self_witness"] == "PROHIBITED"
