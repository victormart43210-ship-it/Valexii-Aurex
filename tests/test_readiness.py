"""Readiness must never promote unverified or stale evidence."""
from datetime import datetime, timedelta, timezone

import pytest

from aurex.readiness import WEIGHTS, evaluate

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)


def entry(key: str, *, status: str = "PASS", independent: bool = True, days: int = 0) -> dict:
    return {
        "id": key,
        "status": status,
        "source": "independent CI witness: exact-SHA example",
        "observed_at": (NOW - timedelta(days=days)).isoformat(),
        "independent": independent,
    }


def test_unknown_is_hold() -> None:
    result = evaluate({"checks": []}, now=NOW)
    assert result.score == 0
    assert result.authority == "HOLD"
    assert not result.eligible_for_90


def test_all_independent_fresh_evidence_reaches_100_but_not_release() -> None:
    result = evaluate({"checks": [entry(key) for key in WEIGHTS]}, now=NOW)
    assert result.score == 100
    assert result.eligible_for_90
    assert result.authority == "CANDIDATE_REVIEW_ONLY"


def test_unverified_critical_prevents_90() -> None:
    checks = [entry(key) for key in WEIGHTS]
    for item in checks:
        if item["id"] == "end_to_end_proof":
            item["status"] = "NOT VERIFIED"
    result = evaluate({"checks": checks}, now=NOW)
    assert result.score == 86
    assert result.authority == "HOLD"


@pytest.mark.parametrize("days,independent", [(8, True), (0, False)])
def test_stale_or_self_attested_evidence_does_not_count(days: int, independent: bool) -> None:
    result = evaluate({"checks": [entry(key, days=days, independent=independent) for key in WEIGHTS]}, now=NOW)
    assert result.score == 0


def test_duplicate_check_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        evaluate({"checks": [entry("backend_auth"), entry("backend_auth")]}, now=NOW)


def test_missing_witness_rejected() -> None:
    with pytest.raises(ValueError, match="source"):
        evaluate({"checks": [{"id": "backend_auth", "status": "PASS"}]}, now=NOW)
