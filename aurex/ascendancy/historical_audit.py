"""Read-only audit admission for a future company's historical records.

The mathematical kernel stays company-agnostic. This module does not name a
customer, does not read a filesystem path, and does not accept raw file bytes.
Normalized rows may be audited only when they are explicitly synthetic. An
authorized historical dataset is admitted by digest and then left unprocessed,
because the current engine accepts ``SYNTHETIC_ONLY`` and relabeling real
records would be false.

Jules operation CCXLII had no branch on origin when this file was added. PR #176
already edits the DISPATER engine, store, API, and website, so this gate does
not change those files.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from aurex.dispater_intelligence import RevenueLeakageEngine, digest

_SHA = re.compile(r"^[0-9a-f]{64}$")
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
INVOICE_FIELDS = ("invoice_id", "job_id", "amount", "status")
MAX_DECLARED_BYTES = 1_000_000


class AuditAuthorizationError(PermissionError):
    """The historical source is not admitted."""


def require_authorization(authorization: Mapping[str, Any], now: datetime) -> None:
    """Human, unexpired, and explicit about purpose and privacy. Otherwise refuse."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise AuditAuthorizationError("the decision clock needs a timezone")
    grantor = authorization.get("grantor_kind")
    if grantor != "HUMAN":
        raise AuditAuthorizationError("a human grantor is required")
    expires = authorization.get("expires_at")
    if not isinstance(expires, datetime) or expires.tzinfo is None or expires.utcoffset() is None:
        raise AuditAuthorizationError("expiry needs a timezone")
    real_now = datetime.now(UTC)
    if abs(now - real_now) > timedelta(minutes=2):
        raise AuditAuthorizationError("a caller clock is not a freshness authority")
    if expires <= real_now:
        raise AuditAuthorizationError("authorization is expired")
    if expires - real_now > timedelta(days=7):
        raise AuditAuthorizationError("authorization lifetime is too long")
    if "grantor_verified" in authorization or "authority_verification" in authorization:
        raise AuditAuthorizationError("a caller cannot verify its own authority")
    purpose = authorization.get("purpose")
    privacy = authorization.get("privacy_control")
    if purpose == "SYNTHETIC_VALIDATION" and privacy != "SYNTHETIC_ONLY":
        raise AuditAuthorizationError("synthetic validation stays on synthetic privacy")
    if purpose == "AUTHORIZED_HISTORICAL_REVIEW" and privacy != "READ_ONLY_LOCAL_NO_EXPORT":
        raise AuditAuthorizationError("historical review is read-only and is not exportable")
    if purpose not in {"SYNTHETIC_VALIDATION", "AUTHORIZED_HISTORICAL_REVIEW"}:
        raise AuditAuthorizationError("unknown audit purpose")
    tenant = authorization.get("tenant_id")
    auth_id = authorization.get("authorization_id")
    if not isinstance(tenant, str) or not _TOKEN.fullmatch(tenant):
        raise AuditAuthorizationError("tenant id is not usable")
    if not isinstance(auth_id, str) or not _TOKEN.fullmatch(auth_id):
        raise AuditAuthorizationError("authorization id is not usable")
    reviewer = authorization.get("reviewer_id")
    if not isinstance(reviewer, str) or not _TOKEN.fullmatch(reviewer):
        raise AuditAuthorizationError("a human reviewer id is required")
    if reviewer.casefold() in {"human", "model", "system", "agent"} or reviewer in {auth_id, tenant}:
        raise AuditAuthorizationError("the reviewer id is not an independent person")
    expected_action = {
        "SYNTHETIC_VALIDATION": "SYNTHETIC_AUDIT_READ",
        "AUTHORIZED_HISTORICAL_REVIEW": "HISTORICAL_REVIEW_READ",
    }[str(purpose)]
    if authorization.get("action") != expected_action:
        raise AuditAuthorizationError("the action does not match the purpose")
    scope = authorization.get("scope")
    if not isinstance(scope, str) or not scope.startswith(f"{tenant}:"):
        raise AuditAuthorizationError("the scope is not bound to the tenant")
    if not _TOKEN.fullmatch(scope.removeprefix(f"{tenant}:")):
        raise AuditAuthorizationError("the scope is not bound to the tenant")


def normalize_invoices(
    rows: Sequence[Mapping[str, str]],
    source_headers: Mapping[str, str],
) -> list[dict[str, str]]:
    """Apply a caller-supplied header map. There is no built-in company layout."""
    missing = [field for field in INVOICE_FIELDS if field not in source_headers]
    if missing:
        raise ValueError(f"mapping is missing canonical fields: {missing}")
    headers = [source_headers[field] for field in INVOICE_FIELDS]
    if any(not isinstance(header, str) or not header.strip() or len(header) > 64 for header in headers):
        raise ValueError("each source header must be a short non-empty string")
    if len(set(headers)) != len(headers):
        raise ValueError("two canonical fields cannot share one source header")
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        item: dict[str, str] = {}
        for field in INVOICE_FIELDS:
            header = source_headers[field]
            if header not in row or not isinstance(row[header], str):
                raise ValueError(f"row {index} is missing {header}")
            item[field] = row[header]
        normalized.append(item)
    return normalized


