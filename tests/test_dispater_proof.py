from dispater_proof.reconcile import demo, reconcile


def test_synthetic_seeded_findings():
    codes = {finding.code for finding in demo()}
    assert codes == {"DUPLICATE_INVOICE_ID", "MISSING_DISPATCH", "MILEAGE_MISMATCH"}


def test_clean_record_has_no_findings():
    dispatches = [{"dispatch_id": "D1", "miles": "2"}]
    invoices = [{"invoice_id": "I1", "dispatch_id": "D1", "miles": "2", "base_charge": "5", "rate_per_mile": "2", "total": "9"}]
    assert reconcile(dispatches, invoices) == []


def test_invalid_amount_is_flagged():
    dispatches = [{"dispatch_id": "D1", "miles": "2"}]
    invoices = [{"invoice_id": "I1", "dispatch_id": "D1", "miles": "2", "base_charge": "5", "rate_per_mile": "oops", "total": "9"}]
    assert any(f.code == "INVALID_AMOUNT" for f in reconcile(dispatches, invoices))


def test_duplicate_dispatch_id_is_ambiguous_regardless_of_row_order():
    dispatches = [
        {"dispatch_id": "D1", "miles": "8"},
        {"dispatch_id": "D1", "miles": "12"},
    ]
    invoices = [{"invoice_id": "I1", "dispatch_id": "D1", "miles": "12"}]

    findings = reconcile(dispatches, invoices)

    assert [finding.code for finding in findings] == ["AMBIGUOUS_DISPATCH"]
    assert reconcile(list(reversed(dispatches)), invoices) == findings


def test_out_of_range_amount_does_not_abort_later_invoice():
    dispatches = [{"dispatch_id": "D1", "miles": "2"}]
    invoices = [
        {
            "invoice_id": "I1",
            "dispatch_id": "D1",
            "miles": "2",
            "base_charge": "1E+26",
            "rate_per_mile": "0",
            "total": "1E+26",
        },
        {
            "invoice_id": "I2",
            "dispatch_id": "D1",
            "miles": "2",
            "base_charge": "5",
            "rate_per_mile": "2",
            "total": "9",
        },
    ]

    findings = reconcile(dispatches, invoices)

    assert [(finding.invoice_id, finding.code) for finding in findings] == [
        ("I1", "INVALID_AMOUNT")
    ]
