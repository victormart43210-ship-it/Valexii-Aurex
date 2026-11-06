"""Incremental monitoring over typed synthetic records.

Reconciliation of the merged snapshot is repeated in memory because a new invoice can
refer to an older job. Source documents are not re-read. Findings are never promoted to
confirmed recovery by monitoring.
"""

from __future__ import annotations

from typing import Any

from aurex import dispater_store
from aurex.dispater_intelligence import InvalidSnapshot, RevenueLeakageEngine

TABLE_IDS = {
    "jobs": "job_id",
    "invoices": "invoice_id",
    "rates": "rate_id",
    "payments": "payment_id",
    "equipment": "ticket_id",
    "labor": "record_id",
}


def _index(rows: list[dict[str, Any]], id_key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row[id_key]
        if key in indexed and indexed[key] != row:
            raise InvalidSnapshot(f"conflicting {id_key} {key}; requalify explicitly instead of overwriting")
        indexed[key] = row
    return indexed


def merge_datasets(base: dict[str, Any], additions: dict[str, Any]) -> dict[str, Any]:
    """Merge by identifier. An identical replay is a no-op. A changed identifier is rejected."""
    if base.get("tenant_id") != additions.get("tenant_id"):
        raise InvalidSnapshot("monitoring batch tenant does not match the baseline")
    if base.get("dataset_type") != "SYNTHETIC_ONLY" or additions.get("dataset_type") != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("monitoring accepts synthetic records only")
    merged = {
        "tenant_id": base["tenant_id"],
        "dataset_type": "SYNTHETIC_ONLY",
    }
    for table, id_key in TABLE_IDS.items():
        current = _index(list(base.get(table, [])), id_key)
        incoming = _index(list(additions.get(table, [])), id_key)
        for key, row in incoming.items():
            if key in current and current[key] != row:
                raise InvalidSnapshot(f"conflicting {id_key} {key}; requalify explicitly instead of overwriting")
            current[key] = row
        merged[table] = [current[key] for key in sorted(current)]
    return merged


def diff_findings(previous: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify finding movement. Absence is not a collected recovery."""
    prior = {(item["code"], item["subject"]): item for item in previous}
    live = {(item["code"], item["subject"]): item for item in current}
    events: list[dict[str, Any]] = []
    for key in sorted(live):
        item = live[key]
        if key not in prior:
            kind = "NEW_FINDING"
        elif prior[key].get("finding_sha256") == item.get("finding_sha256"):
            kind = "UNCHANGED"
        else:
            kind = "REQUALIFIED"
        events.append(
            {
                "type": kind,
                "code": item["code"],
                "subject": item["subject"],
                "qualification": item.get("qualification"),
                "confirmed": False,
            }
        )
    for key in sorted(prior):
        if key not in live:
            events.append(
                {
                    "type": "ABSENT",
                    "code": key[0],
                    "subject": key[1],
                    "qualification": prior[key].get("qualification"),
                    "confirmed": False,
                    "note": "Absence is not resolution and not recovered cash.",
                }
            )
    return {
        "authority_state": "HOLD",
        "financial_authority": "NONE",
        "confirmed_recovery_usd": "0.00",
        "events": events,
    }


def monitor_increment(tenant_id: str, baseline: dict[str, Any], additions: dict[str, Any]) -> dict[str, Any]:
    """Reconcile the merged snapshot and diff it against the baseline findings."""
    before = RevenueLeakageEngine(tenant_id).reconcile_records(baseline)
    merged = merge_datasets(baseline, additions)
    after = RevenueLeakageEngine(tenant_id).reconcile_records(merged)
    movement = diff_findings(before["findings"], after["findings"])
    movement["dataset_sha256"] = after["dataset_sha256"]
    movement["identified_exposure_usd"] = after["financial_summary"]["identified_exposure_usd"]
    movement["withheld_unresolved_usd"] = after["financial_summary"]["withheld_unresolved_usd"]
    return movement


def persist_increment(
    tenant_id: str,
    baseline: dict[str, Any],
    additions: dict[str, Any],
    source_sha256: str,
) -> tuple[dict[str, Any], bool]:
    """Store one monitoring checkpoint. The same source digest is a retry, not a new event."""
    if not isinstance(source_sha256, str) or len(source_sha256) != 64:
        raise InvalidSnapshot("source digest must be a sha256 hex string")
    merged = merge_datasets(baseline, additions)
    before = RevenueLeakageEngine(tenant_id).reconcile_records(baseline)
    after = RevenueLeakageEngine(tenant_id).reconcile_records(merged)
    existing = dispater_store.get_monitor_event(tenant_id, source_sha256)
    if existing is not None:
        if existing["checkpoint_sha256"] != after["dataset_sha256"]:
            raise InvalidSnapshot("conflicting source evidence: digest reused for a different checkpoint")
        return existing, False
    stored, _created = dispater_store.save_run(tenant_id, after)
    movement = diff_findings(before["findings"], after["findings"])
    payload = {
        "run_id": stored["run_id"],
        "receipt_binding": stored.get("receipt_binding"),
        "dataset_sha256": after["dataset_sha256"],
        "events": movement["events"],
        "identified_exposure_usd": after["financial_summary"]["identified_exposure_usd"],
        "withheld_unresolved_usd": after["financial_summary"]["withheld_unresolved_usd"],
        "confirmed_recovery_usd": "0.00",
        "authority_state": "HOLD",
        "financial_authority": "NONE",
    }
    event = dispater_store.save_monitor_event(
        tenant_id,
        source_sha256=source_sha256,
        checkpoint_sha256=after["dataset_sha256"],
        event_type="INCREMENT",
        payload=payload,
    )
    return event, True
