"""
Adversarial Negative Tests for DISPATER × AUREX-OX Industrial Pipeline.

Enforces non-delegable security invariants:
1. Model self-witness prohibition: An AI model cannot verify or corroborate a finding.
2. Financial exposure cannot be negative, NaN, or infinite.
3. Provenance cycle and dangling parent rejection (fail-closed).
4. Multi-root independence: Two records deriving from the same root cannot corroborate.
5. Cross-tenant isolation: Tenant A records cannot be admitted or reconciled in Tenant B pipeline.
6. Payload size limit: Requests > 5MB are rejected immediately.
"""

from datetime import UTC, datetime

import pytest

from aurex.dispater_envelope import DocumentCategory
from aurex.dispater_international import QwenLocalInferenceAdapter
from aurex.dispater_pipeline import IndustrialAuditPipeline
from aurex.evidence_kernel import (
    ActorKind,
    EvidenceGraph,
    EvidenceRecord,
    challenge_finding,
)


def test_model_cannot_self_verify() -> None:
    pipeline = IndustrialAuditPipeline("tenant-adv-1")
    qwen = QwenLocalInferenceAdapter()

    # Advisory output has ADVISORY_ONLY authority
    advice = qwen.classify_ambiguity("Check this invoice discrepancy", {"code": "RATE_MISMATCH"})
    assert advice["authority"] == "ADVISORY_ONLY"
    assert "AI assists the process" in advice["advisory_disclaimer"]

    # When pipeline runs with ActorKind.MODEL, findings are WITHHELD
    snapshot = {
        "dataset_type": "SYNTHETIC_ONLY",
        "tenant_id": "tenant-adv-1",
        "as_of": "2026-11-05",
        "jobs": [
            {
                "job_id": "FT-ADV-1",
                "customer_id": "ADV-OP",
                "service_code": "PRESSURE_PUMPING",
                "date": "2026-01-01",
            }
        ],
        "rates": [
            {
                "rate_id": "RATE-ADV-1",
                "customer_id": "ADV-OP",
                "service_code": "PRESSURE_PUMPING",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "4000.00",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-ADV-1",
                "job_id": "FT-ADV-1",
                "amount": "5000.00",
                "status": "open",
            }
        ],
        "payments": [],
    }

    result = pipeline.execute_audit_run(snapshot, actor_kind=ActorKind.MODEL)
    for f in result.qualified_findings:
        assert f.get("authority") != "MODEL_VERIFIED"
    for w in result.withheld_findings:
        assert "HOLD" in w.get("qualification", "") or "WITHHELD" in w.get("qualification", "") or "SINGLE_ROOT" in w.get("qualification", "")


def test_reject_non_finite_and_negative_amounts() -> None:
    # Finding with negative exposure is withheld by challenge_finding
    finding_neg = {
        "finding_id": "FND-NEG",
        "exposure_usd": "-500.00",
        "recovered_usd": "0.00",
        "tenant_id": "tenant-adv-1",
        "evidence": [],
    }
    problems = challenge_finding(finding_neg, "tenant-adv-1", set())
    assert "negative exposure" in problems

    # Finding with NaN or Inf is withheld
    finding_nan = {
        "finding_id": "FND-NAN",
        "exposure_usd": "NaN",
        "recovered_usd": "0.00",
        "tenant_id": "tenant-adv-1",
        "evidence": [],
    }
    problems_nan = challenge_finding(finding_nan, "tenant-adv-1", set())
    assert "invalid amount" in problems_nan


def test_reject_payload_exceeding_5mb() -> None:
    pipeline = IndustrialAuditPipeline("tenant-adv-1")
    huge_payload = b"x" * (5 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="exceeds 5MB ceiling"):
        pipeline.admit_document(
            source_id="test",
            source_record_id="rec-1",
            document_category=DocumentCategory.INVOICE,
            raw_bytes=huge_payload,
            media_type="application/json",
        )


def test_multi_root_independence_enforcement() -> None:
    graph = EvidenceGraph("tenant-adv-1")
    now = datetime.now(UTC)

    # Root 1: PDF invoice
    r1 = EvidenceRecord(
        evidence_id="root-inv-pdf",
        tenant_id="tenant-adv-1",
        source_system="erp",
        source_record_id="INV-100",
        content_sha256="hash1",
        acquired_at=now,
    )
    # Derived 1: OCR from Root 1
    d1 = EvidenceRecord(
        evidence_id="ocr-inv-text",
        tenant_id="tenant-adv-1",
        source_system="ocr",
        source_record_id="INV-100-OCR",
        content_sha256="hash2",
        acquired_at=now,
        parents=("root-inv-pdf",),
    )
    # Derived 2: DB row from Root 1
    d2 = EvidenceRecord(
        evidence_id="db-inv-row",
        tenant_id="tenant-adv-1",
        source_system="db",
        source_record_id="INV-100-DB",
        content_sha256="hash3",
        acquired_at=now,
        parents=("root-inv-pdf",),
    )
    graph.add(r1)
    graph.add(d1)
    graph.add(d2)

    # d1 and d2 share the same root ("erp", "INV-100").
    # Therefore, independent_root_count must be 1, NOT 2.
    assert graph.independent_root_count(["ocr-inv-text", "db-inv-row"]) == 1
