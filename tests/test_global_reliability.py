from aurex.global_reliability import evaluate_reliability


def test_reliability_accept() -> None:
    res = evaluate_reliability(conformal_score=0.95, distribution_shift=False)
    assert res.decision == "ACCEPT"
    assert res.abstained is False


def test_reliability_abstain_on_shift() -> None:
    res = evaluate_reliability(conformal_score=0.95, distribution_shift=True)
    assert res.decision == "ABSTAIN"
    assert res.abstained is True


def test_reliability_reject_on_low_conformal() -> None:
    res = evaluate_reliability(conformal_score=0.1, distribution_shift=False)
    assert res.decision == "REJECT"
