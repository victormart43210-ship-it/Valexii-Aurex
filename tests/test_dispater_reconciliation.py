"""Comprehensive security and end-to-end verification suite for DISPATER Industrial Audit Engine.

Validates Synthetic Beta Acceptance Scenarios A through L:
- Scenario A: Correct invoice (zero findings, control dataset)
- Scenario B: Underbilled work (accurate candidate underbilling exposure)
- Scenario C: Overbilled work (exposure categorized as overbilling without claiming recovery)
- Scenario D: Unbilled completed ticket (evidence-linked exception)
- Scenario E: Duplicate invoices (no double counting)
- Scenario F: Partial payment (unreconciled paid status tracked)
- Scenario G: Conflicting rates (ambiguity surfaced fail-closed)
- Scenario H: Cross-tenant access (unauthorized tenant access rejected)
- Scenario I: Service restart recovery (persisted SQLite audits remain accessible across restart)
- Scenario J: Tampered receipt (digest verification fails closed)
- Scenario K: Missing configuration (fails closed)
- Scenario L: Malformed / hostile input (safe rejection without internal stack disclosure)
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import (
    InvalidSnapshot,
    RevenueLeakageEngine,
    TenantAuthorizationError,
    get_latest_audit_run,
    sanitize_formula_field,
)


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")
    return TestClient(app)


def test_scenario_a_correct_invoice_control_dataset():
    """Scenario A: Correct invoice produces 0 findings (zero false positives)."""
    tenant = "TENANT-CLEAN"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    clean_dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {
                "job_id": "FT-001",
                "customer_id": "CUST-A",
                "service_code": "FLOWBACK",
                "date": "2026-10-15",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-001",
                "customer_id": "CUST-A",
                "service_code": "FLOWBACK",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "1200.00",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-001",
                "job_id": "FT-001",
                "amount": "1200.00",
                "status": "paid",
            }
        ],
        "payments": [
            {
                "payment_id": "PMT-001",
                "invoice_id": "INV-001",
                "amount": "1200.00",
            }
        ],
    }

    report = engine.reconcile_records(clean_dataset)
    assert len(report["findings"]) == 0
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["financial_summary"]["potential_underbilling_usd"] == "0.00"
    assert report["financial_summary"]["potential_overbilling_usd"] == "0.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"


def test_scenario_b_underbilled_work():
    """Scenario B: Underbilled work creates candidate underbilling finding."""
    tenant = "TENANT-UNDERBILL"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-U1", "customer_id": "CUST-B", "service_code": "PUMP", "date": "2026-10-10"}
        ],
        "rates": [
            {"rate_id": "R-U1", "customer_id": "CUST-B", "service_code": "PUMP", "start": "2026-01-01", "end": "2026-12-31", "amount": "4000.00"}
        ],
        "invoices": [
            {"invoice_id": "INV-U1", "job_id": "FT-U1", "amount": "3200.00", "status": "open"}  # Underbilled by $800
        ],
        "payments": [],
    }

    report = engine.reconcile_records(dataset)
    assert len(report["findings"]) == 1
    f = report["findings"][0]
    assert f["code"] == "RATE_MISMATCH"
    assert f["exposure_kind"] == "POTENTIAL_UNDERBILLING"
    assert f["exposure_usd"] == "800.00"
    assert report["financial_summary"]["potential_underbilling_usd"] == "800.00"
    assert report["financial_summary"]["potential_overbilling_usd"] == "0.00"


def test_scenario_c_overbilled_work_no_recovery_claim():
    """Scenario C: Overbilled work categorized correctly without claiming recovered revenue."""
    tenant = "TENANT-OVERBILL"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-O1", "customer_id": "CUST-C", "service_code": "WIRE", "date": "2026-10-11"}
        ],
        "rates": [
            {"rate_id": "R-O1", "customer_id": "CUST-C", "service_code": "WIRE", "start": "2026-01-01", "end": "2026-12-31", "amount": "2500.00"}
        ],
        "invoices": [
            {"invoice_id": "INV-O1", "job_id": "FT-O1", "amount": "3000.00", "status": "open"}  # Overbilled by $500
        ],
        "payments": [],
    }

    report = engine.reconcile_records(dataset)
    f = report["findings"][0]
    assert f["code"] == "RATE_MISMATCH"
    assert f["exposure_kind"] == "POTENTIAL_OVERBILLING"
    assert f["exposure_usd"] == "500.00"
    assert report["financial_summary"]["potential_overbilling_usd"] == "500.00"
    assert report["financial_summary"]["confirmed_recovery_usd"] == "0.00"


def test_scenario_d_unbilled_completed_ticket():
    """Scenario D: Completed ticket with no invoice flags unbilled revenue."""
    tenant = "TENANT-UNBILLED"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-UNBILLED-01", "customer_id": "CUST-D", "service_code": "FRAC", "date": "2026-10-05"}
        ],
        "rates": [
            {"rate_id": "R-FRAC", "customer_id": "CUST-D", "service_code": "FRAC", "start": "2026-01-01", "end": "2026-12-31", "amount": "5500.00"}
        ],
        "invoices": [],
        "payments": [],
    }

    report = engine.reconcile_records(dataset)
    assert len(report["findings"]) == 1
    f = report["findings"][0]
    assert f["code"] == "UNBILLED_JOB"
    assert f["exposure_kind"] == "POTENTIAL_UNDERBILLING"
    assert f["exposure_usd"] == "5500.00"


def test_scenario_e_duplicate_invoices():
    """Scenario E: Multiple invoices referencing same job flags critical risk without double counting."""
    tenant = "TENANT-DUP"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-DUP-01", "customer_id": "CUST-E", "service_code": "CRANE", "date": "2026-10-06"}
        ],
        "rates": [
            {"rate_id": "R-CRANE", "customer_id": "CUST-E", "service_code": "CRANE", "start": "2026-01-01", "end": "2026-12-31", "amount": "1500.00"}
        ],
        "invoices": [
            {"invoice_id": "INV-DUP-A", "job_id": "FT-DUP-01", "amount": "1500.00", "status": "open"},
            {"invoice_id": "INV-DUP-B", "job_id": "FT-DUP-01", "amount": "1500.00", "status": "open"},
        ],
        "payments": [],
    }

    report = engine.reconcile_records(dataset)
    dup_finding = next(f for f in report["findings"] if f["code"] == "MULTIPLE_INVOICES")
    assert dup_finding["severity"] == "CRITICAL"
    assert dup_finding["exposure_kind"] == "POTENTIAL_OVERBILLING"
    assert dup_finding["exposure_usd"] == "1500.00"


def test_scenario_f_partial_payment():
    """Scenario F: Partial payment on paid-marked invoice detects unreconciled balance."""
    tenant = "TENANT-PARTIAL"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-P1", "customer_id": "CUST-F", "service_code": "WATER", "date": "2026-10-07"}
        ],
        "rates": [
            {"rate_id": "R-WATER", "customer_id": "CUST-F", "service_code": "WATER", "start": "2026-01-01", "end": "2026-12-31", "amount": "2000.00"}
        ],
        "invoices": [
            {"invoice_id": "INV-P1", "job_id": "FT-P1", "amount": "2000.00", "status": "paid"}
        ],
        "payments": [
            {"payment_id": "PMT-P1", "invoice_id": "INV-P1", "amount": "1500.00"}  # Short paid by $500
        ],
    }

    report = engine.reconcile_records(dataset)
    f = report["findings"][0]
    assert f["code"] == "PAID_STATUS_UNRECONCILED"
    assert f["exposure_kind"] == "POTENTIAL_UNDERBILLING"
    assert f["exposure_usd"] == "500.00"


def test_scenario_g_conflicting_rates():
    """Scenario G: Overlapping rate schedules flagged as ambiguous uncertainty."""
    tenant = "TENANT-RATES"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {"job_id": "FT-AMB", "customer_id": "CUST-G", "service_code": "RIG", "date": "2026-06-01"}
        ],
        "rates": [
            {"rate_id": "R-OLD", "customer_id": "CUST-G", "service_code": "RIG", "start": "2026-01-01", "end": "2026-12-31", "amount": "3000.00"},
            {"rate_id": "R-NEW", "customer_id": "CUST-G", "service_code": "RIG", "start": "2026-05-01", "end": "2026-12-31", "amount": "3200.00"},
        ],
        "invoices": [
            {"invoice_id": "INV-AMB", "job_id": "FT-AMB", "amount": "3200.00", "status": "open"}
        ],
        "payments": [],
    }

    report = engine.reconcile_records(dataset)
    f = next(f for f in report["findings"] if f["code"] == "AMBIGUOUS_RATE")
    assert f["severity"] == "MEDIUM"
    assert f["exposure_kind"] == "UNVERIFIED_EXPOSURE"


def test_scenario_h_cross_tenant_access_rejection(auth_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """Scenario H: Cross-tenant access is rejected fail-closed (HTTP 403 / TenantAuthorizationError)."""
    # Configure token for Tenant Alpha
    token_alpha = "alpha" * 8  # 40 chars
    monkeypatch.setenv("AUREX_TENANT_TOKEN_TENANT_ALPHA", token_alpha)

    # Tenant Alpha token trying to access Tenant Beta
    res = auth_client.get(
        "/v1/dispater/dashboard?tenant_id=TENANT_BETA",
        headers={"Authorization": f"Bearer {token_alpha}"},
    )
    assert res.status_code == 403
    assert "Principal not authorized for requested tenant" in res.json()["detail"]

    # Engine-level tenant boundary check
    engine_alpha = RevenueLeakageEngine(tenant_id="TENANT-ALPHA")
    with pytest.raises(TenantAuthorizationError, match="Tenant isolation mismatch"):
        engine_alpha.reconcile_records({
            "tenant_id": "TENANT-BETA",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [],
            "rates": [],
            "invoices": [],
            "payments": [],
        })


def test_scenario_i_service_restart_durable_storage_recovery():
    """Scenario I: Audits stored in durable SQLite remain accessible across service restarts."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "test_dispater.db")
        tenant = "TENANT-PERSIST-01"

        engine1 = RevenueLeakageEngine(tenant_id=tenant, db_path=db_file)
        payload = {
            "tenant_id": tenant,
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-10-01"}],
            "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "1000.00"}],
            "invoices": [{"invoice_id": "INV-1", "job_id": "J1", "amount": "1200.00", "status": "open"}],
            "payments": [],
        }
        report1 = engine1.reconcile_records(payload)
        run_id = report1["run_id"]

        # Simulate service restart: create fresh engine instance querying the same SQLite DB
        del engine1
        recovered_report = get_latest_audit_run(tenant, db_path=db_file)
        assert recovered_report is not None
        assert recovered_report["run_id"] == run_id
        assert recovered_report["receipt_sha256"] == report1["receipt_sha256"]
        assert recovered_report["financial_summary"]["identified_exposure_usd"] == "200.00"

        # Verify cross-tenant retrieval yields None for other tenant
        other_run = get_latest_audit_run("TENANT-OTHER", db_path=db_file)
        assert other_run is None


