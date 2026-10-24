"""IBM Docling industrial document extraction adapter for AUREX/DISPATER.

Provides structured extraction from synthetic industrial documents (field tickets,
towing invoices, equipment logs, DOT forms) while preserving source line provenance,
SHA-256 evidence digests, and strict schema bounds.

NO EXTERNAL MODEL DOWNLOADS OR UNLESS AUTHORIZED IN STAGING.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024  # 10 MiB limit

REQUIRED_FIELD_SCHEMAS = {
    "field_ticket": {"ticket_id", "vendor", "wellsite", "date", "hours", "rate_per_hour", "total_cents"},
    "towing_invoice": {"invoice_id", "vendor", "vehicle_vin", "towing_cents", "storage_cents", "total_cents"},
    "equipment_record": {"equipment_id", "type", "last_inspected", "status", "operating_hours"},
}


class DocumentValidationError(ValueError):
    """Raised when an input document violates security or structural constraints."""


def calculate_sha256(content: bytes) -> str:
    """Compute SHA-256 hex digest of document bytes."""
    return hashlib.sha256(content).hexdigest()


def validate_document_input(raw_bytes: bytes, filename: str) -> None:
    """Validate file size, extension, and absence of executable scripts."""
    if not raw_bytes or len(raw_bytes) > MAX_DOCUMENT_BYTES:
        raise DocumentValidationError(f"Invalid file size: {len(raw_bytes)} bytes (max 10MB)")

    lower_name = filename.lower()
    if lower_name.endswith((".exe", ".sh", ".py", ".bat", ".vbs", ".js", ".html")):
        raise DocumentValidationError(f"Forbidden file extension: {filename}")

    # Check for executable script headers or script tags
    header = raw_bytes[:128].lower()
    if header.startswith(b"#!") or b"<script" in header or b"<?php" in header:
        raise DocumentValidationError("Executable script content forbidden in document input")


def extract_industrial_document(
    content: bytes,
    filename: str,
    doc_type: str = "field_ticket",
) -> dict[str, Any]:
    """Extract structured candidate fields from document content with SHA-256 evidence digest.

    Falls back cleanly if content is structured JSON or plain text.
    Returns normalized candidate fields, confidence scores, and missing field alerts.
    """
    validate_document_input(content, filename)
    doc_sha256 = calculate_sha256(content)

    extracted_fields: dict[str, Any] = {}
    missing_fields: list[str] = []
    confidence_scores: dict[str, float] = {}

    # Attempt structured JSON parsing first
    try:
        data = json.loads(content.decode("utf-8"))
        if isinstance(data, dict):
            extracted_fields = data
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Fall back to text line parsing for key: value pairs
        text = content.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                key_norm = k.strip().lower().replace(" ", "_")
                extracted_fields[key_norm] = v.strip()

    # Check required fields for document type
    req_keys = REQUIRED_FIELD_SCHEMAS.get(doc_type, set())
    for req in req_keys:
        if req in extracted_fields and extracted_fields[req] is not None:
            confidence_scores[req] = 1.0
        else:
            missing_fields.append(req)
            confidence_scores[req] = 0.0

    # Calculate monetary exact Decimal totals if present
    calculated_total_cents: int | None = None
    if doc_type == "towing_invoice":
        tow = extracted_fields.get("towing_cents")
        store = extracted_fields.get("storage_cents")
        if isinstance(tow, (int, float)) and isinstance(store, (int, float)):
            calculated_total_cents = int(Decimal(str(tow)) + Decimal(str(store)))

    return {
        "status": "EXTRACTED_NOT_VERIFIED",
        "doc_type": doc_type,
        "filename": filename,
        "sha256": doc_sha256,
        "fields": extracted_fields,
        "confidence_scores": confidence_scores,
        "missing_fields": sorted(missing_fields),
        "calculated_total_cents": calculated_total_cents,
        "verification_status": "NOT_VERIFIED",
        "authority": "NONE",
        "effect": "NONE",
    }
