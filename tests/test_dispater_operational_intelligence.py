"""
Unit, security, and synthetic E2E scenario tests for DISPATER Sovereign Operational Intelligence engine (Scenarios A-H).
"""

from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_intelligence import (
    CalculatorAssumptions,
    FleetMaintenanceEngine,
    IntegrationFoundationAdapters,
    OperationalValueCalculator,
    RevenueLeakageEngine,
)

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer 12345678901234567890123456789012"}


def test_scenario_a_unbilled_twelve_thousand_job():
    """Scenario A: Completed $12,000 field job with no invoice."""
    tickets = [{"ticket_id": "FT-A1", "po_id": "PO-10", "invoice_id": None, "total_amount": 12000.0}]
    invoices = []
    pos = [{"po_id": "PO-10", "amount_limit": 15000.0}]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-A", tickets, invoices, pos, [])
    unbilled_excs = [e for e in excs if e.rule_type == "UNBILLED_FIELD_TICKET"]
    assert len(unbilled_excs) == 1
    assert unbilled_excs[0].financial_exposure == 12000.0


def test_scenario_b_missing_po_invoice():
    """Scenario B: $7,500 field job with missing purchase order."""
    tickets = [{"ticket_id": "FT-B1", "po_id": None, "invoice_id": "INV-B1", "total_amount": 7500.0}]
    invoices = [{"invoice_id": "INV-B1", "total_amount": 7500.0}]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-B", tickets, invoices, [], [])
    po_excs = [e for e in excs if e.rule_type == "UNMATCHED_PO"]
    assert len(po_excs) == 1
    assert po_excs[0].financial_exposure == 7500.0


def test_scenario_c_rate_discrepancy():
    """Scenario C: Contract rate differs from invoiced rate."""
    tickets = []
    invoices = [{
        "invoice_id": "INV-C1",
        "vendor_or_customer": "Customer C",
        "total_amount": 3000.0,
        "line_items": [{"rate_code": "CRANE-HR", "unit_rate": 300.0, "quantity": 10}],
    }]
    rates = [{"rate_code": "CRANE-HR", "approved_rate": 200.0}]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-C", tickets, invoices, [], rates)
    rate_excs = [e for e in excs if e.rule_type == "RATE_DISCREPANCY"]
    assert len(rate_excs) == 1
    assert rate_excs[0].financial_exposure == 1000.0


def test_scenario_d_duplicate_invoice():
    """Scenario D: Duplicate supplier invoice."""
    invoices = [
        {"invoice_id": "INV-D1", "vendor_or_customer": "Vendor D", "total_amount": 4500.0, "line_items": []},
        {"invoice_id": "INV-D2", "vendor_or_customer": "Vendor D", "total_amount": 4500.0, "line_items": []},
    ]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-D", [], invoices, [], [])
    dup_excs = [e for e in excs if e.rule_type == "DUPLICATE_INVOICE"]
    assert len(dup_excs) == 1
    assert dup_excs[0].financial_exposure == 4500.0


def test_scenario_e_pump_maintenance_overdue():
    """Scenario E: Pump maintenance overdue by 200 operating hours."""
    fleet = [{
        "equipment_id": "PUMP-101",
        "equipment_name": "Triplex Mud Pump 101",
        "operating_hours": 450.0,
        "last_service_hours": 0.0,
        "service_threshold_hours": 250.0,
        "current_mileage": 0.0,
        "last_service_mileage": 0.0,
        "has_inspection_record": True,
        "detected_defects": [],
    }]
    recs = FleetMaintenanceEngine.evaluate_fleet("TENANT-E", fleet)
    assert len(recs) == 1
    assert recs[0].status == "OVERDUE_SERVICE"
    assert recs[0].priority_classification == "CRITICAL"


def test_scenario_f_unbilled_equipment_materials():
    """Scenario F: Unbilled equipment and materials."""
    tickets = [{
        "ticket_id": "FT-F1",
        "po_id": "PO-F",
        "invoice_id": "INV-F",
        "total_amount": 5000.0,
        "items": [
            {"name": "Hydraulic Winch Unit", "subtotal": 1200.0, "billed": False},
            {"name": "Synthetic Slings", "subtotal": 300.0, "billed": False},
        ],
    }]
    pos = [{"po_id": "PO-F", "amount_limit": 10000.0}]
    invoices = [{"invoice_id": "INV-F", "total_amount": 5000.0}]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-F", tickets, invoices, pos, [])
    item_excs = [e for e in excs if e.rule_type == "UNBILLED_ITEMS"]
    assert len(item_excs) == 1
    assert item_excs[0].financial_exposure == 1500.0


def test_scenario_g_tenant_isolation(monkeypatch):
    """Scenario G: Cross-tenant data access attempt."""
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")

    resp_a = client.post(
        "/v1/dispater/reconciliation",
        headers=AUTH_HEADER,
        json={"tenant_id": "TENANT-ALPHA", "field_tickets": [{"ticket_id": "FT-A", "po_id": None, "total_amount": 100.0}]},
    )
    resp_b = client.post(
        "/v1/dispater/reconciliation",
        headers=AUTH_HEADER,
        json={"tenant_id": "TENANT-BETA", "field_tickets": [{"ticket_id": "FT-B", "po_id": None, "total_amount": 200.0}]},
    )
    assert resp_a.json()["tenant_id"] == "TENANT-ALPHA"
    assert resp_b.json()["tenant_id"] == "TENANT-BETA"
    assert resp_a.json()["exceptions"][0]["tenant_id"] == "TENANT-ALPHA"
    assert resp_b.json()["exceptions"][0]["tenant_id"] == "TENANT-BETA"


def test_scenario_h_missing_evidence_and_malformed():
    """Scenario H: Missing evidence and malformed financial records."""
    tickets = [{
        "ticket_id": "FT-H1",
        "po_id": "PO-H",
        "invoice_id": "INV-H",
        "total_amount": 2500.0,
        "evidence_valid": False,  # Missing evidence
    }]
    pos = [{"po_id": "PO-H", "amount_limit": 5000.0}]
    invoices = [{"invoice_id": "INV-H", "total_amount": 2500.0}]
    excs = RevenueLeakageEngine.evaluate_records("TENANT-H", tickets, invoices, pos, [])
    evd_excs = [e for e in excs if e.rule_type == "MISSING_CONFLICTING_EVIDENCE"]
    assert len(evd_excs) == 1


def test_value_calculator_and_accounting_export():
    assumptions = CalculatorAssumptions(monthly_job_volume=150, avg_ticket_value=2500.0)
    calc_res = OperationalValueCalculator.calculate_value("TENANT-COMMERCIAL-01", assumptions)
    assert calc_res.total_estimated_monthly_value > 0.0

    excs = RevenueLeakageEngine.evaluate_records("TENANT-COMMERCIAL-01", [{"ticket_id": "FT-1", "po_id": None, "total_amount": 500.0}], [], [], [])
    acc_export = IntegrationFoundationAdapters.export_accounting_format(excs)
    assert acc_export["adjustments_count"] >= 1
    assert acc_export["entries"][0]["status"] == "REQUIRES_HUMAN_APPROVAL"
