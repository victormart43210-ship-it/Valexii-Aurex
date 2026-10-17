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
    total_amount: float = Field(default=0.0, ge=0.0)
    tax_amount: float = Field(default=0.0, ge=0.0)
    line_items: tuple[LineItem, ...] = ()
    extracted_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def digest_sha256(self) -> str:
        body = {
            "document_id": self.document_id,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "total_amount": self.total_amount,
            "currency": self.currency,
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

    total_match = re.search(r"(?:total|amount due|balance due)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    total_amount = float(total_match.group(1).replace(",", "")) if total_match else 0.0

    tax_match = re.search(r"(?:tax|vat|gst)\s*:?\s*\$?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    tax_amount = float(tax_match.group(1).replace(",", "")) if tax_match else 0.0

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
                unit_price=float(price),
                amount=float(amt),
            )
        )

    return FinancialExtractionRecord(
        document_id=document_id,
        vendor_name=vendor,
        invoice_number=invoice_num,
        invoice_date=invoice_date,
        currency=currency,
        total_amount=total_amount,
        tax_amount=tax_amount,
        line_items=tuple(items),
    )
