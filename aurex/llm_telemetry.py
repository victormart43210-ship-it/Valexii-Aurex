"""Privacy-bounded, transport-neutral telemetry for *actually observed* work.

No data collection, OTel exporter, GPU job, LLM training, or public endpoint.
Caller-supplied events are *unqualified* until independently admitted. Only
allowlisted numeric measurements and SHA identities can be represented; raw
prompts, weights, tokens and secrets cannot be serialized through this schema.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta

_SHA = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,63}$")
_KIND = {"backend", "model_training", "model_evaluation", "model_inference", "test_job"}
_PHASE = {"STARTED", "PROGRESS", "COMPLETED", "FAILED", "HOLD"}
_METRIC_RANGES: dict[str, tuple[float, float]] = {
    "train_loss": (0.0, 1e7),
    "eval_loss": (0.0, 1e7),
    "evaluation_accuracy": (0.0, 1.0),
    "tokens_processed": (0.0, 1e12),
    "tokens_generated": (0.0, 1e12),
    "latency_ms": (0.0, 8.64e7),
    "gpu_memory_mb": (0.0, 1e9),
    "cpu_percent": (0.0, 100.0),
    "gpu_percent": (0.0, 100.0),
}
_COUNT_METRICS = {"tokens_processed", "tokens_generated"}


@dataclass(frozen=True, slots=True)
class ObservedEvent:
    run_id: str
    event_index: int
    kind: str
    phase: str
    observed_at: datetime
    evidence_sha256: str
    model_sha256: str | None = None
    dataset_sha256: str | None = None
    training_step: int | None = None
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TelemetrySummary:
    run_id: str | None
    status: str
    observed_events: int
    latest_phase: str | None
    latest_metrics: dict[str, float]
    last_observed_at: str | None
    stream_sha256: str | None
    model_sha256: str | None
    dataset_sha256: str | None
    independent_verification: str = "NOT VERIFIED"
    authority: str = "NONE"
    safe_for_public_surface: bool = False


def _valid_sha(sha: str | None) -> bool:
    return isinstance(sha, str) and _SHA.fullmatch(sha) is not None


def _validate(event: ObservedEvent, now: datetime) -> None:
    if (
        not isinstance(event, ObservedEvent)
        or not isinstance(event.run_id, str)
        or not _ID.fullmatch(event.run_id)
        or isinstance(event.event_index, bool)
        or not isinstance(event.event_index, int)
        or event.event_index < 0
        or not isinstance(event.kind, str) or event.kind not in _KIND
        or not isinstance(event.phase, str) or event.phase not in _PHASE
        or not isinstance(event.observed_at, datetime)
        or event.observed_at.tzinfo is None
        or event.observed_at.utcoffset() is None
        or event.observed_at > now + timedelta(seconds=5)
        or not _valid_sha(event.evidence_sha256)
    ):
        raise ValueError("unqualified event identity, type, clock or provenance")
    if event.kind.startswith("model_") and (
        not _valid_sha(event.model_sha256)
        or (event.kind != "model_inference" and not _valid_sha(event.dataset_sha256))
    ):
        raise ValueError("model and dataset identity required")
    if event.model_sha256 is not None and not _valid_sha(event.model_sha256):
        raise ValueError("invalid model digest")
    if event.dataset_sha256 is not None and not _valid_sha(event.dataset_sha256):
        raise ValueError("invalid dataset digest")
    if (
        event.training_step is not None
        and (isinstance(event.training_step, bool)
             or not isinstance(event.training_step, int)
             or not 0 <= event.training_step <= 10_000_000)
    ):
        raise ValueError("invalid training step")
    if event.training_step is not None and event.kind != "model_training":
        raise ValueError("training step on non-training event")
    if not isinstance(event.metrics, dict) or len(event.metrics) > len(_METRIC_RANGES):
        raise ValueError("invalid or oversized metrics object")
    for key, value in event.metrics.items():
        bounds = _METRIC_RANGES.get(key)
        if (
            bounds is None or not isinstance(value, (float, int))
            or isinstance(value, bool) or not math.isfinite(value)
            or not bounds[0] <= value <= bounds[1]
            or (key in _COUNT_METRICS and not float(value).is_integer())
        ):
            raise ValueError("metric name, type, units or bounds invalid")
    if event.phase == "STARTED" and event.metrics:
        raise ValueError("STARTED cannot report completed measurements")


def summarize_events(
    events: Sequence[ObservedEvent],
    *,
    now: datetime,
    max_age: timedelta = timedelta(minutes=10),
) -> TelemetrySummary:
    """Render only supplied events; missing metrics stay missing.

    Independent trust, tenant scope, auth, signatures, and time calibration
    are external obligations. No training quality or accuracy is inferred.
    """
    if (
        not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None
        or not isinstance(max_age, timedelta) or max_age <= timedelta(0)
        or max_age > timedelta(days=7)
        or len(events) > 2000
    ):
        raise ValueError("invalid observation window or sequence size")
    if not events:
        return TelemetrySummary(None, "NOT_INSTRUMENTED", 0, None, {}, None, None, None, None)
    run_id = events[0].run_id
    last_index = -1
    last_time: datetime | None = None
    model_sha: str | None = None
    dataset_sha: str | None = None
    kind: str | None = None
    last_metrics: dict[str, float] = {}
    canonical: list[dict[str, object]] = []
    for event in events:
        _validate(event, now)
        if (
            event.run_id != run_id or event.event_index != last_index + 1
            or (last_time is not None and event.observed_at < last_time)
            or (kind is not None and event.kind != kind)
            or (model_sha is not None and event.model_sha256 != model_sha)
            or (dataset_sha is not None and event.dataset_sha256 != dataset_sha)
        ):
            raise ValueError("run/mode mismatch, missing event, out-of-order observation")
        last_index = event.event_index
        last_time = event.observed_at
        kind = event.kind
        model_sha = event.model_sha256
        dataset_sha = event.dataset_sha256
        last_metrics.update(event.metrics)
        canonical.append({
            "run": run_id, "index": event.event_index,
            "kind": event.kind, "phase": event.phase,
            "observed_at": event.observed_at.isoformat(),
            "evidence_sha256": event.evidence_sha256,
            "model_sha256": model_sha, "dataset_sha256": dataset_sha,
            "step": event.training_step,
            "metrics": sorted(event.metrics.items()),
        })
    assert last_time is not None
    state = (
        "STALE_HOLD" if now - last_time > max_age
        else "OBSERVED_FAILURE_HOLD" if events[-1].phase in {"FAILED", "HOLD"}
        else "OBSERVED_NOT_VERIFIED"
    )
    fingerprint = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return TelemetrySummary(
        run_id, state, len(events), events[-1].phase,
        last_metrics, last_time.isoformat(), fingerprint, model_sha, dataset_sha,
    )
