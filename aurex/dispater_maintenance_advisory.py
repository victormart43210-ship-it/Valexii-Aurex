"""DISPATER industrial maintenance advisory: original, deterministic, synthetic-only.

Capability-level inspiration from public industrial EAM/FSM descriptions.
Not IFS software, not an IFS connector, not predictive ML, and not dispatch authority.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any


class MaintenanceInputError(ValueError):
    """Invalid or unsupported maintenance data."""


def _day(value: object) -> date:
    if not isinstance(value, str):
        raise MaintenanceInputError("date must be ISO text")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise MaintenanceInputError("invalid ISO date") from exc
    if parsed.isoformat() != value:
        raise MaintenanceInputError("date must be YYYY-MM-DD")
    return parsed


def _hours(value: object) -> Decimal:
    if not isinstance(value, str):
        raise MaintenanceInputError("meter values must be decimal strings")
    try:
        n = Decimal(value)
    except InvalidOperation as exc:
        raise MaintenanceInputError("invalid meter value") from exc
    if not n.is_finite() or n < 0 or n > 100000000 or n.quantize(Decimal("0.01")) != n:
        raise MaintenanceInputError("meter value out of bounds")
    return n


def assess_maintenance(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Produce read-only work-order proposals from a bounded synthetic snapshot.

    Calendar and hour thresholds are deterministic, not predictions.
    All proposed actions require a separate human approval.
    """
    if not isinstance(snapshot, dict) or snapshot.get("dataset_type") != "SYNTHETIC_ONLY":
        raise MaintenanceInputError("synthetic-only input required")
    tenant = snapshot.get("tenant_id")
    if not isinstance(tenant, str) or not (1 <= len(tenant) <= 80):
        raise MaintenanceInputError("tenant_id required")
    as_of = _day(snapshot.get("as_of"))
    assets = snapshot.get("assets")
    if not isinstance(assets, list) or len(assets) > 1000:
        raise MaintenanceInputError("assets must be a bounded list")
    ids: set[str] = set()
    findings: list[dict[str, str]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            raise MaintenanceInputError("invalid asset")
        asset_id = asset.get("asset_id")
        if not isinstance(asset_id, str) or not (1 <= len(asset_id) <= 80) or asset_id in ids:
            raise MaintenanceInputError("missing or duplicate asset_id")
        ids.add(asset_id)
        if asset.get("tenant_id") != tenant:
            raise MaintenanceInputError("cross-tenant asset rejected")
        last = _day(asset.get("last_service_date"))
        if last > as_of:
            raise MaintenanceInputError("future service date")
        interval = asset.get("service_interval_days")
        if type(interval) is not int or not (1 <= interval <= 3650):
            raise MaintenanceInputError("invalid service interval")
        current = _hours(asset.get("meter_hours"))
        serviced = _hours(asset.get("last_service_meter_hours"))
        if current < serviced:
            raise MaintenanceInputError("meter rollback requires independent reconciliation")
        try:
            due_date = last + timedelta(days=interval)
        except OverflowError as exc:
            raise MaintenanceInputError("due date out of bounds") from exc
        calendar_due = as_of >= due_date
        hour_due = False
        due_hours = None
        if "service_interval_hours" in asset:
            step = _hours(asset["service_interval_hours"])
            if step <= 0:
                raise MaintenanceInputError("hour interval must be positive")
            due_hours = serviced + step
            hour_due = current >= due_hours
        if not (calendar_due or hour_due):
            continue
        reasons = []
        if calendar_due:
            reasons.append("CALENDAR_DUE")
        if hour_due:
            reasons.append("METER_DUE")
        finding = {
            "asset_id": asset_id,
            "status": "PROPOSED_HUMAN_REVIEW",
            "authority": "NONE",
            "reasons": ",".join(reasons),
            "due_date": due_date.isoformat(),
            "next_service_meter_hours": str(due_hours) if due_hours is not None else "NOT_CONFIGURED",
            "now": "Maintenance threshold reached for asset " + asset_id,
            "changed": ",".join(reasons),
            "next": "Inspect service history and propose a work order for human approval",
            "why": "Calendar or meter threshold met; not a prediction of failure",
            "proof": f"last_service={last.isoformat()}; current_meter={current}; last_service_meter={serviced}",
        }
        findings.append(finding)
    findings.sort(key=lambda item: item["asset_id"])
    report: dict[str, Any] = {
        "schema": "dispater.synthetic.maintenance_advisory.v1",
        "tenant_id": tenant,
        "as_of": as_of.isoformat(),
        "financial_authority": "NONE",
        "dispatch_authority": "NONE",
        "confirmed_savings_usd": "0.00",
        "work_orders_created": 0,
        "findings": findings,
    }
    # This digest covers the advisory report, not the input snapshot or its provenance.
    raw = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    report["receipt_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return report