def admitted_byte_length(dataset: Mapping[str, Any]) -> int:
    """UTF-8 length of the canonical normalized rows. This is not a source-file length."""
    raw = json.dumps(dict(dataset), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return len(raw.encode("utf-8"))


def _declared_source(source_sha256: str, byte_length: int, dataset: Mapping[str, Any]) -> None:
    if not isinstance(source_sha256, str) or not _SHA.fullmatch(source_sha256):
        raise AuditAuthorizationError("source digest must be 64 lowercase hex characters")
    if not isinstance(byte_length, int) or isinstance(byte_length, bool) or not 1 <= byte_length <= MAX_DECLARED_BYTES:
        raise AuditAuthorizationError("declared byte length is outside the read-only limit")
    if byte_length != admitted_byte_length(dataset):
        raise AuditAuthorizationError("declared byte length does not match the admitted rows")


def historical_validation_proposal() -> dict[str, object]:
    """A reviewable proposal. It does not open files or run historical rows."""
    return {
        "schema": "aurex.historical_validation.proposal.v1",
        "status": "PROPOSED",
        "activated": False,
        "dataset_role": "private real-company validation dataset",
        "requirements": [
            "human grantor",
            "unexpired authorization",
            "read-only no-export privacy control",
            "caller-supplied header map",
            "digest admission without returning raw rows",
            "engine support that does not relabel historical rows as synthetic",
        ],
        "financial_authority": "NONE",
        "production": "HOLD",
    }


def economic_events(report: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """One event per finding. Exposure is copied, not recalculated."""
    events: list[dict[str, Any]] = []
    for finding in report.get("findings", []):
        events.append(
            {
                "event_id": finding["exposure_event_id"],
                "code": finding["code"],
                "subject": finding["subject"],
                "exposure_usd": finding["exposure_usd"],
                "qualification": finding["qualification"],
                "evidence_sha256": tuple(item["record_sha256"] for item in finding["evidence"]),
                "confirmed_recovery_usd": "0.00",
            }
        )
    return tuple(events)


def run_authorized_audit(
    authorization: Mapping[str, Any],
    now: datetime,
    dataset: Mapping[str, Any],
    *,
    source_sha256: str,
    byte_length: int,
) -> dict[str, Any]:
    """Admit a digest and audit it only when the rows are synthetic.

    ``dataset`` must already be normalized by the caller. Raw bytes and paths
    are not parameters. The returned dossier does not contain the rows.
    """
    require_authorization(authorization, now)
    if not isinstance(dataset, Mapping):
        raise AuditAuthorizationError("normalized rows must be an object")
    _declared_source(source_sha256, byte_length, dataset)
    row_digest = digest(dict(dataset))
    if row_digest != source_sha256:
        raise AuditAuthorizationError("source digest does not match the normalized rows")
    tenant = str(authorization["tenant_id"])
    if dataset.get("tenant_id") != tenant:
        raise AuditAuthorizationError("dataset tenant does not match the authorization")
    base = {
        "authorization_id": authorization["authorization_id"],
        "tenant_id": tenant,
        "source_sha256": source_sha256,
        "byte_length_declared": byte_length,
        "byte_length_verified": False,
        "admitted_row_byte_length_matches": True,
        "byte_length_scope": "NORMALIZED_ROWS_NOT_SOURCE_FILE",
        "source_bytes_status": "SOURCE_BYTES_UNVERIFIED",
        "grantor_verified": False,
        "authority_verification": "UNVERIFIED",
        "reviewer_binding": "TOKEN_NOT_SIGNATURE",
        "synthetic_label_verified": False,
        "dataset_classification_verification": "UNVERIFIED",
        "action": authorization.get("action"),
        "scope": authorization.get("scope"),
        "third_party_contact": "NONE",
        "financial_action": "NONE",
        "read_only": True,
        "export_allowed": False,
        "rows_returned": False,
        "financial_authority": "NONE",
        "production": "HOLD",
        "confirmed_recovery_usd": "0.00",
    }
    purpose = authorization["purpose"]
    dataset_type = dataset.get("dataset_type")
    if purpose == "AUTHORIZED_HISTORICAL_REVIEW" or dataset_type != "SYNTHETIC_ONLY":
        return {
            **base,
            "status": "NOT_PROCESSED",
            "reason": "ENGINE_ADMITS_SYNTHETIC_ONLY",
            "events": (),
        }
    report = RevenueLeakageEngine(tenant).reconcile_records(dict(dataset))
    summary = report["financial_summary"]
    return {
        **base,
        "status": "SYNTHETIC_AUDIT_COMPLETE",
        "reason": "SYNTHETIC_ROWS_AUDITED",
        "financial_summary": summary,
        "events": economic_events(report),
        "confirmed_recovery_usd": summary["confirmed_recovery_usd"],
    }
