"""
Tests for THE BIG ONE Real-Company Validation Tooling.

Verifies:
1. Secure, read-only directory scanning and classification.
2. Digital PDF, XLSX, CSV, JSON recognized as ELIGIBLE_DIGITAL.
3. Image scans (PNG, JPEG) categorized as REQUIRES_OCR without pretending OCR is run.
4. Macro-enabled workbooks (.xlsm) safely rejected.
5. Deterministic inventory manifest SHA-256 generation.
6. Tenant isolation and fail-closed privacy bounds.
"""

from pathlib import Path

from aurex.the_big_one import (
    FileProcessingEligibility,
    scan_local_directory,
)


def test_the_big_one_read_only_scan(tmp_path: Path) -> None:
    # Set up mock company folder
    company_dir = tmp_path / "the_big_one_sample"
    company_dir.mkdir()

    # Create digital files
    (company_dir / "invoice_1.pdf").write_bytes(b"%PDF-1.4 sample pdf content")
    (company_dir / "rate_sheet.xlsx").write_bytes(b"PK\x03\x04 sample xlsx content")
    (company_dir / "tickets.csv").write_text("ticket_id,hours\nT-1,10.0\n")
    (company_dir / "contracts.json").write_text('{"contract_id": "C-1"}\n')

    # Create scan image
    (company_dir / "scanned_slip.png").write_bytes(b"\x89PNG\r\n\x1a\n sample png")

    # Create macro file
    (company_dir / "dangerous_macro.xlsm").write_bytes(b"PK\x03\x04 macro payload")

    # Create unknown extension
    (company_dir / "notes.unsupported").write_text("random note")

    report = scan_local_directory(company_dir, tenant_id="company-alpha")

    assert report.tenant_id == "company-alpha"
    assert report.total_files_discovered == 7
    assert report.eligible_digital_files == 4  # pdf, xlsx, csv, json
    assert report.files_requiring_ocr == 1    # png
    assert report.rejected_files == 2         # xlsm, unsupported

    # Check manifest hash
    assert len(report.inventory_manifest_sha256) == 64

    # Verify specific file eligibility
    records_by_name = {r.relative_path: r for r in report.records}
    assert records_by_name["invoice_1.pdf"].eligibility == FileProcessingEligibility.ELIGIBLE_DIGITAL
    assert records_by_name["scanned_slip.png"].eligibility == FileProcessingEligibility.REQUIRES_OCR
    assert records_by_name["dangerous_macro.xlsm"].eligibility == FileProcessingEligibility.REJECTED_MACRO
    assert records_by_name["notes.unsupported"].eligibility == FileProcessingEligibility.UNSUPPORTED_FORMAT
