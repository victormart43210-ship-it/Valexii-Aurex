"""Unit tests for IBM Docling document extraction and security validation."""

from __future__ import annotations

import json

import pytest

from aurex.docling_adapter import (
    DocumentValidationError,
    extract_industrial_document,
    validate_document_input,
)
from workstation.docling_lab import run_synthetic_benchmark


def test_valid_json_document_extraction() -> None:
    doc = {
        "ticket_id": "FT-901",
        "vendor": "Midland Drilling Co",
        "wellsite": "Pad C-3",
        "date": "2026-10-22",
        "hours": 10,
        "rate_per_hour": 200,
        "total_cents": 200000,
    }
    content = json.dumps(doc).encode("utf-8")
    res = extract_industrial_document(content, "ticket.json", doc_type="field_ticket")

    assert res["status"] == "EXTRACTED_NOT_VERIFIED"
    assert res["sha256"] is not None
    assert len(res["sha256"]) == 64
    assert res["fields"]["ticket_id"] == "FT-901"
    assert res["missing_fields"] == []
    assert res["authority"] == "NONE"


def test_towing_invoice_total_calculation() -> None:
    doc = {
        "invoice_id": "TOW-808",
        "vendor": "Apex Towing Services",
        "vehicle_vin": "1FA6P8CF0R1000002",
        "towing_cents": 25000,
        "storage_cents": 10000,
        "total_cents": 35000,
    }
    content = json.dumps(doc).encode("utf-8")
    res = extract_industrial_document(content, "tow.json", doc_type="towing_invoice")

    assert res["calculated_total_cents"] == 35000
    assert res["confidence_scores"]["invoice_id"] == 1.0


def test_missing_field_detection() -> None:
    incomplete = {
        "ticket_id": "FT-902",
        "vendor": "Midland Drilling Co",
        # missing hours, rate, date
    }
    content = json.dumps(incomplete).encode("utf-8")
    res = extract_industrial_document(content, "incomplete.json", doc_type="field_ticket")

    assert "date" in res["missing_fields"]
    assert "hours" in res["missing_fields"]
    assert res["confidence_scores"]["date"] == 0.0


def test_executable_script_file_rejection() -> None:
    with pytest.raises(DocumentValidationError, match="Forbidden file extension"):
        validate_document_input(b"echo 'evil'", "malicious.sh")

    with pytest.raises(DocumentValidationError, match="Executable script content"):
        validate_document_input(b"#!/bin/bash\nrm -rf /", "data.txt")


def test_docling_synthetic_benchmark() -> None:
    report = run_synthetic_benchmark()
    assert report["status"] == "BENCHMARK_COMPLETE"
    assert report["accuracy_pct"] == 100.0
    assert report["total_documents"] == 2
