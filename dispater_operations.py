"""DISPATER synthetic-only operational exception detection.

Candidate building blocks inspired by industry-standard ticketing, job-costing,
maintenance and exception-review workflows. No external I/O or authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True)
class OperationalException:
    kind: str
    tenant_id: str
    record_id: str
    detail: str
    potential_exposure: str | None
    evidence_hash: str
    status: str = "HUMAN_REVIEW_REQUIRED"


def _money(value: Any) -> Decimal:
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid amount") from exc
    if not d.is_finite() or d < 0 or d.as_tuple().exponent < -2:
        raise ValueError("invalid amount")
    return d


def _validate(tenant: str, records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not tenant or not tenant.strip():
        raise ValueError("tenant required")
    indexed: dict[str, dict[str, Any]] = {}
    for row in records:
        if row.get("synthetic") is not True or row.get("tenant_id") != tenant:
            raise ValueError("synthetic tenant boundary violation")
        key = row.get("id")
        if not isinstance(key, str) or not key or key in indexed:
            raise ValueError("duplicate or invalid ID")
        indexed[key] = row
    return indexed


def _finding(kind: str, tenant: str, record: dict[str, Any], detail: str, exposure: Decimal | None = None) -> OperationalException:
    evidence_hash = sha256(json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return OperationalException(kind, tenant, record["id"], detail, str(exposure) if exposure is not None else None, evidence_hash)


def detect_unbilled_tickets(
    tenant_id: str, tickets: list[dict[str, Any]], invoices: list[dict[str, Any]]
) -> list[OperationalException]:
    """Identify completed synthetic tickets without an invoice reference.

    Exposure is an unverified potential amount, not recovered revenue.
    """
    ticket_map = _validate(tenant_id, tickets)
    invoice_map = _validate(tenant_id, invoices)
    billed = {i.get("ticket_id") for i in invoice_map.values()}
    result = []
    for key, ticket in sorted(ticket_map.items()):
        if ticket.get("status") == "COMPLETED" and key not in billed:
            amount = _money(ticket["estimated_billable_amount"]) if "estimated_billable_amount" in ticket else None
            result.append(_finding("UNBILLED_COMPLETED_TICKET", tenant_id, ticket, "No linked invoice found in supplied dataset; verify completeness.", amount))
    return result


def detect_maintenance_exceptions(
    tenant_id: str, assets: list[dict[str, Any]]
) -> list[OperationalException]:
    """Deterministic threshold checks, not predictive maintenance."""
    asset_map = _validate(tenant_id, assets)
    result = []
    for _, asset in sorted(asset_map.items()):
        unit = asset.get("meter_unit")
        if unit not in {"hours", "miles"}:
            raise ValueError("unsupported meter unit")
        reading = _money(asset.get("meter_reading"))
        due = _money(asset.get("service_due_at"))
        if reading >= due:
            result.append(_finding("MAINTENANCE_DUE", tenant_id, asset, f"{unit}: {reading} recorded; service threshold {due}; human verification required."))
        if asset.get("inspection_status") == "MISSING":
            result.append(_finding("INSPECTION_MISSING", tenant_id, asset, "Inspection evidence missing; verify with equipment supervisor."))
    return result


def summarize_exceptions(findings: list[OperationalException]) -> dict[str, Any]:
    """Do not double-count exposure: same record can have multiple findings."""
    seen: set[tuple[str, str]] = set()
    exposure = Decimal("0")
    for f in findings:
        if f.status != "HUMAN_REVIEW_REQUIRED":
            raise ValueError("unauthorized finding status")
        key = (f.tenant_id, f.record_id)
        if key not in seen and f.potential_exposure is not None:
            exposure += _money(f.potential_exposure)
            seen.add(key)
    return {"exceptions": len(findings), "potential_exposure_upper_bound": str(exposure), "verified_savings": None, "note": "Synthetic, incomplete data; exposure is not recovered revenue."}
