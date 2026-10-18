from aurex.financial_extractor import extract_financial_data


def test_financial_data_extraction_subtotal_and_total() -> None:
    sample = """ACME Cyber Solutions Inc.
Invoice #: INV-2026-089
Date: 2026-10-15
Line Items:
Security Audit Services 1 x 500.00 = 500.00
Subtotal: 500.00
Tax: 25.00
Grand Total: 525.00 USD
"""
    record = extract_financial_data("doc-inv-001", sample)
    assert record.document_id == "doc-inv-001"
    assert record.vendor_name == "ACME Cyber Solutions Inc."
    assert record.invoice_number == "INV-2026-089"
    assert record.invoice_date == "2026-10-15"
    assert record.subtotal_amount == 500.00
    assert record.tax_amount == 25.00
    assert record.total_amount == 525.00
    assert record.subtotal_present is True
    assert record.final_total_present is True
    assert record.has_missing_totals is False
    assert record.consistency_result == "CONSISTENT"
    assert record.currency == "USD"
    assert len(record.line_items) == 1


def test_line_item_change_alters_digest() -> None:
    sample_a = """Vendor A
Invoice #: INV-1
Line Items:
Item One 1 x 100.00 = 100.00
Total: 100.00
"""
    sample_b = """Vendor A
Invoice #: INV-1
Line Items:
Item Two 1 x 100.00 = 100.00
Total: 100.00
"""
    rec_a = extract_financial_data("doc-01", sample_a)
    rec_b = extract_financial_data("doc-01", sample_b)
    assert rec_a.digest_sha256() != rec_b.digest_sha256()


def test_test_d_subtotal_without_final_total() -> None:
    sample_d = """Vendor: Example Oilfield LLC
Invoice #1234
Date 10/17/2026
Subtotal $500.00
"""
    rec = extract_financial_data("doc-d", sample_d)
    assert rec.subtotal_present is True
    assert rec.final_total_present is False
    assert rec.has_missing_totals is False


def test_discrepancy_detection() -> None:
    sample_disc = """Vendor Discrepancy
Invoice #: INV-DISC
Subtotal: 100.00
Tax: 10.00
Grand Total: 150.00
"""
    rec = extract_financial_data("doc-disc", sample_disc)
    assert rec.consistency_result == "DISCREPANCY"
