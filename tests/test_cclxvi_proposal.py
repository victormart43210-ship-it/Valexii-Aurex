"""Observation proposals stay advisory."""

from datetime import UTC, datetime, timedelta

from aurex.ascendancy.proposal import propose


def _observation(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "schema": "aurex.observation.v1",
        "source_sha256": "ab" * 32,
        "observed_at": datetime(2026, 11, 6, 22, 0, tzinfo=UTC),
        "hypothesis": "The stored receipt matches the live report.",
        "counterevidence": ["The same agent produced both readings."],
        "effect": "NONE",
    }
    body.update(overrides)
    return body


def test_a_contested_observation_is_recorded_without_effect() -> None:
    result = propose(
        _observation(),
        now=datetime(2026, 11, 6, 22, 10, tzinfo=UTC),
        max_age=timedelta(hours=1),
    )
    assert result["decision"] == "RECORDED"
    assert result["effect"] == "NONE"
    assert result["authority"] == "NONE"
    assert result["financial_authority"] == "NONE"
    assert result["production"] == "HOLD"
    assert result["launch"] == "NOT_STARTED"
    assert result["independent_verification"] == "NOT_VERIFIED"


def test_missing_counterevidence_abstains() -> None:
    result = propose(
        _observation(counterevidence=[]),
        now=datetime(2026, 11, 6, 22, 10, tzinfo=UTC),
        max_age=timedelta(hours=1),
    )
    assert result["decision"] == "ABSTAIN"
    assert result["effect"] == "NONE"


def test_stale_or_effective_observations_are_refused() -> None:
    now = datetime(2026, 11, 6, 22, 10, tzinfo=UTC)
    stale = propose(
        _observation(observed_at=datetime(2026, 11, 5, tzinfo=UTC)),
        now=now,
        max_age=timedelta(hours=1),
    )
    assert stale["decision"] == "REFUSED"
    assert "STALE_EVIDENCE" in stale["problems"]
    acted = propose(_observation(effect="DEPLOY"), now=now, max_age=timedelta(hours=1))
    assert acted["decision"] == "REFUSED"
    assert acted["effect"] == "NONE"
    assert "EFFECT_REFUSED" in acted["problems"]
