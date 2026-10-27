from decimal import Decimal
import pytest
from dispater_reconciliation import reconcile_synthetic


def fixture():
    base = {"tenant_id": "synthetic-tenant", "synthetic": True}
    invoice = {**base, "id": "INV-1", "ticket_id": "T1", "po_id": "P1", "rate_id": "R1", "amount": "7500.00", "quantity": "10", "vendor_id": "V1", "external_number": "A"}
    ticket = {**base, "id": "T1", "signed": True}
    po = {**base, "id": "P1", "approved_amount": "7500.00"}
    rate = {**base, "id": "R1", "unit_rate": "750.00"}
    return invoice, ticket, po, rate


def test_clean_invoice_has_no_findings():
    i, t, p, r = fixture()
    assert reconcile_synthetic("synthetic-tenant", [i], [t], [p], [r]) == []


def test_missing_po_and_signature_require_review():
    i, t, p, r = fixture()
    t["signed"] = False
    findings = reconcile_synthetic("synthetic-tenant", [i], [t], [], [r])
    assert {f.code for f in findings} == {"MISSING_PO", "MISSING_SIGNATURE"}
    assert all(f.review_status == "HUMAN_REVIEW_REQUIRED" and len(f.evidence_hash) == 64 for f in findings)


def test_duplicate_invoice():
    i, t, p, r = fixture()
    second = {**i, "id": "INV-2"}
    assert "DUPLICATE_INVOICE" in {f.code for f in reconcile_synthetic("synthetic-tenant", [i, second], [t], [p], [r])}


def test_tenant_boundary_and_real_data_fail_closed():
    i, t, p, r = fixture()
    with pytest.raises(ValueError):
        reconcile_synthetic("other", [i], [t], [p], [r])
    i["synthetic"] = False
    with pytest.raises(ValueError):
        reconcile_synthetic("synthetic-tenant", [i], [t], [p], [r])


def test_rate_difference_and_invalid_amount():
    i, t, p, r = fixture()
    i["amount"] = "7000.00"
    findings = reconcile_synthetic("synthetic-tenant", [i], [t], [p], [r])
    assert next(f.exposure for f in findings if f.code == "RATE_MISMATCH") == "500.00"
    i["amount"] = "NaN"
    with pytest.raises(ValueError):
        reconcile_synthetic("synthetic-tenant", [i], [t], [p], [r])