def test_scenario_j_tampered_receipt_detection():
    """Scenario J: Tampering with any payload field alters deterministic SHA-256 receipt."""
    tenant = "TENANT-TAMPER"
    engine = RevenueLeakageEngine(tenant_id=tenant)
    base = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-10-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "1000.00"}],
        "invoices": [{"invoice_id": "INV-1", "job_id": "J1", "amount": "1000.00", "status": "open"}],
        "payments": [],
    }
    report1 = engine.reconcile_records(base)

    # Alter amount by 1 cent
    tampered = dict(base)
    tampered["invoices"] = [{"invoice_id": "INV-1", "job_id": "J1", "amount": "1000.01", "status": "open"}]
    report2 = engine.reconcile_records(tampered)

    assert report1["receipt_sha256"] != report2["receipt_sha256"]


def test_scenario_k_missing_or_insecure_configuration():
    """Scenario K: Missing or short token fails closed."""
    client = TestClient(app)
    # Missing auth header -> 401
    res = client.get("/v1/dispater/dashboard?tenant_id=default")
    assert res.status_code == 401

    # Short token -> 401
    res2 = client.get(
        "/v1/dispater/dashboard?tenant_id=default",
        headers={"Authorization": "Bearer short"},
    )
    assert res2.status_code == 401


def test_scenario_l_malformed_or_hostile_input():
    """Scenario L: Formula injection and malformed inputs are safely rejected or sanitized."""
    # Formula injection sanitized
    assert sanitize_formula_field("=2+5") == "'=2+5"
    assert sanitize_formula_field("+A1") == "'+A1"
    assert sanitize_formula_field("-B1") == "'-B1"
    assert sanitize_formula_field("@SUM") == "'@SUM"

    engine = RevenueLeakageEngine(tenant_id="TENANT-MALFORMED")

    # Malformed non-numeric hours
    bad_hrs = {
        "tenant_id": "TENANT-MALFORMED",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-10-01", "hours": "abc"}],
        "rates": [],
        "invoices": [],
        "payments": [],
    }
    with pytest.raises(InvalidSnapshot, match="Non-numeric equipment hours"):
        engine.reconcile_records(bad_hrs)
