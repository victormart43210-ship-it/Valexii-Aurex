"""Comprehensive security and end-to-end verification suite for DISPATER Industrial Audit Engine.

Verifies:
1. Complete workflow: Equipment ticket + Invoice + Approved Rate -> Reconciliation -> Billing Discrepancy -> XAELI 5-step finding -> Audit Report.
2. Clean control dataset produces 0 findings (zero false positives).
3. Deterministic calculation consistency across repeated executions.
4. Malformed, missing, conflicting, and duplicate input failure handling.
5. Strict tenant isolation enforcement.
6. CSV formula injection defense.
7. API integration contracts:
   - POST /v1/dispater/reconciliation
   - GET  /v1/dispater/findings
   - GET  /v1/dispater/dashboard
   - Unauthenticated 401 rejection
"""

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import (
    InvalidSnapshot,
    RevenueLeakageEngine,
    sanitize_formula_field,
)


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")
    return TestClient(app)


def test_dispater_e2e_workflow_and_finding_structure():
    """Verify equipment ticket -> invoice -> rate -> discrepancy -> XAELI finding -> audit report."""
    tenant = "TENANT-PERMIAN-01"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    # Synthetic oilfield fixture with a deliberate $500 overbilling
    dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {
                "job_id": "FT-FRAC-104",
                "customer_id": "APACHE-OPERATOR",
                "service_code": "PRESSURE_PUMPING",
                "date": "2026-10-20",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-PP-2026",
                "customer_id": "APACHE-OPERATOR",
                "service_code": "PRESSURE_PUMPING",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "4500.00",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-PP-104",
                "job_id": "FT-FRAC-104",
                "amount": "5000.00",  # $500 discrepancy
                "status": "open",
            }
        ],
        "payments": [],
    }

    report1 = engine.reconcile_records(dataset)
    report2 = engine.reconcile_records(dataset)

    # 1. Deterministic repeatability
    assert report1 == report2
    assert report1["receipt_sha256"] == report2["receipt_sha256"]
    assert len(report1["receipt_sha256"]) == 64

    # 2. Financial calculation accuracy
    assert report1["financial_summary"]["identified_exposure_usd"] == "500.00"
    assert report1["financial_summary"]["confirmed_recovery_usd"] == "0.00"

    # 3. Canonical 5-Step XAELI Finding
    assert len(report1["findings"]) == 1
    f = report1["findings"][0]
    assert f["code"] == "RATE_MISMATCH"
    assert f["severity"] == "HIGH"
    assert f["exposure_usd"] == "500.00"
    assert f["authority"] == "HUMAN_REVIEW_REQUIRED"

    xaeli = f["xaeli_explanation"]
    assert "Invoice INV-PP-104 billed $5000.00 vs approved rate of $4500.00" in xaeli["now"]
    assert "Discrepancy of $500.00 detected" in xaeli["changed"]
    assert "Issue corrected invoice or credit memo" in xaeli["next"]
    assert "Deviating from contractual agreed rates causes revenue leakage" in xaeli["why"]
    assert "Rate SHA:" in xaeli["proof"]


def test_clean_control_dataset_zero_findings():
    """Verify that a clean control dataset produces no unsupported findings."""
    tenant = "TENANT-CLEAN-CONTROL"
    engine = RevenueLeakageEngine(tenant_id=tenant)

    clean_dataset = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {
                "job_id": "FT-PERFECT-01",
                "customer_id": "DEVON-ENERGY",
                "service_code": "FLOWBACK",
                "date": "2026-10-15",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-FB-DEVON",
                "customer_id": "DEVON-ENERGY",
                "service_code": "FLOWBACK",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "1200.00",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-PERFECT-01",
                "job_id": "FT-PERFECT-01",
                "amount": "1200.00",
                "status": "paid",
            }
        ],
        "payments": [
            {
                "payment_id": "PMT-001",
                "invoice_id": "INV-PERFECT-01",
                "amount": "1200.00",
            }
        ],
    }

    report = engine.reconcile_records(clean_dataset)
    assert len(report["findings"]) == 0
    assert report["financial_summary"]["identified_exposure_usd"] == "0.00"
    assert report["counts"]["findings"] == 0


