"""Adversarial Bayesian evidence fusion tests."""
from datetime import UTC, datetime, timedelta

import pytest

from aurex.bayesian_evidence import fuse

NOW = datetime(2026, 10, 16, tzinfo=UTC)


def observation(identity="a", cluster="independent-A", **overrides):
    item = {
        "id": identity,
        "cluster": cluster,
        "qualification": "PASS",
        "independent": True,
        "status": "OBSERVED",
        "calibration": "INDEPENDENTLY_VALIDATED",
        "observed_at": NOW.isoformat(),
        "p_given_h": 0.8,
        "p_given_not_h": 0.2,
    }
    item.update(overrides)
    return item


def run(items, prior=0.5):
    return fuse({"hypothesis": "contract_is_correct", "prior": prior, "observations": items}, now=NOW)


def test_prior_only_never_promotes_authority():
    result = run([])
    assert result.posterior == 0.5
    assert result.status == "ANALYSIS_ONLY_NOT_AUTHORITY"


def test_single_independent_witness_updates_odds():
    result = run([observation()])
    assert result.posterior == pytest.approx(0.8)
    assert result.independent_clusters == 1


def test_correlated_duplicate_does_not_multiply_confidence():
    result = run([observation(), observation("b")])
    assert result.posterior == pytest.approx(0.8)
    assert result.qualified_witnesses == 2
    assert result.independent_clusters == 1


def test_independent_witness_can_update_twice():
    result = run([observation(), observation("b", "independent-B")])
    assert result.posterior == pytest.approx(16 / 17)


def test_unqualified_or_self_witness_does_not_count():
    result = run([observation(independent=False), observation("b", qualification="NOT VERIFIED")])
    assert result.posterior == 0.5
    assert len(result.rejected) == 2


def test_stale_or_uncalibrated_is_rejected():
    result = run([observation(observed_at=(NOW - timedelta(days=8)).isoformat()),
                  observation("b", calibration="UNVERIFIED")])
    assert result.posterior == 0.5


def test_contradictory_witness_reduces_confidence():
    result = run([observation(p_given_h=0.1, p_given_not_h=0.9)])
    assert result.posterior < 0.5


@pytest.mark.parametrize("prior", [0, 1, float("nan"), float("inf"), -0.1])
def test_invalid_prior_rejected(prior):
    with pytest.raises(ValueError):
        run([], prior=prior)


def test_duplicate_ids_rejected():
    with pytest.raises(ValueError, match="unique"):
        run([observation(), observation()])


def test_weakest_correlated_evidence_wins():
    result = run([observation(), observation("b", p_given_h=0.3, p_given_not_h=0.6)])
    assert result.posterior == pytest.approx(1 / 3)


def test_out_of_range_near_zero_likelihoods_do_not_overflow() -> None:
    result = run([
        observation(
            p_given_h=0.9,
            p_given_not_h=1e-320,
        )
    ])
    assert result.posterior == pytest.approx(10 / 11)
    assert result.status == "ANALYSIS_ONLY_NOT_AUTHORITY"


def test_tiny_ratio_is_stable_and_conservative() -> None:
    result = run([
        observation(p_given_h=1e-320, p_given_not_h=0.9)
    ])
    assert result.posterior == pytest.approx(1 / 11)


def test_missing_or_naive_clock_fails_closed() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        fuse({"hypothesis": "yes", "prior": 0.5, "observations": []}, now=NOW.replace(tzinfo=None))
    with pytest.raises(ValueError, match="timezone-aware"):
        fuse({"hypothesis": "yes", "prior": 0.5, "observations": []}, now="today")


def test_large_numeric_prior_does_not_overflow() -> None:
    with pytest.raises(ValueError):
        run([], prior=10 ** 1000)


def test_unbounded_source_names_are_rejected() -> None:
    with pytest.raises(ValueError, match="hypothesis"):
        fuse({"hypothesis": "x" * 257, "prior": 0.5, "observations": []}, now=NOW)
    with pytest.raises(ValueError, match="unique"):
        run([observation(identity="x" * 129)])
    result = run([observation(cluster="x" * 129)])
    assert result.independent_clusters == 0
    assert "missing_independence_cluster" in result.rejected[0]


def test_declarations_are_not_signed_admission() -> None:
    result = run([observation()])
    assert result.qualified_witnesses == 1
    assert result.status == "ANALYSIS_ONLY_NOT_AUTHORITY"
    assert not hasattr(result, "authorization")
