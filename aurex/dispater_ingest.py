"""Bounded ingestion for synthetic industrial tables.

This module accepts UTF-8 CSV or JSON that already uses the reconciliation field names.
It does not OCR, fetch URLs, execute document instructions, or call a model. PDF, image,
and spreadsheet binaries are rejected until a verified parser is installed. Every accepted
batch keeps the source digest, row provenance, and a separation between source text and
the typed values passed to reconciliation.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

from aurex.dispater_intelligence import sanitize_formula_field

SCHEMA = "dispater.ingestion.v1"
MAX_BYTES = 1_000_000
MAX_ROWS = 2000
TABLES = ("jobs", "invoices", "rates", "payments", "equipment", "labor")
REQUIRED = {
    "jobs": ("job_id", "customer_id", "service_code", "date"),
    "invoices": ("invoice_id", "job_id", "amount", "status"),
    "rates": ("rate_id", "customer_id", "service_code", "start", "end", "amount"),
    "payments": ("payment_id", "invoice_id", "amount"),
    "equipment": ("ticket_id", "job_id", "equipment_id", "service_date", "billable_hours", "standby_hours", "invoiced_hours"),
    "labor": ("record_id", "job_id", "role", "service_date", "approved_hours", "billed_hours"),
}


class IngestError(ValueError):
    """A source was rejected before it could become evidence."""


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _decode(raw: bytes) -> str:
    if not isinstance(raw, bytes | bytearray):
        raise IngestError("source must be bytes")
    if len(raw) > MAX_BYTES:
        raise IngestError("source exceeds the byte limit")
    if b"\x00" in raw:
        raise IngestError("binary source rejected")
    try:
        return bytes(raw).decode("utf-8")
    except UnicodeError as exc:
        raise IngestError("source must be UTF-8") from exc


def _cell(value: str) -> str:
    cleaned = sanitize_formula_field(value.strip())
    if len(cleaned) > 256:
        raise IngestError("field exceeds 256 characters")
    return cleaned


def _rows_from_csv(text: str) -> tuple[str, list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise IngestError("csv requires a header")
    table = reader.fieldnames[0].strip()
    if table not in TABLES:
        raise IngestError("csv first column must name the table")
    expected = REQUIRED[table]
    if any(key not in reader.fieldnames for key in expected):
        raise IngestError("csv header is missing required columns")
    rows: list[dict[str, str]] = []
    for index, row in enumerate(reader, start=2):
        if len(rows) >= MAX_ROWS:
            raise IngestError("csv exceeds the row limit")
        if None in row:
            raise IngestError(f"row {index} has extra columns")
        record = {key: _cell(row.get(key, "")) for key in expected}
        if any(not record[key] for key in expected):
            raise IngestError(f"row {index} is missing a required value")
        record["_row"] = str(index)
        rows.append(record)
    return table, rows


def _rows_from_json(text: str) -> dict[str, list[dict[str, str]]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IngestError("json source is malformed") from exc
    if not isinstance(payload, dict):
        raise IngestError("json source must be an object")
    declared = payload.get("dataset_type")
    if declared is not None and declared != "SYNTHETIC_ONLY":
        raise IngestError("a source that declares a non-synthetic dataset is refused")
    tables: dict[str, list[dict[str, str]]] = {name: [] for name in TABLES}
    for name in TABLES:
        rows = payload.get(name, [])
        if not isinstance(rows, list) or len(rows) > MAX_ROWS:
            raise IngestError(f"{name} must be a bounded list")
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise IngestError(f"{name} row {index} must be an object")
            record = {key: _cell(str(row.get(key, ""))) for key in REQUIRED[name]}
            if any(not record[key] for key in REQUIRED[name]):
                raise IngestError(f"{name} row {index} is missing a required value")
            record["_row"] = str(index)
            tables[name].append(record)
    return tables


def ingest_source(tenant_id: str, filename: str, raw: bytes, *, kind: str) -> dict[str, Any]:
    """Validate one source and return typed rows plus an ingestion receipt.

    Document text is data. A cell that says to ignore policy or pay an invoice does not
    change authority, and it is stored only as a sanitized field value.
    """
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise IngestError("tenant is required")
    if kind not in ("csv", "json", "pdf", "xlsx", "png", "jpeg"):
        raise IngestError("unsupported source type")
    if not isinstance(filename, str) or "/" in filename or "\\" in filename or not filename:
        raise IngestError("filename must be a single path segment")
    source_sha256 = _digest(bytes(raw))
    field_provenance: list[dict[str, Any]] = []
    if kind in ("png", "jpeg"):
        from aurex.dispater_documents import reject_unparsed_image

        reject_unparsed_image(bytes(raw), kind)
    if kind in ("csv", "json"):
        text = _decode(raw)
        tables: dict[str, list[dict[str, str]]] = {name: [] for name in TABLES}
        if kind == "csv":
            table, rows = _rows_from_csv(text)
            tables[table] = rows
        else:
            tables = _rows_from_json(text)
    elif kind == "pdf":
        from aurex.dispater_documents import extract_pdf

        tables, field_provenance = extract_pdf(bytes(raw), source_sha256)
    elif kind == "xlsx":
        from aurex.dispater_documents import extract_xlsx

        tables = extract_xlsx(bytes(raw))
    else:
        raise IngestError("unsupported source type")
    provenance = []
    for name, rows in tables.items():
        for row in rows:
            provenance.append(
                {
                    "tenant_id": tenant_id,
                    "table": name,
                    "source_filename": filename,
                    "source_sha256": source_sha256,
                    "row": row["_row"],
                    "record_id": row[REQUIRED[name][0]],
                    "qualification": "EXTRACTED",
                    "inferred": False,
                }
            )
    dataset = {
        "tenant_id": tenant_id,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{k: row[k] for k in REQUIRED["jobs"]} for row in tables["jobs"]],
        "invoices": [{k: row[k] for k in REQUIRED["invoices"]} for row in tables["invoices"]],
        "rates": [{k: row[k] for k in REQUIRED["rates"]} for row in tables["rates"]],
        "payments": [{k: row[k] for k in REQUIRED["payments"]} for row in tables["payments"]],
        "equipment": [{k: row[k] for k in REQUIRED["equipment"]} for row in tables["equipment"]],
        "labor": [{k: row[k] for k in REQUIRED["labor"]} for row in tables["labor"]],
    }
    return {
        "schema": SCHEMA,
        "tenant_id": tenant_id,
        "source_sha256": source_sha256,
        "byte_length": len(bytes(raw)),
        "byte_length_scope": "RECEIVED_REQUEST_BYTES",
        "caller_declared_byte_length_accepted": False,
        "source_bytes_status": "VERIFIED_RECEIVED_BYTES",
        "source_identity": "UNVERIFIED",
        "filename": filename,
        "kind": kind,
        "processor": {"name": "dispater_ingest", "version": SCHEMA, "model": None, "ocr": "NOT_INSTALLED"},
        "field_provenance": field_provenance,
        "authority_state": "HOLD",
        "financial_authority": "NONE",
        "dataset": dataset,
        "provenance": provenance,
        "limits": "PDF text and XLSX cells are extracted locally. OCR is not installed. A model did not create these values.",
    }


def reject_unverified_parser(filename: str) -> None:
    """Formats without a reviewed parser are rejected by name."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix in {"pdf", "xlsx", "csv", "json"}:
        return
    if suffix in {"png", "jpg", "jpeg", "tif", "tiff"}:
        raise IngestError("OCR runtime is not installed; the image was not interpreted")
    raise IngestError("unsupported source type")


__all__ = ["SCHEMA", "IngestError", "ingest_source", "reject_unverified_parser"]
