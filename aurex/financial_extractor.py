"""Deterministic Financial Extractor Module for AUREX (Zero Paid External Model Calls)."""

import re
from datetime import UTC, datetime

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

    document_id: str = Field(min_length=1)
    vendor_name: str = Field(default="UNKNOWN_VENDOR")
    invoice_number: str | None = None
    invoice_date: str | None = None
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    subtotal_amount: float = Field(default=0.0, ge=0.0)
    tax_amount: float = Field(default=0.0, ge=0.0)
    total_amount: float = Field(default=0.0, ge=0.0)
    has_missing_totals: bool = False
    line_items: tuple[LineItem, ...] = ()
    extracted_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def digest_sha256(self) -> str:
        body = {
            "document_id": self.document_id,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "subtotal_amount": self.subtotal_amount,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "line_items_count": len(self.line_items),
        }
        return fingerprint(body)


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

    # Distinct subtotal matching
    subtotal_match = re.search(r"(?:subtotal|sub-total)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    subtotal_amount = round(float(subtotal_match.group(1).replace(",", "")), 2) if subtotal_match else 0.0

    # Grand total matching (preferring explicit grand total or balance due over subtotal)
    total_match = re.search(
        r"(?:grand total|total amount|amount due|balance due|\btotal\b)\s*:?\s*\$?\s*([\d,]+\.\d{2})",
        raw_text,
        re.IGNORECASE,
    )
    total_amount = round(float(total_match.group(1).replace(",", "")), 2) if total_match else 0.0

    tax_match = re.search(r"(?:tax|vat|gst)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    tax_amount = round(float(tax_match.group(1).replace(",", "")), 2) if tax_match else 0.0

    has_missing = total_amount == 0.0 and subtotal_amount == 0.0

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
                unit_price=round(float(price), 2),
                amount=round(float(amt), 2),
            )
        )

    return FinancialExtractionRecord(
        document_id=document_id,
        vendor_name=vendor,
        invoice_number=invoice_num,
        invoice_date=invoice_date,
        currency=currency,
        subtotal_amount=subtotal_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        has_missing_totals=has_missing,
        line_items=tuple(items),
    )
