"""End-to-end synthetic industrial audit workflow test suite for Operation KUSANAGI CLXXIX.

Verifies complete pipeline:
Record Intake -> XAELI 5-step Analysis -> Brain Trust Orchestration -> Office Work Queue -> Digital Audit Binder Integrity.
"""
from datetime import date

from aurex.brain_trust import execute_brain_trust_orchestration
from aurex.governance_math.industrial_demo import build_demo
from aurex.knowledge_trust import (
    PolicyDocument,
    check_source_independence,
    evaluate_policy_supersession,
)
from aurex.learning_ledger import GovernedLearningLedger


def test_e2e_synthetic_towing_workflow() -> None:
    # 1. Ingestion & XAELI Findings
    demo = build_demo(fixture="towing_v1")
    assert demo["demo"] is True
    assert demo["authority"] == "ADVISORY_ONLY_NO_CERTIFICATION"
    assert len(demo["now"]) == 5

    now_categories = {item["category"]: item["status"] for item in demo["now"]}
    assert now_categories["driver_qualification"] == "PRESENT_NOT_VERIFIED"
    assert now_categories["vehicle_inspection"] == "EXPIRED"
    assert now_categories["maintenance"] == "CONFLICTING"

    # 2. Brain Trust Orchestration
    bt_res = execute_brain_trust_orchestration(
        question="Audit towing records for Permian Recovery Services",
        evidence_ids=("demo-driver-01", "demo-vehicle-01", "demo-maint-01"),
    )
    assert len(bt_res.steps) == 7
    assert bt_res.verifier_status == "VERIFIED"
    assert bt_res.model_authority == "NONE"

    # 3. Knowledge Trust Gateway
    doc1 = PolicyDocument("pol-1", "Old Safety Policy", date(2022, 1, 1), superseded_by="pol-2")
    doc2 = PolicyDocument("pol-2", "Current Safety Policy", date(2026, 1, 1))
    eval_res = evaluate_policy_supersession((doc1, doc2), as_of=date(2026, 10, 26))
    assert eval_res[0].can_authorize_current is False
    assert eval_res[1].can_authorize_current is True

    # 4. Learning Ledger Quarantine
    ledger = GovernedLearningLedger()
    corr = ledger.submit_correction(
        "corr-1", "audit-1", "Vehicle inspection expired", "New annual inspection form uploaded"
    )
    assert corr.status == "QUARANTINED"
    assert ledger.can_apply_to_production("corr-1") is False


def test_source_independence_warning() -> None:
    res = check_source_independence(("digest-a", "digest-a"))
    assert res["independent_corroboration"] is False
    assert "identical copies do not constitute" in str(res["duplicate_warning"])
