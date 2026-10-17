from aurex.financial_extractor import extract_financial_data


def test_financial_data_extraction_sample_invoice() -> None:
    sample = """ACME Cyber Solutions Inc.
Invoice #: INV-2026-089
Date: 2026-10-15
Line Items:
Security Audit Services 1 x 500.00 = 500.00
Tax: 0.00
Total: 500.00 USD
"""
    record = extract_financial_data("doc-inv-001", sample)
    assert record.document_id == "doc-inv-001"
    assert record.vendor_name == "ACME Cyber Solutions Inc."
    assert record.invoice_number == "INV-2026-089"
    assert record.invoice_date == "2026-10-15"
    assert record.total_amount == 500.00
    assert record.currency == "USD"
    assert len(record.line_items) == 1
    assert record.line_items[0].description == "Security Audit Services"
    assert len(record.digest_sha256()) == 64
