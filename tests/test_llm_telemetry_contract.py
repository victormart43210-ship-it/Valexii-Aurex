"""Regression tests for zero-fabrication AUREX model/worker telemetry."""

from datetime import UTC, datetime, timedelta

import pytest

from aurex.llm_telemetry import ObservedEvent, summarize_events

NOW = datetime(2026, 10, 16, 23, 30, tzinfo=UTC)
EVIDENCE = "a" * 64
MODEL = "b" * 64
DATA = "c" * 64


def event(
    idx: int,
    *,
    minutes_ago: int = 1,
    phase: str = "PROGRESS",
    metrics: dict[str, float] | None = None,
    kind: str = "model_training",
) -> ObservedEvent:
    return ObservedEvent(
        run_id="run-example", event_index=idx, kind=kind,
        phase=phase, observed_at=NOW - timedelta(minutes=minutes_ago),
        evidence_sha256=EVIDENCE, model_sha256=MODEL,
        dataset_sha256=DATA, training_step=idx if kind == "model_training" else None,
        metrics=metrics or {},
    )


def test_empty_stream_is_not_instrumented() -> None:
    r = summarize_events((), now=NOW)
    assert r.status == "NOT_INSTRUMENTED"
    assert not r.latest_metrics
    assert r.safe_for_public_surface is False


def test_actual_model_metrics_represent_only_observations() -> None:
    rows = (
        event(0, minutes_ago=5, phase="STARTED"),
        event(1, minutes_ago=2, metrics={"train_loss": 1.5, "tokens_processed": 100}),
        event(2, minutes_ago=1, phase="COMPLETED", metrics={"train_loss": 1.2}),
    )
    report = summarize_events(rows, now=NOW)
    assert report.observed_events == 3
    assert report.latest_metrics == {"train_loss": 1.2, "tokens_processed": 100}
    assert "eval_loss" not in report.latest_metrics
    assert report.stream_sha256 == summarize_events(rows, now=NOW).stream_sha256
    assert report.independent_verification == "NOT VERIFIED"
    assert report.authority == "NONE"
    assert report.status == "OBSERVED_NOT_VERIFIED"
    assert not report.safe_for_public_surface


def test_stale_and_failed_operations_demote_to_hold() -> None:
    stale = summarize_events((event(0, minutes_ago=22),), now=NOW)
    assert stale.status == "STALE_HOLD"
    failure = summarize_events((event(0, phase="FAILED"),), now=NOW)
    assert failure.status == "OBSERVED_FAILURE_HOLD"


def test_gapped_or_unordered_events_fail_closed() -> None:
    with pytest.raises(ValueError):
        summarize_events((event(1),), now=NOW)
    with pytest.raises(ValueError):
        summarize_events((event(0), event(2)), now=NOW)
    with pytest.raises(ValueError):
        summarize_events((event(0, minutes_ago=1), event(1, minutes_ago=4)), now=NOW)


def test_mixed_run_model_or_kind_is_rejected() -> None:
    other = ObservedEvent(
        "other-run", 1, "model_training", "PROGRESS", NOW,
        EVIDENCE, MODEL, DATA, 1, {"train_loss": 0.5}
    )
    with pytest.raises(ValueError):
        summarize_events((event(0), other), now=NOW)
    wrong_model = ObservedEvent(
        "run-example", 1, "model_training", "PROGRESS", NOW,
        EVIDENCE, DATA, DATA, 1, {}
    )
    with pytest.raises(ValueError):
        summarize_events((event(0), wrong_model), now=NOW)
    wrong_kind = ObservedEvent(
        "run-example", 1, "backend", "PROGRESS", NOW, EVIDENCE
    )
    with pytest.raises(ValueError):
        summarize_events((event(0), wrong_kind), now=NOW)


@pytest.mark.parametrize("metrics", [
    {"train_loss": float("nan")},
    {"eval_loss": float("inf")},
    {"gpu_percent": 120},
    {"tokens_generated": -1},
    {"tokens_processed": 1.5},
    {"api_key": 42},
    {"sample_text": 1},
    {"latency_ms": True},
])
def test_untrusted_metrics_cannot_be_serialized(metrics: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        summarize_events((event(0, metrics=metrics),), now=NOW)


def test_malformed_event_id_and_metric_container_fail_closed() -> None:
    malformed = ObservedEvent(
        None, 0, "model_training", "PROGRESS", NOW, EVIDENCE, MODEL, DATA, 0, {}
    )
    with pytest.raises(ValueError):
        summarize_events((malformed,), now=NOW)
    bad_metrics = ObservedEvent(
        "run-example", 0, "model_training", "PROGRESS", NOW,
        EVIDENCE, MODEL, DATA, 0, None,
    )
    with pytest.raises(ValueError):
        summarize_events((bad_metrics,), now=NOW)


def test_model_events_require_pinned_model_and_dataset() -> None:
    candidate = ObservedEvent(
        "run-example", 0, "model_training", "PROGRESS", NOW,
        EVIDENCE, model_sha256=None, dataset_sha256=DATA, training_step=1,
    )
    with pytest.raises(ValueError):
        summarize_events((candidate,), now=NOW)


def test_future_clock_and_invalid_start_event_rejected() -> None:
    future = ObservedEvent(
        "run-example", 0, "model_training", "PROGRESS",
        NOW + timedelta(minutes=1), EVIDENCE, MODEL, DATA,
    )
    with pytest.raises(ValueError):
        summarize_events((future,), now=NOW)
    with pytest.raises(ValueError):
        summarize_events(
            (event(0, phase="STARTED", metrics={"train_loss": 1.0}),), now=NOW
        )
