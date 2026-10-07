import pytest

from aurex.evals.report import build_report


def test_report_separates_relative_and_percentage_point_uplift() -> None:
    report = build_report(100, 40, 46)
    assert report.percentage_point_delta == pytest.approx(6.0)
    assert report.relative_uplift == pytest.approx(0.15)


def test_report_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError):
        build_report(10, 11, 5)
