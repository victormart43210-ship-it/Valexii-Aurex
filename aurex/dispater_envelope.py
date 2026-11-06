"""
DISPATER Canonical Evidence Normalization and Envelope Schemas.

Enforces versioned, tamper-evident data contracts for industrial audit records:
- Original source bytes and SHA-256 digests are permanently retained.
- Model-generated or OCR text can NEVER overwrite original source evidence.
- Field-level provenance retains raw value, normalized Decimal value, adapter ID/version,
  confidence score, page/row locator, and evidence qualification state.
- Invariants: Decimal arithmetic for all currency amounts, fail-closed validation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

SCHEMA_VERSION = "dispater.evidence.envelope.v1"


def compute_sha256(data: bytes | str | dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash."""
    if isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    elif isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    else:
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class EvidenceQualificationStatus(StrEnum):
    PENDING_QUALIFICATION = "PENDING_QUALIFICATION"
    QUALIFIED_INDEPENDENT = "QUALIFIED_INDEPENDENT"
    DERIVED_CORROBORATION = "DERIVED_CORROBORATION"
    CONTESTED = "CONTESTED"
    STALE = "STALE"
    INVALIDATED = "INVALIDATED"
    WITHHELD = "WITHHELD"


class DocumentCategory(StrEnum):
    INVOICE = "INVOICE"
    EQUIPMENT_TICKET = "EQUIPMENT_TICKET"
    RATE_SCHEDULE = "RATE_SCHEDULE"
    CONTRACT = "CONTRACT"
    PAYMENT_RECORD = "PAYMENT_RECORD"
    DISPATCH_LOG = "DISPATCH_LOG"
    ADJUSTMENT = "ADJUSTMENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FieldProvenance:
    field_name: str
    raw_value: str
    normalized_value: Any
    adapter_id: str
    adapter_version: str
    adapter_digest: str
    page_or_row_locator: str
    confidence: float
    qualification_status: EvidenceQualificationStatus
    recorded_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "raw_value": self.raw_value,
            "normalized_value": (
                str(self.normalized_value)
                if isinstance(self.normalized_value, Decimal)
                else self.normalized_value
            ),
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "adapter_digest": self.adapter_digest,
            "page_or_row_locator": self.page_or_row_locator,
            "confidence": self.confidence,
            "qualification_status": self.qualification_status.value,
            "recorded_at_utc": self.recorded_at_utc,
        }


@dataclass(frozen=True)
class CanonicalEvidenceEnvelope:
    envelope_id: str
    schema_version: str
    tenant_id: str
    source_id: str
    source_record_id: str
    document_category: DocumentCategory
    source_content_sha256: str
    byte_count: int
    media_type: str
    ingested_at_utc: str
    provenance_fields: list[FieldProvenance]
    raw_payload_preview: str  # Bound preview, original bytes stored in object store / hash verification
    superseded_by_id: str | None = None
    envelope_digest: str = ""

    def __post_init__(self) -> None:
        if not self.envelope_digest:
            body = {
                "envelope_id": self.envelope_id,
                "schema_version": self.schema_version,
                "tenant_id": self.tenant_id,
                "source_id": self.source_id,
                "source_record_id": self.source_record_id,
                "document_category": self.document_category.value,
                "source_content_sha256": self.source_content_sha256,
                "byte_count": self.byte_count,
                "media_type": self.media_type,
                "ingested_at_utc": self.ingested_at_utc,
                "provenance_fields": [f.to_dict() for f in self.provenance_fields],
                "superseded_by_id": self.superseded_by_id,
            }
            computed = compute_sha256(body)
            object.__setattr__(self, "envelope_digest", computed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "schema_version": self.schema_version,
            "tenant_id": self.tenant_id,
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
            "document_category": self.document_category.value,
            "source_content_sha256": self.source_content_sha256,
            "byte_count": self.byte_count,
            "media_type": self.media_type,
            "ingested_at_utc": self.ingested_at_utc,
            "provenance_fields": [f.to_dict() for f in self.provenance_fields],
            "raw_payload_preview": self.raw_payload_preview,
            "superseded_by_id": self.superseded_by_id,
            "envelope_digest": self.envelope_digest,
        }


def normalize_currency_amount(raw_val: str | int | float | Decimal) -> Decimal:
    """Safely convert any currency string or numeric to a finite Decimal."""
    if isinstance(raw_val, Decimal):
        if not raw_val.is_finite():
            raise ValueError("Non-finite decimal encountered")
        return raw_val.quantize(Decimal("0.01"))
    s = str(raw_val).strip().replace("$", "").replace(",", "")
    try:
        val = Decimal(s)
        if not val.is_finite():
            raise ValueError("Non-finite decimal encountered")
        return val.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid currency value: {raw_val}") from e
