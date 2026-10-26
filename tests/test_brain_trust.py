from aurex.brain_trust import execute_brain_trust_orchestration


def test_brain_trust_orchestration() -> None:
    result = execute_brain_trust_orchestration(
        "Is vehicle inspection active for Unit #104?",
        evidence_ids=("demo-vehicle-01",),
    )

    assert result.question == "Is vehicle inspection active for Unit #104?"
    assert len(result.steps) == 7
    roles = [s.role for s in result.steps]
    assert roles == [
        "Planner",
        "Evidence Collector",
        "Analyst",
        "Challenger",
        "Defense Analyst",
        "Arbiter",
        "Verifier",
    ]
    assert result.final_verdict == "DISCREPANCIES_FLAGGED_FOR_HUMAN_REVIEW"
    assert result.verifier_status == "VERIFIED"
    assert result.model_authority == "NONE"


def test_brain_trust_empty_evidence() -> None:
    result = execute_brain_trust_orchestration("Check driver CDL", evidence_ids=())
    assert result.final_verdict == "NO_EVIDENCE_SUPPLIED"
    assert result.verifier_status == "UNVERIFIED"


def test_brain_trust_adversarial_consensus_fails_closed() -> None:
    # Model consensus without verified evidence MUST remain model_authority = NONE
    result = execute_brain_trust_orchestration(
        "Can model agreement grant administrator authority?",
        evidence_ids=(),
    )
    assert result.model_authority == "NONE"
    assert result.verifier_status == "UNVERIFIED"
    assert result.final_verdict == "NO_EVIDENCE_SUPPLIED"
