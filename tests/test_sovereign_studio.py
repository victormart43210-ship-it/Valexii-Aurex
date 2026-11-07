import json

import pytest

from aurex.sovereign_studio import (
    REQUIRED_GATES,
    Gate,
    assess_launch,
    build_campaign_brief,
    load_gates,
)


def test_empty_launch_is_hold():
    result = assess_launch({})
    assert result["decision"] == "HOLD"
    assert result["automated_release_authority"] == "NONE"


def test_missing_evidence_demotes_pass():
    result = assess_launch({"engineering_tests": Gate("PASS")})
    assert result["gates"]["engineering_tests"]["status"] == "NOT VERIFIED"


def test_all_gates_evidenced_is_review_eligible_not_release():
    result = assess_launch({key: Gate("PASS", "artifact:123") for key in REQUIRED_GATES})
    assert result["decision"] == "REVIEW_ELIGIBLE"
    assert result["automated_release_authority"] == "NONE"


def test_growth_claim_without_evidence_stays_unverified():
    brief = build_campaign_brief(
        product="BCXMET", audience="security-conscious consumers",
        claim="Detects every attack", claim_evidence=Gate("NOT VERIFIED"),
    )
    assert brief["claim_status"] == "UNVERIFIED"
    assert brief["publication_status"] == "DRAFT_ONLY"


def test_growth_evidenced_still_requires_review():
    brief = build_campaign_brief(
        product="AUREX", audience="developers", claim="Test X passed",
        claim_evidence=Gate("PASS", "ci:123"),
    )
    assert brief["claim_status"] == "EVIDENCE_LINKED"
    assert brief["requires_human_review"]


def test_bad_gate_input_rejected(tmp_path):
    file = tmp_path / "gates.json"
    file.write_text(json.dumps({"engineering_tests": {"status": "SAFE"}}))
    with pytest.raises(ValueError):
        load_gates(file)
