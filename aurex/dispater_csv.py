"""Deterministic, offline, synthetic-only CSV reconciliation for DISPATER.

Compares invoice lines against approved rates and field/service tickets using
Decimal arithmetic only. Findings are PROPOSED exceptions for human review; no
record is modified and no model output is used for any amount.
"""

from __future__ import annotations

import csv
import io
from decimal import Decimal
from typing import Any

from aurex.dispater_pilot import InvalidSnapshot, _money, digest

MAX_BYTES = 1_000_000
MAX_ROWS = 5000
_INVOICE = ("invoice_id", "ticket_id", "service", "quantity", "unit_rate")
_TICKET = ("ticket_id", "service", "quantity")
_RATES = ("service", "approved_rate")


def _read(text: str, required: tuple[str, ...], name: str) -> list[dict[str, str]]:
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise InvalidSnapshot(f"{name}: invalid or oversized CSV")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or set(reader.fieldnames) != set(required):
        raise InvalidSnapshot(f"{name}: columns must be exactly {list(required)}")
    rows = []
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise InvalidSnapshot(f"{name}: malformed row")
        rows.append({k: v.strip() for k, v in row.items()})
        if len(rows) > MAX_ROWS:
            raise InvalidSnapshot(f"{name}: too many rows")
    return rows


def _qty(value: str) -> Decimal:
    return _money(value)


def reconcile_csv(invoices: str, tickets: str, rates: str) -> dict[str, Any]:
    inv = _read(invoices, _INVOICE, "invoices")
    tix = _read(tickets, _TICKET, "tickets")
    rts = _read(rates, _RATES, "rates")
    rate_by_service: dict[str, Decimal] = {}
    for r in rts:
        if r["service"] in rate_by_service:
            raise InvalidSnapshot("rates: duplicate service")
        rate_by_service[r["service"]] = _money(r["approved_rate"])
    ticket_by_id: dict[str, dict[str, str]] = {}
    for t in tix:
        if t["ticket_id"] in ticket_by_id:
            raise InvalidSnapshot("tickets: duplicate ticket_id")
        ticket_by_id[t["ticket_id"]] = t

    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    billed: set[str] = set()
    for row in inv:
        key = (row["invoice_id"], row["ticket_id"])
        ref = f"invoice:{row['invoice_id']}/ticket:{row['ticket_id']}"
        if key in seen:
            findings.append({"code": "DUPLICATE_INVOICE_LINE", "ref": ref})
            continue
        seen.add(key)
        billed.add(row["ticket_id"])
        ticket = ticket_by_id.get(row["ticket_id"])
        if ticket is None:
            findings.append({"code": "MISSING_TICKET", "ref": ref})
            continue
        if ticket["service"] != row["service"]:
            findings.append({"code": "SERVICE_MISMATCH", "ref": ref})
        if _qty(ticket["quantity"]) != _qty(row["quantity"]):
            findings.append({"code": "QUANTITY_MISMATCH", "ref": ref})
        approved = rate_by_service.get(row["service"])
        if approved is None:
            findings.append({"code": "NO_APPROVED_RATE", "ref": ref})
        elif _money(row["unit_rate"]) != approved:
            over = (_money(row["unit_rate"]) - approved) * _qty(row["quantity"])
            findings.append({"code": "RATE_MISMATCH", "ref": ref,
                             "variance_usd": str(over.quantize(Decimal("0.01")))})
    for tid in sorted(set(ticket_by_id) - billed):
        findings.append({"code": "UNBILLED_TICKET", "ref": f"ticket:{tid}"})

    result: dict[str, Any] = {
        "schema": "dispater.csv.reconciliation.v1",
        "dataset_type": "SYNTHETIC_ONLY",
        "status": "EXCEPTIONS_FOR_HUMAN_REVIEW" if findings else "NO_EXCEPTIONS_DETECTED",
        "findings": findings,
        "input_digests": {"invoices": digest(invoices), "tickets": digest(tickets), "rates": digest(rates)},
        "authority": {"financial": "NONE", "model_output": "NONE", "corrections": "PROPOSED_ONLY"},
    }
    result["report_digest"] = digest({k: v for k, v in result.items()})
    return result
