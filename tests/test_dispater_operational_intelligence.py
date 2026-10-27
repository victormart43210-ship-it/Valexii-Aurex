"""
Unit and security tests for DISPATER Sovereign Operational Intelligence engine.
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


def test_revenue_leakage_engine_six_rules():
    tenant_id = "TENANT-TEST-01"
    field_tickets = [
        {
            "ticket_id": "FT-101",
            "po_id": None,  # Rule 1: UNMATCHED_PO
            "invoice_id": None,  # Rule 2: UNBILLED_FIELD_TICKET
            "total_amount": 1500.0,
            "has_customer_signature": False,  # Rule 5: MISSING_SIGNATURE
            "items": [
                {"name": "Heavy Winch Labor", "subtotal": 500.0, "billed": False},  # Rule 6: UNBILLED_ITEMS
            ],
        }
    ]
    invoices = [
        {
            "invoice_id": "INV-201",
            "vendor_or_customer": "ACME Oilfield",
            "total_amount": 3500.0,
            "line_items": [
                {"rate_code": "CRANE-HR", "unit_rate": 250.0, "quantity": 10},  # Rule 3: RATE_DISCREPANCY (master rate = 200.0)
            ],
        },
        {
            "invoice_id": "INV-202",
            "vendor_or_customer": "ACME Oilfield",
            "total_amount": 3500.0,  # Rule 4: DUPLICATE_INVOICE
            "line_items": [],
        },
    ]
    purchase_orders = []
    rate_sheets = [{"rate_code": "CRANE-HR", "approved_rate": 200.0}]

    exceptions = RevenueLeakageEngine.evaluate_records(
        tenant_id=tenant_id,
        field_tickets=field_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
        is_demo=True,
    )

    rule_types = {e.rule_type for e in exceptions}
    assert "UNMATCHED_PO" in rule_types
    assert "UNBILLED_FIELD_TICKET" in rule_types
    assert "MISSING_SIGNATURE" in rule_types
    assert "UNBILLED_ITEMS" in rule_types
    assert "DUPLICATE_INVOICE" in rule_types
    assert "RATE_DISCREPANCY" in rule_types
    assert len(exceptions) >= 6


def test_fleet_maintenance_engine():
    fleet_data = [
        {
            "equipment_id": "RIG-01",
            "equipment_name": "Drilling Rig 01",
            "operating_hours": 300.0,
            "last_service_hours": 0.0,
            "current_mileage": 5000.0,
            "last_service_mileage": 0.0,
            "has_inspection_record": True,
            "detected_defects": [],
        },
        {
            "equipment_id": "TOW-02",
            "equipment_name": "Heavy Tow 02",
            "operating_hours": 50.0,
            "last_service_hours": 0.0,
            "current_mileage": 1000.0,
            "last_service_mileage": 0.0,
            "has_inspection_record": False,
            "detected_defects": [],
        },
    ]
    records = FleetMaintenanceEngine.evaluate_fleet("TENANT-TEST-01", fleet_data)
    assert len(records) == 2
    assert records[0].status == "OVERDUE_SERVICE"
    assert records[1].status == "MISSING_INSPECTION"


def test_value_calculator():
    assumptions = CalculatorAssumptions(monthly_job_volume=100, avg_ticket_value=2000.0)
    res = OperationalValueCalculator.calculate_value("TENANT-TEST-01", assumptions)
    assert res.monthly_revenue_evaluated == 200000.0
    assert res.estimated_revenue_at_risk == 7000.0
    assert "PROJECTION ONLY" in res.projection_disclaimer


def test_integration_adapters():
    csv_data = "ticket_id,po_id,invoice_id,total_amount,has_signature\nFT-01,PO-01,INV-01,1200.0,true"
    imported = IntegrationFoundationAdapters.import_csv_tickets(csv_data)
    assert len(imported) == 1
    assert imported[0]["ticket_id"] == "FT-01"

    exceptions = RevenueLeakageEngine.evaluate_records(
        "TENANT-01",
        [{"ticket_id": "FT-01", "po_id": None, "total_amount": 500.0}],
        [], [], [],
    )
    teams_payload = IntegrationFoundationAdapters.export_teams_notification(exceptions[0])
    assert teams_payload["status"] == "DISABLED_BY_DEFAULT"
    assert teams_payload["external_transmission_allowed"] is False


def test_dispater_api_endpoints(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")

    # Reconciliation endpoint
    resp = client.post(
        "/v1/dispater/reconciliation",
        headers=AUTH_HEADER,
        json={
            "tenant_id": "TENANT-COMMERCIAL-01",
            "field_tickets": [{"ticket_id": "FT-10", "po_id": None, "total_amount": 1000.0}],
            "invoices": [],
            "purchase_orders": [],
            "rate_sheets": [],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_exceptions_count"] >= 1

    # Fleet Maintenance endpoint
    resp = client.get("/v1/dispater/fleet-maintenance", headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert "fleet_records" in resp.json()

    # Value Calculator endpoint
    resp = client.post(
        "/v1/dispater/value-calculator",
        headers=AUTH_HEADER,
        json={"tenant_id": "TENANT-COMMERCIAL-01", "assumptions": {}},
    )
    assert resp.status_code == 200
    assert "total_estimated_monthly_value" in resp.json()

    # Dashboard endpoint
    resp = client.get("/v1/dispater/dashboard", headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert resp.json()["data_classification"] == "SYNTHETIC_STAGING_DEMONSTRATION"
