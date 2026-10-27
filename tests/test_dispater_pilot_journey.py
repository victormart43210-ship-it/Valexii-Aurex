"""
Synthetic 8-Stage Customer Journey & Commercial Pilot Workflow Tests.
"""

import pytest

from aurex.dispater_pilot import (
    CommercialPilotEngine,
    HumanReviewDecision,
    PilotTenantConfig,
    sanitize_csv_formula_injection,
)


def test_complete_8_stage_simulated_customer_journey():
    # Stage 1: Onboarding
    config = PilotTenantConfig(
        tenant_id="TENANT-PILOT-900",
        company_name="Vanguard Oilfield Services",
        industry_sector="Oilfield Operations",
        onboarded_at="2026-10-27T00:00:00Z",
        authorized_human_approver="VP_OPERATIONS",
    )
    engine = CommercialPilotEngine(config)

    # Stage 2: Read-Only Data Ingestion
    field_tickets = [
        {"ticket_id": "FT-P901", "po_id": "PO-900", "invoice_id": None, "total_amount": 12500.0, "has_customer_signature": True},
        {"ticket_id": "FT-P902", "po_id": None, "invoice_id": "INV-902", "total_amount": 4500.0, "has_customer_signature": True},
    ]
    invoices = [
        {"invoice_id": "INV-902", "vendor_or_customer": "Apache Energy", "total_amount": 4500.0},
    ]
    purchase_orders = [
        {"po_id": "PO-900", "amount_limit": 20000.0},
    ]
    rate_sheets = []
    fleet_data = [
        {"equipment_id": "RIG-90", "equipment_name": "Heavy Rig 90", "operating_hours": 320.0, "last_service_hours": 0.0},
    ]

    # Stage 3 & 4: Reconciliation & Discrepancy Detection
    summary = engine.process_ingestion_batch(
        batch_id="BATCH-P900",
        ingested_at="2026-10-27T01:00:00Z",
        field_tickets=field_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
        fleet_data=fleet_data,
    )

    assert summary.evaluated_revenue_usd == 17000.0
    assert summary.potential_exposure_usd == 17000.0  # $12.5k unbilled + $4.5k missing PO
    assert summary.exceptions_count >= 2
    assert summary.pending_human_reviews_count == summary.exceptions_count

    # Stage 5 & 6: Review & Disposition (Human Manager Approval)
    decision = HumanReviewDecision(
        decision_id="DEC-01",
        tenant_id="TENANT-PILOT-900",
        exception_id=summary.xaeli_findings[0].exception_id,
        review_status="APPROVED_CORRECTION",
        reviewer_identity="VP_OPERATIONS",
        reviewed_at="2026-10-27T02:00:00Z",
        notes="Unbilled ticket verified against signed field log. Supplemental invoice issued.",
        approved_adjustment_usd=12500.0,
        actual_recovered_usd=12500.0,
    )
    engine.record_human_decision(decision)

    # Stage 7 & 8: Value Reporting & Evidence Digest
    updated_summary = engine.process_ingestion_batch(
        batch_id="BATCH-P900-V2",
        ingested_at="2026-10-27T02:30:00Z",
        field_tickets=field_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
        fleet_data=fleet_data,
    )

    assert updated_summary.customer_approved_corrections_usd == 12500.0
    assert updated_summary.actual_recovered_revenue_usd == 12500.0
    assert updated_summary.potential_exposure_usd == 17000.0  # Potential exposure remains distinct from recovered


def test_tenant_isolation_error():
    config = PilotTenantConfig(
        tenant_id="TENANT-A",
        company_name="Company A",
        industry_sector="Towing",
        onboarded_at="2026-10-27T00:00:00Z",
        authorized_human_approver="ADMIN_A",
    )
    engine = CommercialPilotEngine(config)

    decision_b = HumanReviewDecision(
        decision_id="DEC-B",
        tenant_id="TENANT-B",  # Cross-tenant decision
        exception_id="EXC-10",
        review_status="APPROVED_CORRECTION",
        reviewer_identity="ADMIN_A",
        reviewed_at="2026-10-27T00:00:00Z",
        notes="Invalid cross tenant decision",
    )

    with pytest.raises(ValueError, match="Tenant isolation error"):
        engine.record_human_decision(decision_b)


def test_formula_injection_sanitization():
    assert sanitize_csv_formula_injection("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert sanitize_csv_formula_injection("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_formula_injection("Normal Vendor Name") == "Normal Vendor Name"
