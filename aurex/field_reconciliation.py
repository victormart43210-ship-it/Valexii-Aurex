"""AUREX Field Audit: deterministic, synthetic-only financial reconciliation rules.

These functions do not authenticate documents, determine legal obligations,
approve spending, or give AI models authority. All input is already structured.
"""
from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

MAX_CASES = 100
_CASE_ID = re.compile(r"BETA-[0-9]{3}\Z")
_INVOICE_ID = re.compile(r"INV-[0-9]{4}\Z")
_FIELDS = frozenset({
    "case_id", "invoice_id", "invoice_cents", "ticket_cents",
    "approved_rate_cents_per_hour", "documented_hours", "synthetic",
})


def invoice_ticket_difference(invoice: Decimal, ticket: Decimal) -> Decimal:
    """Signed decimal variance; used by the nine-source pilot and beta fixtures."""
    if not isinstance(invoice, Decimal) or not isinstance(ticket, Decimal):
        raise ValueError("two exact Decimal amounts required")
    if not invoice.is_finite() or not ticket.is_finite():
        raise ValueError("nonfinite amount refused")
    return invoice - ticket


def reconcile_field_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare fictional invoices, tickets, rates, and duplicate IDs in order.

    Reject malformed input atomically; no partial release report or side effects.
    Caller owns evidence provenance and independently scores outputs.
    """
    if type(cases) is not list or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError("expected 1-100 structured synthetic cases")
    known_cases: set[str] = set()
    known_invoices: set[str] = set()
    outputs: list[dict[str, Any]] = []
    for row in cases:
        if type(row) is not dict or set(row) != _FIELDS or row["synthetic"] is not True:
            raise ValueError("invalid or non-synthetic field record")
        cid, iid = row["case_id"], row["invoice_id"]
        if (type(cid) is not str or not _CASE_ID.fullmatch(cid) or cid in known_cases
                or type(iid) is not str or not _INVOICE_ID.fullmatch(iid)):
            raise ValueError("invalid or duplicate case ID or invoice ID format")
        invoice, ticket = row["invoice_cents"], row["ticket_cents"]
        hours, rate = row["documented_hours"], row["approved_rate_cents_per_hour"]
        if (type(invoice) is not int or not 0 < invoice <= 100_000_000
                or type(ticket) is not int or not 0 < ticket <= 100_000_000
                or type(hours) is not int or not 1 <= hours <= 10_000
                or (rate is not None and (type(rate) is not int or not 0 < rate <= 10_000_000))):
            raise ValueError("invalid fixed-cent, rate, or hour fields")
        flags: list[str] = []
        if iid in known_invoices:
            flags.append("DUPLICATE_INVOICE_ID")
        if invoice_ticket_difference(Decimal(invoice), Decimal(ticket)) != 0:
            flags.append("INVOICE_TICKET_VARIANCE")
        if rate is None:
            flags.append("MISSING_RATE_APPROVAL")
        elif ticket != rate * hours:
            flags.append("TICKET_RATE_VARIANCE")
        known_cases.add(cid)
        known_invoices.add(iid)
        outputs.append({"case_id": cid, "flags": sorted(flags)})
    return outputs
