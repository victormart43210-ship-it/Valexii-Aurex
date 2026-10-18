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
    assert record.has_missing_totals is False
    assert record.currency == "USD"
    assert len(record.line_items) == 1
    assert len(record.digest_sha256()) == 64


def test_financial_data_extraction_missing_totals_flag() -> None:
    sample = """Vendor Without Totals
Invoice #: INV-000
Date: 2026-10-15
No total line present.
"""
    record = extract_financial_data("doc-inv-002", sample)
    assert record.total_amount == 0.0
    assert record.has_missing_totals is True
