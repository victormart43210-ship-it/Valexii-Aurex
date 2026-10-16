"""Read-only Railway deployment readiness: a report, NEVER a deploy command.

Callers supply metadata from describe_environment/describe_service. Missing,
staged and stale state demotes. A green deployment is NOT proof the canonical
backend, storage, signed-evidence controls or frontend contracts work.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_MAX_AGE = timedelta(minutes=30)


@dataclass(frozen=True, slots=True)
class RailwaySnapshot:
    project_name: str
    service_name: str
    source_repo: str
    source_branch: str
    commit_sha: str
    observed_at: datetime
    deployment_status: str
    staged_change_count: int
    volume_state: str
    healthcheck_path: str | None
    tracing_enabled: bool
    auto_instrumentation_enabled: bool
    legacy_config_as_code: bool | None
    storage_separation_reviewed: bool = False
    backup_restore_tested: bool = False


@dataclass(frozen=True, slots=True)
class RailwayAssessment:
    status: str
    findings: tuple[str, ...]
    recommended_order: tuple[str, ...]
    authority: str = "NONE"
    deployment_authorized: bool = False


def assess_railway(
    snapshot: RailwaySnapshot | None,
    *,
    now: datetime,
    canonical_repo: str = "victormart43210-ship-it/Valexii-Aurex",
    expected_release_branch: str = "main",
) -> RailwayAssessment:
    """Gate *readiness for review*; no stage can grant production authority."""
    actions = (
        "VERIFY_CANONICAL_SOURCE_AND_EXACT_SHA",
        "RECONCILE_STAGED_STORAGE_AND_BACKUPS",
        "CONFIRM_HEALTHCHECK_AND_PRIVATE_ACCESS",
        "REVIEW_TRACING_REDACTION_AND_OBSERVABILITY",
        "VERIFY_PRODUCTION_CONTRACTS_BEFORE_DEPLOYMENT",
    )
    findings: list[str] = []
    if (
        not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None
        or not isinstance(snapshot, RailwaySnapshot)
        or snapshot.observed_at.tzinfo is None
        or snapshot.observed_at.utcoffset() is None
        or not now - _MAX_AGE <= snapshot.observed_at <= now + timedelta(seconds=30)
    ):
        return RailwayAssessment("HOLD", ("SNAPSHOT_MISSING_STALE_OR_FUTURE",), actions)
    if snapshot.source_repo != canonical_repo or snapshot.source_branch != expected_release_branch:
        findings.append("NON_CANONICAL_RELEASE_SOURCE")
    if not _SHA40.fullmatch(snapshot.commit_sha):
        findings.append("EXACT_COMMIT_NOT_ESTABLISHED")
    if snapshot.deployment_status != "SUCCESS":
        findings.append("LIVE_DEPLOYMENT_NOT_SUCCESSFUL")
    if (
        isinstance(snapshot.staged_change_count, bool)
        or not isinstance(snapshot.staged_change_count, int)
        or snapshot.staged_change_count < 0
    ):
        findings.append("INVALID_STAGED_CHANGE_COUNT")
    elif snapshot.staged_change_count:
        findings.append("PENDING_INFRASTRUCTURE_CHANGES_NOT_LIVE")
    if snapshot.volume_state != "live":
        findings.append("PERSISTENT_VOLUME_NOT_LIVE_OR_UNVERIFIED")
    if snapshot.healthcheck_path is None or not snapshot.healthcheck_path.startswith("/"):
        findings.append("HEALTHCHECK_NOT_CONFIGURED")
    if not snapshot.tracing_enabled:
        findings.append("DISTRIBUTED_TRACING_NOT_ENABLED")
    if snapshot.auto_instrumentation_enabled and not snapshot.tracing_enabled:
        findings.append("INSTRUMENTATION_WITHOUT_TRACING")
    if snapshot.legacy_config_as_code is True:
        findings.append("CONFIG_AS_CODE_DEPRECATED_2026_12_01")
    elif snapshot.legacy_config_as_code is None:
        findings.append("CONFIG_AS_CODE_USAGE_UNVERIFIED")
    if not snapshot.storage_separation_reviewed:
        findings.append("STATEFUL_SERVICE_DOWNTIME_RISK_UNREVIEWED")
    if not snapshot.backup_restore_tested:
        findings.append("BACKUP_RESTORE_NOT_VERIFIED")
    if not snapshot.project_name or not snapshot.service_name:
        findings.append("SERVICE_IDENTITY_MISSING")
    return RailwayAssessment(
        "HOLD" if findings else "INDEPENDENT_RELEASE_REVIEW_REQUIRED",
        tuple(findings),
        actions,
    )
