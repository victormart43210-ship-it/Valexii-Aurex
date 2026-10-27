"""
End-to-End Synthetic Demonstration Test ($500 Equipment Hour Discrepancy Scenario).

Demonstrates complete pipeline:
Document Ingestion -> Field Extraction -> Cross-Document Reconciliation -> RevenueLeakageEngine -> XAELI 5-Step Explanation -> Human Review Queue.
"""

from aurex.dispater_documents import DocumentIntelligenceEngine
from aurex.dispater_intelligence import RevenueLeakageEngine
from aurex.dispater_pilot import CommercialPilotEngine, HumanReviewDecision, PilotTenantConfig


def test_five_hundred_dollar_equipment_hour_discrepancy_e2e_scenario():
    # 1. Ingest Synthetic Equipment Ticket ($250/hr * 12 hrs = $3,000)
    ticket_file = (
        b"ticket_id,po_id,invoice_id,total_amount,has_signature\n"
        b"FT-E2E-101,PO-E2E-100,INV-E2E-101,3000.0,true"
    )

    doc_result = DocumentIntelligenceEngine.process_document(
        tenant_id="TENANT-E2E-OILFIELD",
        document_id="DOC-E2E-101",
        filename="field_ticket.csv",
        file_bytes=ticket_file,
    )

    assert doc_result.extraction_status == "SUCCESS"
    extracted_tickets = doc_result.extracted_records["field_tickets"]
    assert len(extracted_tickets) == 1

    # 2. Ingest Billed Invoice ($250/hr * 10 hrs = $2,500) -> $500 Discrepancy
    invoices = [{
        "invoice_id": "INV-E2E-101",
        "vendor_or_customer": "Apache Oilfield",
        "total_amount": 2500.0,  # Underbilled by $500 vs field ticket $3000
        "po_id": "PO-E2E-100",
        "line_items": [{"rate_code": "RIG-HR", "unit_rate": 250.0, "quantity": 10}],
        "multi_record_mismatch": True,
        "mismatch_amount": 500.0,
    }]
    purchase_orders = [{"po_id": "PO-E2E-100", "amount_limit": 10000.0}]
    rate_sheets = [{"rate_code": "RIG-HR", "approved_rate": 250.0}]

    # 3. Cross-Document Reconciliation
    exceptions = RevenueLeakageEngine.evaluate_records(
        tenant_id="TENANT-E2E-OILFIELD",
        field_tickets=extracted_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
    )

    mismatch_excs = [e for e in exceptions if e.rule_type == "MULTI_RECORD_DISCREPANCY"]
    assert len(mismatch_excs) == 1
    assert mismatch_excs[0].financial_exposure == 500.0

    # 4. XAELI 5-Step Explanation
    xaeli_findings = RevenueLeakageEngine.convert_to_xaeli_findings(mismatch_excs)
    assert len(xaeli_findings) == 1
    f = xaeli_findings[0]
    assert "MULTI_RECORD_DISCREPANCY" in f.now
    assert "SHA-256 Digest" in f.proof
    assert f.exposure_usd == 500.0

    # 5. Human Review Queue & Value Reporting
    pilot_config = PilotTenantConfig(
        tenant_id="TENANT-E2E-OILFIELD",
        company_name="Apache Oilfield",
        industry_sector="Oilfield Operations",
        onboarded_at="2026-10-27T00:00:00Z",
        authorized_human_approver="MANAGER_DAN",
    )
    pilot = CommercialPilotEngine(pilot_config)
    summary = pilot.process_ingestion_batch(
        batch_id="BATCH-E2E-01",
        ingested_at="2026-10-27T01:00:00Z",
        field_tickets=extracted_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
        fleet_data=[],
    )

    assert summary.potential_exposure_usd == 500.0
    assert summary.actual_recovered_revenue_usd == 0.0  # Potential exposure remains distinct from recovered

    # 6. Human Review Approval
    decision = HumanReviewDecision(
        decision_id="DEC-E2E-1",
        tenant_id="TENANT-E2E-OILFIELD",
        exception_id=f.exception_id,
        review_status="APPROVED_CORRECTION",
        reviewer_identity="MANAGER_DAN",
        reviewed_at="2026-10-27T02:00:00Z",
        notes="Underbilled 2 rig hours verified against field log. Reissued invoice for $500.",
        approved_adjustment_usd=500.0,
        actual_recovered_usd=500.0,
    )
    pilot.record_human_decision(decision)

    updated_summary = pilot.process_ingestion_batch(
        batch_id="BATCH-E2E-02",
        ingested_at="2026-10-27T02:30:00Z",
        field_tickets=extracted_tickets,
        invoices=invoices,
        purchase_orders=purchase_orders,
        rate_sheets=rate_sheets,
        fleet_data=[],
    )

    assert updated_summary.actual_recovered_revenue_usd == 500.0
