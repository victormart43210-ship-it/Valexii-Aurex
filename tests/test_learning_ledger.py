from aurex.learning_ledger import CorrectionStatus, GovernedLearningLedger


def test_learning_ledger_quarantine() -> None:
    ledger = GovernedLearningLedger()
    entry = ledger.submit_correction(
        correction_id="corr-101",
        audit_id="audit-904",
        original="Driver qualification missing",
        human_fix="Driver CDL uploaded and verified manually",
    )

    assert entry.status == CorrectionStatus.QUARANTINED
    assert ledger.can_apply_to_production("corr-101") is False


def test_learning_ledger_prohibits_auto_modification() -> None:
    ledger = GovernedLearningLedger()
    ledger.submit_correction(
        correction_id="corr-102",
        audit_id="audit-905",
        original="Vehicle inspection expired",
        human_fix="Inspection receipt verified",
    )

    # Autonomous production prompt/weight modification is prohibited
    assert ledger.can_apply_to_production("corr-102") is False
