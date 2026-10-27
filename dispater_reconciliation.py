"""DISPATER deterministic, synthetic-only invoice reconciliation candidate.

No financial authority, writes, external services, or automatic approvals.
This standalone module is intentionally not wired to a production route.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Literal

FindingCode = Literal["MISSING_TICKET", "MISSING_PO", "MISSING_RATE", "RATE_MISMATCH", "AMOUNT_MISMATCH", "DUPLICATE_INVOICE", "MISSING_SIGNATURE"]


@dataclass(frozen=True)
class Finding:
    code: FindingCode
    invoice_id: str
    tenant_id: str
    exposure: str
    evidence_hash: str
    review_status: Literal["HUMAN_REVIEW_REQUIRED"] = "HUMAN_REVIEW_REQUIRED"


def _amount(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid monetary value") from exc
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("amount must be finite, nonnegative and have at most two decimals")
    return amount


def reconcile_synthetic(
    tenant_id: str,
    invoices: list[dict[str, object]],
    tickets: list[dict[str, object]],
    purchase_orders: list[dict[str, object]],
    rates: list[dict[str, object]],
) -> list[Finding]:
    """Produce review-only findings; inputs must be explicitly synthetic.

    All records are tenant-scoped and exact-ID matched. Missing evidence never
    produces an approval. Exposure is *potential*, never recovered revenue.
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id required")
    sources = (invoices, tickets, purchase_orders, rates)
    for records in sources:
        for record in records:
            if record.get("synthetic") is not True or record.get("tenant_id") != tenant_id:
                raise ValueError("only tenant-matched synthetic records accepted")
    def index(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = {}
        for record in records:
            key = record.get("id")
            if not isinstance(key, str) or not key or key in result:
                raise ValueError("record IDs must be unique nonempty strings")
            result[key] = record
        return result
    ticket_map, po_map, rate_map = (index(records) for records in (tickets, purchase_orders, rates))
    invoice_map = index(invoices)
    seen: set[tuple[str, str, str]] = set()
    findings: list[Finding] = []
    for invoice_id, invoice in sorted(invoice_map.items()):
        amount = _amount(invoice.get("amount"))
        ticket_id, po_id, rate_id = (invoice.get(key) for key in ("ticket_id", "po_id", "rate_id"))
        if not all(isinstance(x, str) for x in (ticket_id, po_id, rate_id)):
            raise ValueError("references must be strings")
        digest = sha256(json.dumps(invoice, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        def flag(code: FindingCode, exposure: Decimal) -> None:
            findings.append(Finding(code, invoice_id, tenant_id, str(exposure), digest))
        if ticket_id not in ticket_map:
            flag("MISSING_TICKET", amount)
        elif ticket_map[ticket_id].get("signed") is not True:
            flag("MISSING_SIGNATURE", amount)
        if po_id not in po_map:
            flag("MISSING_PO", amount)
        if rate_id not in rate_map:
            flag("MISSING_RATE", amount)
        else:
            rate = _amount(rate_map[rate_id].get("unit_rate"))
            quantity = _amount(invoice.get("quantity"))
            expected = rate * quantity
            if expected != amount:
                flag("RATE_MISMATCH", abs(expected - amount))
        if po_id in po_map and "approved_amount" in po_map[po_id]:
            approved = _amount(po_map[po_id]["approved_amount"])
            if amount > approved:
                flag("AMOUNT_MISMATCH", amount - approved)
        signature = (str(invoice.get("vendor_id", "")), str(invoice.get("external_number", "")), str(amount))
        if signature in seen:
            flag("DUPLICATE_INVOICE", amount)
        seen.add(signature)
    return findings