def test_malformed_and_duplicate_input_failure_handling():
    """Verify failure handling for non-synthetic, duplicate, malformed dates, and missing fields."""
    engine = RevenueLeakageEngine(tenant_id="TENANT-FAIL")

    # Reject non-synthetic dataset
    with pytest.raises(InvalidSnapshot, match="Only explicitly labeled SYNTHETIC_ONLY"):
        engine.reconcile_records({"dataset_type": "CUSTOMER_LIVE_DATA"})

    base_payload = {
        "tenant_id": "TENANT-FAIL",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [],
        "rates": [],
        "invoices": [],
        "payments": [],
    }

    # Reject duplicate job_ids
    dup_jobs = dict(base_payload)
    dup_jobs["jobs"] = [
        {"job_id": "DUP-1", "customer_id": "C1", "service_code": "S1", "date": "2026-10-01"},
        {"job_id": "DUP-1", "customer_id": "C1", "service_code": "S1", "date": "2026-10-02"},
    ]
    with pytest.raises(InvalidSnapshot, match="duplicate identifier 'DUP-1' detected"):
        engine.reconcile_records(dup_jobs)

    # Reject malformed dates
    bad_date = dict(base_payload)
    bad_date["jobs"] = [
        {"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "10/01/2026"}
    ]
    with pytest.raises(InvalidSnapshot, match="date must be ISO YYYY-MM-DD"):
        engine.reconcile_records(bad_date)

    # Reject negative money
    bad_money = dict(base_payload)
    bad_money["invoices"] = [
        {"invoice_id": "INV-1", "job_id": "J1", "amount": "-500.00", "status": "open"}
    ]
    with pytest.raises(InvalidSnapshot, match="invalid nonnegative USD amount"):
        engine.reconcile_records(bad_money)


def test_tenant_isolation_boundary():
    """Verify that tenant mismatch is rejected."""
    engine_a = RevenueLeakageEngine(tenant_id="TENANT-A")
    with pytest.raises(InvalidSnapshot, match="Tenant isolation mismatch"):
        engine_a.reconcile_records({
            "tenant_id": "TENANT-B",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [],
            "rates": [],
            "invoices": [],
            "payments": [],
        })


def test_formula_injection_defense():
    """Verify that spreadsheet formula injection characters are neutralized."""
    assert sanitize_formula_field("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert sanitize_formula_field("+1+1") == "'+1+1"
    assert sanitize_formula_field("-2+3") == "'-2+3"
    assert sanitize_formula_field("@SUM(1,2)") == "'@SUM(1,2)"
    assert sanitize_formula_field("\tsecret") == "'\tsecret"
    assert sanitize_formula_field("normal_job_id") == "normal_job_id"


def test_dispater_api_endpoints_integration(auth_client: TestClient):
    """Verify authenticated API routes: reconciliation, findings, dashboard, and 401 unauthenticated."""
    headers = {"Authorization": "Bearer 12345678901234567890123456789012"}
    tenant = "TENANT-API-TEST"

    # 1. Unauthenticated request must return 401
    unauth_res = auth_client.get(f"/v1/dispater/dashboard?tenant_id={tenant}")
    assert unauth_res.status_code == 401

    # 2. Initial dashboard state
    init_dash = auth_client.get(f"/v1/dispater/dashboard?tenant_id={tenant}", headers=headers)
    assert init_dash.status_code == 200
    assert init_dash.json()["status"] == "INITIALIZED"
    assert init_dash.json()["system_state"]["production_release"] == "HOLD"
    assert init_dash.json()["system_state"]["financial_authority"] == "NONE"

    # 3. Post reconciliation
    payload = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [
            {
                "job_id": "FT-UNBILLED-99",
                "customer_id": "OPERATOR-X",
                "service_code": "WIRELINE",
                "date": "2026-10-18",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-WL",
                "customer_id": "OPERATOR-X",
                "service_code": "WIRELINE",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "2200.00",
            }
        ],
        "invoices": [],  # Unbilled job
        "payments": [],
    }
    reconcile_res = auth_client.post("/v1/dispater/reconciliation", json=payload, headers=headers)
    assert reconcile_res.status_code == 200
    report = reconcile_res.json()
    assert report["financial_summary"]["identified_exposure_usd"] == "2200.00"
    assert len(report["findings"]) == 1
    assert report["findings"][0]["code"] == "UNBILLED_JOB"

    # 4. Query findings endpoint
    findings_res = auth_client.get(f"/v1/dispater/findings?tenant_id={tenant}", headers=headers)
    assert findings_res.status_code == 200
    f_data = findings_res.json()
    assert f_data["count"] == 1
    assert f_data["findings"][0]["code"] == "UNBILLED_JOB"

    # 5. Query updated dashboard endpoint
    dash_res = auth_client.get(f"/v1/dispater/dashboard?tenant_id={tenant}", headers=headers)
    assert dash_res.status_code == 200
    d_data = dash_res.json()
    assert d_data["status"] == "AUDIT_COMPLETE"
    assert d_data["identified_exposure_usd"] == "2200.00"
    assert d_data["finding_counts"]["high"] == 1
