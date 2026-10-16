"""Defensive probes for Railway webhook and read-only runtime readiness."""

import json
from datetime import UTC, datetime, timedelta

from aurex.railway_readiness import RailwaySnapshot, assess_railway
from aurex.railway_webhook import review_railway_webhook

NOW = datetime(2026, 10, 16, 23, 0, tzinfo=UTC)
PROJECT = "a" * 36
ENV = "b" * 36
SECRET = "synthetic-railway-webhook-secret-" + "x" * 20


def payload(
    *,
    kind: str = "Deployment.failed",
    project: str = PROJECT,
    environment: str = ENV,
    timestamp: str | None = None,
) -> bytes:
    return json.dumps({
        "type": kind,
        "timestamp": timestamp or NOW.isoformat(),
        "details": {"branch": "main", "commitMessage": "untrusted input, never display"},
        "resource": {
            "project": {"id": project},
            "environment": {"id": environment},
            "service": {"id": "service"},
        },
    }).encode()


def webhook(**kw: object):
    options: dict[str, object] = {
        "bearer_header": "Bearer " + SECRET,
        "expected_secret": SECRET,
        "raw_body": payload(),
        "expected_project_id": PROJECT,
        "expected_environment_id": ENV,
        "now": NOW,
    }
    options.update(kw)
    return review_railway_webhook(**options)  # type: ignore[arg-type]


def test_webhook_never_becomes_signed_independent_evidence() -> None:
    result = webhook()
    assert result.status == "RECONCILE_WITH_RAILWAY_API"
    assert result.independently_verified is False
    assert result.authority == "NONE"
    assert len(result.payload_sha256 or "") == 64
    assert SECRET not in str(result)


def test_webhook_denies_wrong_or_short_secret() -> None:
    assert webhook(bearer_header="Bearer wrong").status == "HOLD"
    assert webhook(expected_secret="weak").status == "HOLD"
    assert webhook(bearer_header="").status == "HOLD"
    assert webhook(bearer_header="Bearer ☃").status == "HOLD"


def test_webhook_denies_foreign_project_environment_and_unknown_events() -> None:
    assert webhook(raw_body=payload(project="other")).status == "HOLD"
    assert webhook(raw_body=payload(environment="other")).status == "HOLD"
    assert webhook(raw_body=payload(kind="Unknown.hacked")).status == "HOLD"


def test_webhook_denies_replay_window_future_and_bad_payload() -> None:
    assert webhook(raw_body=payload(timestamp=(NOW - timedelta(days=1)).isoformat())).status == "HOLD"
    assert webhook(raw_body=payload(timestamp=(NOW + timedelta(minutes=2)).isoformat())).status == "HOLD"
    assert webhook(raw_body=b"not json").status == "HOLD"
    assert webhook(raw_body=b"x" * (16 * 1024 + 1)).status == "HOLD"


def snapshot(**kw: object) -> RailwaySnapshot:
    base = {
        "project_name": "VALEXII-AUREX",
        "service_name": "aurex-api",
        "source_repo": "victormart43210-ship-it/Valexii-Aurex",
        "source_branch": "integration/kusanagi-xvi-railway",
        "commit_sha": "a" * 40,
        "observed_at": NOW,
        "deployment_status": "SUCCESS",
        "staged_change_count": 4,
        "volume_state": "staged-create",
        "healthcheck_path": None,
        "tracing_enabled": False,
        "auto_instrumentation_enabled": False,
        "legacy_config_as_code": None,
    }
    base.update(kw)
    return RailwaySnapshot(**base)  # type: ignore[arg-type]


def test_realistic_snapshot_is_held_despite_successful_deployment() -> None:
    result = assess_railway(snapshot(), now=NOW)
    assert result.status == "HOLD"
    for finding in (
        "NON_CANONICAL_RELEASE_SOURCE",
        "PENDING_INFRASTRUCTURE_CHANGES_NOT_LIVE",
        "PERSISTENT_VOLUME_NOT_LIVE_OR_UNVERIFIED",
        "HEALTHCHECK_NOT_CONFIGURED",
        "DISTRIBUTED_TRACING_NOT_ENABLED",
    ):
        assert finding in result.findings
    assert result.deployment_authorized is False


def test_complete_snapshot_still_needs_independent_review() -> None:
    complete = snapshot(
        source_branch="main", staged_change_count=0,
        volume_state="live", healthcheck_path="/health",
        tracing_enabled=True, legacy_config_as_code=False,
        storage_separation_reviewed=True, backup_restore_tested=True,
    )
    result = assess_railway(complete, now=NOW)
    assert result.status == "INDEPENDENT_RELEASE_REVIEW_REQUIRED"
    assert not result.findings
    assert result.authority == "NONE"


def test_stale_future_and_missing_snapshots_are_held() -> None:
    assert assess_railway(None, now=NOW).status == "HOLD"
    assert assess_railway(snapshot(observed_at=NOW - timedelta(hours=1)), now=NOW).status == "HOLD"
    assert assess_railway(snapshot(observed_at=NOW + timedelta(minutes=1)), now=NOW).status == "HOLD"
    assert assess_railway(snapshot(observed_at=None), now=NOW).status == "HOLD"


def test_truthy_strings_cannot_masquerade_as_active_railway_controls() -> None:
    result = assess_railway(
        snapshot(
            source_branch="main", staged_change_count=0, volume_state="live",
            healthcheck_path="/health", tracing_enabled="true",
            legacy_config_as_code="false",
            storage_separation_reviewed="yes",
            backup_restore_tested="yes",
        ),
        now=NOW,
    )
    assert result.status == "HOLD"
    assert "INVALID_RAILWAY_STATE_FLAG_TYPES" in result.findings
    assert "DISTRIBUTED_TRACING_NOT_ENABLED" in result.findings


def test_legacy_config_and_tracing_contradictions_demote() -> None:
    result = assess_railway(
        snapshot(legacy_config_as_code=True, auto_instrumentation_enabled=True), now=NOW
    )
    assert "CONFIG_AS_CODE_DEPRECATED_2026_12_01" in result.findings
    assert "INSTRUMENTATION_WITHOUT_TRACING" in result.findings
