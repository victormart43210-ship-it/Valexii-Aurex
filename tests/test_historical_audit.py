"""Authorization, redaction, and onboarding. No company layout is built in."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from aurex.ascendancy.dispater_adapter import synthetic_ledger
from aurex.ascendancy.historical_audit import (
    AuditAuthorizationError,
    admitted_byte_length,
    normalize_invoices,
    run_authorized_audit,
)
from aurex.dispater_intelligence import digest

NOW = datetime(2026, 11, 6, 13, 10, tzinfo=UTC)


def _auth(purpose: str, privacy: str, *, kind: str = "HUMAN", expires: datetime | None = None) -> dict[str, object]:
    return {
        "authorization_id": "auth-1",
        "tenant_id": "tenant-asc",
        "purpose": purpose,
        "privacy_control": privacy,
        "expires_at": NOW + timedelta(days=1) if expires is None else expires,
        "grantor_kind": kind,
        "reviewer_id": "reviewer-1",
    }


def test_models_and_expired_grants_cannot_open_records() -> None:
    dataset = synthetic_ledger()
    source = digest(dataset)
    for kind in ("MODEL", "SYSTEM"):
        try:
            run_authorized_audit(_auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY", kind=kind), NOW, dataset, source_sha256=source, byte_length=admitted_byte_length(dataset))
        except AuditAuthorizationError as exc:
            assert "human" in str(exc)
        else:
            raise AssertionError(kind)
    try:
        run_authorized_audit(
            _auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY", expires=NOW),
            NOW,
            dataset,
            source_sha256=source,
            byte_length=admitted_byte_length(dataset),
        )
    except AuditAuthorizationError as exc:
        assert "expired" in str(exc)
    else:
        raise AssertionError("expired grant")


def test_a_stale_clock_and_a_missing_reviewer_are_refused() -> None:
    dataset = synthetic_ledger()
    source = digest(dataset)
    length = admitted_byte_length(dataset)
    stale = NOW - timedelta(days=30)
    try:
        run_authorized_audit(
            _auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY", expires=stale + timedelta(days=1)),
            stale,
            dataset,
            source_sha256=source,
            byte_length=length,
        )
    except AuditAuthorizationError as exc:
        assert "fresh" in str(exc) or "expired" in str(exc)
    else:
        raise AssertionError("stale clock")
    grant = _auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY")
    del grant["reviewer_id"]
    try:
        run_authorized_audit(grant, NOW, dataset, source_sha256=source, byte_length=length)
    except AuditAuthorizationError as exc:
        assert "reviewer" in str(exc)
    else:
        raise AssertionError("missing reviewer")


def test_historical_rows_are_admitted_by_digest_and_not_processed() -> None:
    dataset = synthetic_ledger()
    dataset["dataset_type"] = "HISTORICAL_LOCAL"
    source = digest(dataset)
    dossier = run_authorized_audit(
        _auth("AUTHORIZED_HISTORICAL_REVIEW", "READ_ONLY_LOCAL_NO_EXPORT"),
        NOW,
        dataset,
        source_sha256=source,
        byte_length=admitted_byte_length(dataset),
    )
    assert dossier["status"] == "NOT_PROCESSED"
    assert dossier["reason"] == "ENGINE_ADMITS_SYNTHETIC_ONLY"
    assert dossier["events"] == ()
    assert dossier["export_allowed"] is False
    assert dossier["rows_returned"] is False
    assert dossier["byte_length_verified"] is True
    assert dossier["byte_length_scope"] == "NORMALIZED_ROWS_NOT_SOURCE_FILE"
    assert dossier["grantor_verified"] is False
    assert dossier["synthetic_label_verified"] is False
    assert "jobs" not in dossier
    assert dossier["confirmed_recovery_usd"] == "0.00"


def test_a_mismatched_digest_is_refused() -> None:
    dataset = synthetic_ledger()
    try:
        run_authorized_audit(
            _auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY"),
            NOW,
            dataset,
            source_sha256="ab" * 32,
            byte_length=admitted_byte_length(dataset),
        )
    except AuditAuthorizationError as exc:
        assert "digest" in str(exc)
    else:
        raise AssertionError("mismatched digest")


def test_synthetic_events_match_independent_money() -> None:
    dataset = {
        "tenant_id": "tenant-asc",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "110.00", "status": "open"}],
        "payments": [],
    }
    expected = Decimal("110.00") - Decimal("100.00")
    dossier = run_authorized_audit(
        _auth("SYNTHETIC_VALIDATION", "SYNTHETIC_ONLY"),
        NOW,
        dataset,
        source_sha256=digest(dataset),
        byte_length=admitted_byte_length(dataset),
    )
    assert dossier["status"] == "SYNTHETIC_AUDIT_COMPLETE"
    assert dossier["financial_summary"]["identified_exposure_usd"] == f"{expected:.2f}"
    assert dossier["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    assert sum(Decimal(item["exposure_usd"]) for item in dossier["events"]) == expected
    assert dossier["rows_returned"] is False


def test_onboarding_map_is_supplied_by_the_caller() -> None:
    rows = normalize_invoices(
        [{"InvNo": "I1", "Work": "J1", "Amt": "10.00", "State": "open"}],
        {"invoice_id": "InvNo", "job_id": "Work", "amount": "Amt", "status": "State"},
    )
    assert rows == [{"invoice_id": "I1", "job_id": "J1", "amount": "10.00", "status": "open"}]
    try:
        normalize_invoices([{"invoice_id": "I1"}], {"invoice_id": "invoice_id"})
    except ValueError as exc:
        assert "missing canonical fields" in str(exc)
    else:
        raise AssertionError("partial map")


def test_package_source_does_not_encode_a_company_dataset() -> None:
    root = Path(__file__).resolve().parents[1] / "aurex" / "ascendancy"
    text = "\n".join(path.read_text() for path in root.glob("*.py"))
    lowered = text.lower()
    assert "the big one" not in lowered
    assert "company_schema" not in lowered
