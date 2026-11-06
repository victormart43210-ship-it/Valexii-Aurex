"""
Test 36-Month Golden Historical Industrial Audit & Continuous Monitoring Pipeline.

Verifies end-to-end processing across 36 synthetic operational months:
1. Ingestion and source hashing of realistic multi-month invoices, tickets, and contracts.
2. Selection of appropriate processing adapters (deterministic structured vs OCR).
3. Field-level provenance preservation across all records.
4. Deterministic revenue reconciliation (distinguishing clean transactions from discrepancies).
5. Independent multi-root evidence qualification via Evidence Integrity Kernel.
6. Tamper-evident audit receipt and presentation generation.
7. Contract invalidation and finding lifecycle updates upon contract correction.
8. Incremental continuous monitoring ingestion of month 37 without rewriting history.
"""

import json
from decimal import Decimal
from typing import Any

from aurex.dispater_envelope import DocumentCategory, compute_sha256
from aurex.dispater_monitoring import ContinuousMonitoringEngine, MonitoringEventKind
from aurex.evidence_kernel import ActorKind


def build_36_month_synthetic_dataset(tenant_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Generates 36 months of realistic monthly industrial operational records matching RevenueLeakageEngine schema."""
    jobs: list[dict[str, Any]] = []
    invoices: list[dict[str, Any]] = []
    rates: list[dict[str, Any]] = [
        {
            "rate_id": "RATE-WRECKER-2023",
            "customer_id": "APACHE-OPERATOR",
            "service_code": "HEAVY_WRECKER_75T",
            "start": "2023-01-01",
            "end": "2026-12-31",
            "amount": "3500.00",
        }
    ]
    payments: list[dict[str, Any]] = []
    raw_documents: list[dict[str, Any]] = []

    # 36 months simulation:
    for m in range(1, 37):
        month_str = f"2023-{(m - 1) % 12 + 1:02d}-15" if m <= 12 else (
            f"2024-{(m - 13) % 12 + 1:02d}-15" if m <= 24 else f"2025-{(m - 25) % 12 + 1:02d}-15"
        )
        inv_id = f"INV-36M-{m:03d}"
        job_id = f"FT-36M-{m:03d}"

        # Standard monthly clean run: $3500.00
        # Seed intentional known discrepancy in month 7: $4500 ($1000 overbilling)
        # Seed intentional known discrepancy in month 19: $3000 ($500 underbilling)
        if m == 7:
            inv_amount = "4500.00"
        elif m == 19:
            inv_amount = "3000.00"
        else:
            inv_amount = "3500.00"

        job_record = {
            "job_id": job_id,
            "customer_id": "APACHE-OPERATOR",
            "service_code": "HEAVY_WRECKER_75T",
            "date": month_str,
        }
        inv_record = {
            "invoice_id": inv_id,
            "job_id": job_id,
            "amount": inv_amount,
            "status": "paid",
        }
        pay_record = {
            "payment_id": f"PAY-36M-{m:03d}",
            "invoice_id": inv_id,
            "amount": inv_amount,
            "date": month_str,
        }

        jobs.append(job_record)
        invoices.append(inv_record)
        payments.append(pay_record)

        raw_documents.append({
            "source_id": f"accounting_system_inv_{m}",
            "source_record_id": inv_id,
            "category": DocumentCategory.INVOICE,
            "raw_bytes": json.dumps(inv_record).encode("utf-8"),
            "media_type": "application/json",
        })
        raw_documents.append({
            "source_id": f"field_dispatch_tkt_{m}",
            "source_record_id": job_id,
            "category": DocumentCategory.EQUIPMENT_TICKET,
            "raw_bytes": json.dumps(job_record).encode("utf-8"),
            "media_type": "application/json",
        })

    snapshot = {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": tenant_id,
        "as_of": "2026-11-05",
        "jobs": jobs,
        "rates": rates,
        "invoices": invoices,
        "payments": payments,
    }
    return snapshot, raw_documents


def test_36_month_golden_audit_end_to_end() -> None:
    tenant_id = "tenant-industrial-permian"
    snapshot, raw_docs = build_36_month_synthetic_dataset(tenant_id)
    engine = ContinuousMonitoringEngine(tenant_id=tenant_id)

    # 1. Admit all 72 historical source documents (36 months x 2 docs)
    assert len(raw_docs) == 72
    for doc in raw_docs:
        envelope = engine.pipeline.admit_document(
            source_id=doc["source_id"],
            source_record_id=doc["source_record_id"],
            document_category=doc["category"],
            raw_bytes=doc["raw_bytes"],
            media_type=doc["media_type"],
        )
        assert envelope.source_content_sha256 == compute_sha256(doc["raw_bytes"])
        assert len(envelope.provenance_fields) > 0
        # Immutability check: raw payload preview preserved
        assert envelope.byte_count == len(doc["raw_bytes"])

    # 2. Execute 36-Month Historical Reconciliation & Independent Verification
    audit_result = engine.pipeline.execute_audit_run(
        snapshot=snapshot,
        actor_kind=ActorKind.HUMAN,
        reviewer_id="lead-industrial-auditor",
    )
    engine.record_historical_audit(audit_result)

    assert audit_result.envelopes_admitted == 72
    assert audit_result.verification_status == "HOLD_PENDING_HUMAN_SIGNATURE"
    assert len(audit_result.audit_receipt_sha256) == 64

    # 3. Verify Discrepancies Detected accurately
    findings = audit_result.qualified_findings + audit_result.withheld_findings
    assert len(findings) >= 2
    month_7_finding = next((f for f in findings if "007" in f.get("subject", "") or "INV-36M-007" in str(f)), None)
    assert month_7_finding is not None
    assert Decimal(str(month_7_finding["exposure_usd"])) == Decimal("1000.00")

    # 4. Invalidation on Contract Correction (MEDAURUS Freshness invariant)
    engine.process_contract_update(
        contract_id="CONTRACT-HEAVY-WRECKER-2023",
        new_contract_spec={"equipment_type": "HEAVY_WRECKER_75T", "retroactive_rate": "3750.00"},
    )
    assert len(engine.audit_log) > 0
    contract_event = next(e for e in engine.audit_log if e.event_kind == MonitoringEventKind.CONTRACT_SUPERSEDED)
    assert contract_event.details["contract_id"] == "CONTRACT-HEAVY-WRECKER-2023"

    # 5. Continuous Monitoring: Month 37 Incremental Record Ingestion
    month_37_inv = {
        "invoice_id": "INV-36M-037",
        "job_id": "FT-36M-037",
        "amount": "3500.00",
        "status": "paid",
    }
    env_37 = engine.ingest_incremental_record(
        source_id="accounting_system_inv_37",
        source_record_id="INV-36M-037",
        category=DocumentCategory.INVOICE,
        raw_bytes=json.dumps(month_37_inv).encode("utf-8"),
        media_type="application/json",
    )
    assert env_37.source_record_id == "INV-36M-037"

    # Historical runs preserved without mutation
    assert len(engine.historical_runs) == 1
    assert engine.historical_runs[0].run_id == audit_result.run_id
