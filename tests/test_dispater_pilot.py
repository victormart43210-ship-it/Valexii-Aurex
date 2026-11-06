"""Offline no-network tests for the non-operational DISPATER prototype."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aurex.dispater_evidence import assess_synthetic_readiness
from aurex.dispater_pilot import InvalidSnapshot, audit_synthetic, verify_self_issued_report
from aurex.dispater_workflow import propose_synthetic_workflow, retrieve_synthetic_knowledge


def revenue_fixture() -> dict:
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "TOW", "date": "2026-10-01"}],
        "rates": [{
            "rate_id": "R1", "customer_id": "C1", "service_code": "TOW",
            "start": "2026-01-01", "end": "2026-12-31", "amount": "150.00",
        }],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "paid"}],
        "payments": [{"payment_id": "P1", "invoice_id": "I1", "amount": "150.00"}],
    }


def test_revenue_reconciles_but_never_grants_authority() -> None:
    snap = revenue_fixture()
    report = audit_synthetic(snap)
    assert report["findings"] == []
    assert report["status"] == "HOLD"
    assert report["independent_verification"] == "NOT VERIFIED"
    assert verify_self_issued_report(snap, report)


def test_underbilled_job_is_flagged_without_auto_recovery() -> None:
    snap = revenue_fixture()
    snap["invoices"][0]["amount"] = "100.00"
    snap["payments"][0]["amount"] = "100.00"
    report = audit_synthetic(snap)
    assert [(f["code"], f.get("difference_usd")) for f in report["findings"]] == [
        ("RATE_MISMATCH", "-50.00")
    ]
    assert report["status"] == "HOLD"


def test_unbilled_job_and_missing_rate_are_separate_uncertainties() -> None:
    snap = revenue_fixture()
    snap["invoices"].clear()
    snap["payments"].clear()
    snap["rates"].clear()
    codes = {f["code"] for f in audit_synthetic(snap)["findings"]}
    assert codes == {"UNBILLED_JOB", "RATE_UNVERIFIED"}


def test_duplicate_invoices_never_count_as_recovered_revenue() -> None:
    snap = revenue_fixture()
    snap["invoices"].append({
        "invoice_id": "I2", "job_id": "J1", "amount": "150.00", "status": "open",
    })
    codes = {f["code"] for f in audit_synthetic(snap)["findings"]}
    assert "MULTIPLE_INVOICES" in codes
    assert "RATE_MISMATCH" not in codes


def test_paid_status_unreconciled() -> None:
    snap = revenue_fixture()
    snap["payments"][0]["amount"] = "70.00"
    report = audit_synthetic(snap)
    match = next(f for f in report["findings"] if f["code"] == "PAID_STATUS_UNRECONCILED")
    assert match["difference_usd"] == "-80.00"


def test_orphan_invoice_and_payment() -> None:
    snap = revenue_fixture()
    snap["invoices"][0]["job_id"] = "MISSING_JOB"
    snap["payments"].append({
        "payment_id": "P2", "invoice_id": "MISSING_INVOICE", "amount": "10.00",
    })
    codes = {f["code"] for f in audit_synthetic(snap)["findings"]}
    assert {"ORPHAN_INVOICE", "ORPHAN_PAYMENT"}.issubset(codes)


def test_no_nonsynthetic_or_malformed_financial_data() -> None:
    snap = revenue_fixture()
    snap["dataset_type"] = "CUSTOMER_EXPORT"
    with pytest.raises(InvalidSnapshot):
        audit_synthetic(snap)
    snap["dataset_type"] = "SYNTHETIC_ONLY"
    snap["invoices"][0]["amount"] = "-1.00"
    with pytest.raises(InvalidSnapshot):
        audit_synthetic(snap)


def test_duplicate_ids_rejected() -> None:
    snap = revenue_fixture()
    snap["jobs"].append(deepcopy(snap["jobs"][0]))
    with pytest.raises(InvalidSnapshot, match="duplicate"):
        audit_synthetic(snap)


def test_receipt_is_consistency_only_and_detects_tampering() -> None:
    snap = revenue_fixture()
    report = audit_synthetic(snap)
    report["status"] = "PASS"
    assert not verify_self_issued_report(snap, report)


def workflow_fixture() -> dict:
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "workflow_id": "W1",
        "source": "crm",
        "target": "documents",
        "action": "propose_draft",
        "object_type": "field_ticket",
        "field_names": ["job_id", "customer_id"],
        "human_approval": True,
    }


def test_workflow_never_executes_and_has_explicit_gates() -> None:
    plan = propose_synthetic_workflow(workflow_fixture())
    assert plan["state"] == "HOLD"
    assert plan["execution"] == "DRY_RUN_ONLY"
    assert plan["model_authority"] == "NONE"
    assert "NO_EXTERNAL_CONNECTOR_CONFIGURED" in plan["blockers"]
    assert set(plan["orchestrator_options"]) >= {"Make", "Zapier"}


def test_sensitive_payroll_write_stays_prohibited_even_with_approval() -> None:
    spec = workflow_fixture()
    spec["target"] = "payroll"
    plan = propose_synthetic_workflow(spec)
    assert "PAYROLL_OR_BILLING_WRITE_PROHIBITED" in plan["blockers"]
    assert plan["state"] == "HOLD"


def test_workflow_rejects_secrets_and_missing_approval() -> None:
    spec = workflow_fixture()
    spec["field_names"].append("api_secret")
    with pytest.raises(InvalidSnapshot):
        propose_synthetic_workflow(spec)
    spec = workflow_fixture()
    spec["human_approval"] = False
    assert "HUMAN_APPROVAL_UNSPECIFIED" in propose_synthetic_workflow(spec)["blockers"]


def knowledge_fixture() -> list[dict]:
    return [
        {
            "dataset_type": "SYNTHETIC_ONLY",
            "tenant": "Company-A",
            "document_id": "A-1",
            "title": "Dispatch Manual",
            "excerpt": "Send dispatch ticket to dispatcher for review.",
            "allow_roles": ["dispatcher", "owner"],
        },
        {
            "dataset_type": "SYNTHETIC_ONLY",
            "tenant": "Company-B",
            "document_id": "B-1",
            "title": "Dispatch Manual",
            "excerpt": "Other company dispatch procedures.",
            "allow_roles": ["owner"],
        },
    ]


def test_knowledge_candidates_scoped_by_tenant_and_role() -> None:
    documents = knowledge_fixture()
    out = retrieve_synthetic_knowledge(documents, caller_tenant="Company-A", role="dispatcher", query="dispatch")
    assert [c["document_id"] for c in out["candidates"]] == ["A-1"]
    assert out["generated_answer"] is None
    assert out["model_training_performed"] is False
    assert out["state"] == "HOLD"
    assert retrieve_synthetic_knowledge(
        documents, caller_tenant="Company-A", role="viewer", query="dispatch"
    )["candidates"] == []


def test_private_or_duplicate_knowledge_documents_rejected() -> None:
    documents = knowledge_fixture()
    documents[0]["dataset_type"] = "PRODUCTION"
    with pytest.raises(InvalidSnapshot):
        retrieve_synthetic_knowledge(documents, caller_tenant="Company-A", role="owner", query="dispatch")
    documents = knowledge_fixture()
    documents.append(deepcopy(documents[0]))
    with pytest.raises(InvalidSnapshot):
        retrieve_synthetic_knowledge(documents, caller_tenant="Company-A", role="owner", query="dispatch")


def readiness_fixture() -> dict:
    return {
        "dataset_type": "SYNTHETIC_ONLY",
        "as_of": "2026-10-23",
        "requirements": [
            {
                "rule_id": "DEMO-DOT-01", "domain": "DOT", "subject_id": "TRUCK-1",
                "record_class": "DEMO_DRIVER_FILE", "reviewed": True, "applies": True,
            }
        ],
        "documents": [
            {
                "document_id": "D1", "rule_id": "DEMO-DOT-01",
                "expires_on": "2026-12-31", "copy_available": True,
            }
        ],
    }


def test_readiness_is_only_metadata_assessment() -> None:
    report = assess_synthetic_readiness(readiness_fixture())
    assert report["findings"] == []
    assert report["indexed_demo_requirements"] == 1
    assert report["status"] == "HOLD"


def test_missing_document_and_unreviewed_requirement_are_distinct() -> None:
    snap = readiness_fixture()
    snap["documents"].clear()
    assert assess_synthetic_readiness(snap)["findings"][0]["code"] == "EVIDENCE_MISSING_OR_EXPIRED"
    snap["requirements"][0]["reviewed"] = False
    assert assess_synthetic_readiness(snap)["findings"][0]["code"] == "APPLICABILITY_UNVERIFIED"


def test_expiry_and_real_data_rejection() -> None:
    snap = readiness_fixture()
    snap["documents"][0]["expires_on"] = "2026-01-01"
    assert assess_synthetic_readiness(snap)["findings"][0]["code"] == "EVIDENCE_MISSING_OR_EXPIRED"
    snap["dataset_type"] = "ACTUAL_PAYROLL"
    with pytest.raises(InvalidSnapshot):
        assess_synthetic_readiness(snap)
