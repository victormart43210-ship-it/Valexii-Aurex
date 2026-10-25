"""Deterministic, synthetic-data-only dispatch/invoice reconciliation.

No model output can establish payment, compliance, or financial authority.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, DecimalException, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    code: str
    invoice_id: str
    dispatch_id: str
    detail: str
    evidence_sha256: str
    status: str = "REVIEW_REQUIRED"


def digest(record: dict[str, str]) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def money(value: str) -> Decimal | None:
    try:
        amount = Decimal(value)
        return amount if amount.is_finite() else None
    except (InvalidOperation, TypeError):
        return None


def reconcile(dispatches: list[dict[str, str]], invoices: list[dict[str, str]]) -> list[Finding]:
    """Return review flags; do not silently approve invoices or mutate inputs."""
    dispatch_by_id: dict[str, dict[str, str]] = {}
    ambiguous_dispatch_ids: set[str] = set()
    for dispatch in dispatches:
        dispatch_id = dispatch["dispatch_id"]
        if dispatch_id in dispatch_by_id:
            ambiguous_dispatch_ids.add(dispatch_id)
        else:
            dispatch_by_id[dispatch_id] = dispatch
    seen: set[str] = set()
    findings: list[Finding] = []
    for invoice in invoices:
        invoice_id = invoice.get("invoice_id", "")
        dispatch_id = invoice.get("dispatch_id", "")
        sha = digest(invoice)

        def flag(code: str, detail: str) -> None:
            findings.append(Finding(code, invoice_id, dispatch_id, detail, sha))

        if invoice_id in seen:
            flag("DUPLICATE_INVOICE_ID", "Invoice ID appears more than once")
        seen.add(invoice_id)
        if dispatch_id in ambiguous_dispatch_ids:
            flag("AMBIGUOUS_DISPATCH", "Multiple dispatch records share this dispatch ID")
            continue
        dispatch = dispatch_by_id.get(dispatch_id)
        if dispatch is None:
            flag("MISSING_DISPATCH", "No matching dispatch record")
            continue
        billed_miles = money(invoice.get("miles", ""))
        recorded_miles = money(dispatch.get("miles", ""))
        if billed_miles is None or recorded_miles is None:
            flag("INVALID_MILEAGE", "Mileage missing or not numeric")
        elif billed_miles != recorded_miles:
            flag("MILEAGE_MISMATCH", f"Invoice miles {billed_miles}; dispatch miles {recorded_miles}")
        base = money(invoice.get("base_charge", ""))
        rate = money(invoice.get("rate_per_mile", ""))
        total = money(invoice.get("total", ""))
        if any(v is None for v in (base, rate, total, billed_miles)):
            flag("INVALID_AMOUNT", "Charge components missing or invalid")
        elif base is not None and rate is not None and total is not None and billed_miles is not None:
            try:
                expected = base + rate * billed_miles
                if expected.quantize(Decimal("0.01")) != total.quantize(Decimal("0.01")):
                    flag("TOTAL_MISMATCH", f"Invoice total {total}; computed total {expected}")
            except DecimalException:
                flag("INVALID_AMOUNT", "Charge components are outside supported precision")
    return findings


def demo() -> list[Finding]:
    base = Path(__file__).resolve().parent / "fixtures"
    return reconcile(read_csv(base / "dispatches.csv"), read_csv(base / "invoices.csv"))


if __name__ == "__main__":
    print(json.dumps([asdict(f) for f in demo()], indent=2))
