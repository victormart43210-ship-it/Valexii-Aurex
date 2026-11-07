"""Test suite for DISPATER audit readiness and reproducible evidence package exports."""

from datetime import date

from aurex.dispater_audit_package import (
    FMCSA_REQUIREMENTS,
    AuditPackageEngine,
    digest_object,
)


def test_audit_package_engine_freshness_and_missing_exceptions():
    """Verify missing document identification and expiration tracking."""
    engine = AuditPackageEngine("tow-tenant-1")

    vehicles = [{"vehicle_id": "TRUCK-01"}, {"vehicle_id": "TRUCK-02"}]
    drivers = [{"driver_id": "DRV-ALICE"}, {"driver_id": "DRV-BOB"}]
    documents = [
        {
            "document_id": "DOC-ALICE-MED",
            "driver_id": "DRV-ALICE",
            "type": "MEDICAL_EXAMINER_CERT",
            "issued_date": "2025-01-01",
            "expiration_date": "2027-01-01",
        },
        {
            "document_id": "DOC-TRUCK1-INSP",
            "vehicle_id": "TRUCK-01",
            "type": "ANNUAL_INSPECTION",
            "issued_date": "2025-07-01",
            "expiration_date": "2026-07-01",
        },
        {
            "document_id": "DOC-TRUCK2-INSP",
            "vehicle_id": "TRUCK-02",
            "type": "ANNUAL_INSPECTION",
            "issued_date": "2024-05-01",
            "expiration_date": "2025-05-01",  # Expired as of 2026
        },
    ]

    as_of = date(2026, 6, 1)
    eval_res = engine.evaluate_compliance(documents, vehicles, drivers, as_of_date=as_of)

    assert eval_res["counts"]["documents_inventoried"] == 3
    assert eval_res["counts"]["unresolved_exceptions"] == 2

    # Expect: 1 missing med cert for DRV-BOB, 1 expired inspection for TRUCK-02
    exc_ids = [e["exception_id"] for e in eval_res["exceptions"]]
    assert "EXC-MED-DRV-BOB" in exc_ids
    assert "EXC-EXP-INSP-DOC-TRUCK2-INSP" in exc_ids


def test_reproducible_audit_package_manifest_digest():
    """Verify deterministic manifest creation and integrity receipt."""
    engine = AuditPackageEngine("tow-tenant-1")

    eval_res = engine.evaluate_compliance([], [], [], as_of_date=date(2026, 6, 1))
    recon_report = {"financial_summary": {"identified_exposure_usd": "100.00"}}

    pkg_a = engine.export_audit_package(eval_res, recon_report)
    assert "manifest_sha256" in pkg_a
    assert "package_receipt_sha256" in pkg_a
    assert pkg_a["authority_state"] == "ADVISORY_ONLY"

    # Manifest verification
    manifest = pkg_a["manifest"]
    computed_manifest_digest = digest_object(manifest)
    assert pkg_a["manifest_sha256"] == computed_manifest_digest

    # Receipt verification
    body = {k: v for k, v in pkg_a.items() if k != "package_receipt_sha256"}
    assert digest_object(body) == pkg_a["package_receipt_sha256"]


def test_fmcsa_jurisdiction_catalog():
    """Verify DOT/FMCSA rules have explicit statutory citation and applicability."""
    for reg, details in FMCSA_REQUIREMENTS.items():
        assert details["jurisdiction"] == "US_DOT_FMCSA"
        assert len(details["applicability"]) > 10
        assert "category" in details
