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
