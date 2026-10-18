"""Deterministic Financial Extractor Module for AUREX (Operation KUSANAGI XC Reconciled)."""

import re
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    description: str = Field(min_length=1)
    quantity: float = Field(default=1.0, ge=0.0)
    unit_price: float = Field(default=0.0, ge=0.0)
    amount: float = Field(default=0.0, ge=0.0)


class FinancialExtractionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "1.0"
    document_id: str = Field(min_length=1)
    vendor_name: str = Field(default="UNKNOWN_VENDOR")
    invoice_number: str | None = None
    invoice_date: str | None = None
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    subtotal_amount: float = Field(default=0.0, ge=0.0)
    tax_amount: float = Field(default=0.0, ge=0.0)
    total_amount: float = Field(default=0.0, ge=0.0)
    subtotal_present: bool = False
    final_total_present: bool = False
    has_missing_totals: bool = False
    consistency_result: Literal["CONSISTENT", "DISCREPANCY", "INDETERMINATE"] = "INDETERMINATE"
    line_items: tuple[LineItem, ...] = ()
    extracted_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def digest_sha256(self) -> str:
        body = {
            "schema_version": self.schema_version,
            "document_id": self.document_id,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "currency": self.currency,
            "subtotal_amount": self.subtotal_amount,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "subtotal_present": self.subtotal_present,
            "final_total_present": self.final_total_present,
            "has_missing_totals": self.has_missing_totals,
            "consistency_result": self.consistency_result,
            "line_items": [item.model_dump() for item in self.line_items],
        }
        return fingerprint(body)


def _to_decimal(val_str: str) -> float:
    d = Decimal(val_str.replace(",", "")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(d)


def extract_financial_data(
    document_id: str,
    raw_text: str,
) -> FinancialExtractionRecord:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    vendor = lines[0] if lines else "UNKNOWN_VENDOR"

    inv_match = re.search(r"(?:invoice|inv|bill)\s*#?\s*:?\s*([A-Za-z0-9\-]+)", raw_text, re.IGNORECASE)
    invoice_num = inv_match.group(1) if inv_match else None

    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b", raw_text)
    invoice_date = date_match.group(1) if date_match else None

    subtotal_match = re.search(r"(?:subtotal|sub-total)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    subtotal_present = bool(subtotal_match)
    subtotal_amount = _to_decimal(subtotal_match.group(1)) if subtotal_match else 0.0

    total_match = re.search(
        r"(?:grand total|total amount|amount due|balance due|\btotal due\b|\btotal\b)\s*:?\s*\$?\s*([\d,]+\.\d{2})",
        raw_text,
        re.IGNORECASE,
    )
    final_total_present = bool(total_match)
    total_amount = _to_decimal(total_match.group(1)) if total_match else 0.0

    tax_match = re.search(r"(?:tax|vat|gst)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    tax_amount = _to_decimal(tax_match.group(1)) if tax_match else 0.0

    has_missing = not subtotal_present and not final_total_present

    currency = "USD"
    if "EUR" in raw_text or "€" in raw_text:
        currency = "EUR"
    elif "GBP" in raw_text or "£" in raw_text:
        currency = "GBP"

    items: list[LineItem] = []
    item_matches = re.findall(r"([A-Za-z0-9\s\-]+)\s+(\d+(?:\.\d+)?)\s+x\s+\$?([\d\.]+)\s+=\s+\$?([\d\.]+)", raw_text)
    for desc, qty, price, amt in item_matches:
        items.append(
            LineItem(
                description=desc.strip(),
                quantity=float(qty),
                unit_price=_to_decimal(price),
                amount=_to_decimal(amt),
            )
        )

    consistency: Literal["CONSISTENT", "DISCREPANCY", "INDETERMINATE"] = "INDETERMINATE"
    if subtotal_present and final_total_present:
        expected = round(subtotal_amount + tax_amount, 2)
        consistency = "CONSISTENT" if abs(expected - total_amount) < 0.001 else "DISCREPANCY"

    return FinancialExtractionRecord(
        document_id=document_id,
        vendor_name=vendor,
        invoice_number=invoice_num,
        invoice_date=invoice_date,
        currency=currency,
        subtotal_amount=subtotal_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        subtotal_present=subtotal_present,
        final_total_present=final_total_present,
        has_missing_totals=has_missing,
        consistency_result=consistency,
        line_items=tuple(items),
    )
