from aurex.sovereign_studio import (
    MarketingClaim,
    create_campaign_draft,
    evaluate_launch_readiness,
)


def test_create_campaign_draft_default_draft() -> None:
    claim = MarketingClaim(
        claim_id="c-001",
        statement="130 automated tests pass on release candidate.",
        evidence_id="ev-130",
        verification_status="VERIFIED",
    )
    draft = create_campaign_draft(
        campaign_id="camp-01",
        brand="AUREX",
        title="AUREX Mainline Release",
        content="We are pleased to announce the AUREX release candidate.",
        claims=[claim],
    )
    assert draft.approval_status == "DRAFT"
    assert draft.brand == "AUREX"
    assert len(draft.claims) == 1
    assert draft.claims[0].verification_status == "VERIFIED"


def test_evaluate_launch_readiness_admit() -> None:
    report = evaluate_launch_readiness(
        studio_id="studio-01",
        release_sha="a" * 40,
        engineering_pass=True,
        intelligence_pass=True,
        growth_pass=True,
    )
    assert report.final_readiness == "ADMIT"
    assert report.engineering_status == "PASS"


def test_evaluate_launch_readiness_hold() -> None:
    report = evaluate_launch_readiness(
        studio_id="studio-02",
        release_sha="b" * 40,
        engineering_pass=True,
        intelligence_pass=False,
        growth_pass=True,
    )
    assert report.final_readiness == "HOLD"
    assert report.intelligence_status == "HOLD"
