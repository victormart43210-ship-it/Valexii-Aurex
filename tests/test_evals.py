from aurex.evals.paired import relative_uplift


def test_relative_uplift() -> None:
    assert relative_uplift(0.40, 0.46) == 0.15


def test_zero_baseline_is_not_claimed() -> None:
    assert relative_uplift(0.0, 0.2) is None
