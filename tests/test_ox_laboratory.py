"""Offline laboratory checks. Expected money is local arithmetic, not an engine callback."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import ModuleType

from aurex.ascendancy.historical_audit import (
    admitted_byte_length,
    historical_validation_proposal,
    run_authorized_audit,
)
from aurex.dispater_intelligence import RevenueLeakageEngine, digest
from aurex.ox.customization import customization_contract, promotion_decision
from aurex.ox.evaluation import evaluate, injected_provider, mock_provider
from aurex.ox.registry import EMPTY_SHA256, RegistryError, validate_registry
from aurex.ox.replay import audit_replay_manifest

NOW = datetime.now(UTC)


def _golden_fixture() -> ModuleType:
    """Load the golden fixture by path. ``import tests`` is not available to ``pytest -q``."""
    path = Path(__file__).resolve().parent / "test_dispater_golden_audit.py"
    spec = importlib.util.spec_from_file_location("ccxlvii_golden_fixture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("golden fixture is missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_rejects_self_approval_and_the_empty_digest() -> None:
    data = validate_registry()
    assert data["paid_inference"] == "OFF"
    assert all(item["live_connection"] == "NOT_VERIFIED" for item in data["models"])
    assert all(item["executable_model"] is False for item in data["research_frameworks"])
    broken = {
        "financial_authority": "NONE",
        "paid_inference": "OFF",
        "models": [{**data["models"][0], "weight_digest": EMPTY_SHA256}],
        "research_frameworks": data["research_frameworks"],
    }
    broken["training"] = "NOT_STARTED"
    try:
        validate_registry(broken)
    except RegistryError as exc:
        assert "digest" in str(exc)
    else:
        raise AssertionError("empty digest")
    promoted = {
        **data,
        "models": [{**data["models"][0], "approval_state": "HUMAN_APPROVED"}],
    }
    try:
        validate_registry(promoted)
    except RegistryError as exc:
        assert "approve" in str(exc)
    else:
        raise AssertionError("denylist approval")
    framework = {
        **data,
        "research_frameworks": [{**data["research_frameworks"][0], "approval_state": "HUMAN_APPROVED"}],
    }
    try:
        validate_registry(framework)
    except RegistryError as exc:
        assert "framework" in str(exc)
    else:
        raise AssertionError("framework approval")


def test_offline_runner_matches_the_answer_key_and_blocks_injection() -> None:
    clean = evaluate("qwen", tenant_id="tenant-lab")
    again = evaluate("qwen", tenant_id="tenant-lab", provider=mock_provider)
    assert clean["passed"] is True
    assert clean["live_connection"] == "NOT_VERIFIED"
    assert clean["report_digest"] == again["report_digest"]
    assert all(item["confirmed_recovery_usd"] == "0.00" for item in clean["cases"])
    def side_channel(case_id: str) -> dict[str, object]:
        output = dict(mock_provider(case_id))
        output["recovered_usd"] = "50.00"
        return output

    diverted = evaluate("qwen", tenant_id="tenant-lab", provider=side_channel)
    assert diverted["passed"] is False

    def nested(case_id: str) -> dict[str, object]:
        output = dict(mock_provider(case_id))
        output["detail"] = {"recovered_usd": "50.00"}
        return output

    assert evaluate("qwen", tenant_id="tenant-lab", provider=nested)["passed"] is False
    poisoned = evaluate("qwen", tenant_id="tenant-lab", provider=injected_provider)
    assert poisoned["passed"] is False
    withheld = next(item for item in poisoned["cases"] if item["case_id"] == "withhold-recovery")
    assert withheld["unsupported_claim"] is True
    assert withheld["circular_evidence"] is True
    try:
        evaluate("qwen", tenant_id="tenant-lab", paid_inference=True)
    except RegistryError as exc:
        assert "paid" in str(exc)
    else:
        raise AssertionError("paid inference")
    try:
        evaluate("qwen", tenant_id="other-tenant")
    except RegistryError as exc:
        assert "tenant" in str(exc)
    else:
        raise AssertionError("cross tenant")


def test_customization_does_not_train_or_let_a_model_promote_itself() -> None:
    contract = customization_contract("lora", tenant_id="tenant-lab", base_entry_id="qwen")
    assert contract["training_started"] is False
    assert contract["weights_downloaded"] is False
    model_vote = promotion_decision(actor="MODEL", evaluation_verified_by_other_party=True, method="prompt")
    assert model_vote["eligible_for_synthetic_config"] is False
    human = promotion_decision(actor="HUMAN", evaluation_verified_by_other_party=True, method="fine_tune")
    assert human["training_started"] is False
    assert human["eligible_for_synthetic_config"] is False


def test_replay_manifest_ignores_the_clock_and_sees_a_changed_cent() -> None:
    first = audit_replay_manifest(
        tenant_pseudonym="tenant-lab",
        audit_run_id="run-1",
        source_digests=["b" * 64, "a" * 64],
        rule_pack_digest="c" * 64,
        code_commit="9148634",
        output_digest="d" * 64,
        created_at="2026-11-06T14:00:00Z",
    )
    later = audit_replay_manifest(
        tenant_pseudonym="tenant-lab",
        audit_run_id="run-1",
        source_digests=["a" * 64, "b" * 64],
        rule_pack_digest="c" * 64,
        code_commit="9148634",
        output_digest="d" * 64,
        created_at="2026-11-06T18:00:00Z",
    )
    changed = audit_replay_manifest(
        tenant_pseudonym="tenant-lab",
        audit_run_id="run-1",
        source_digests=["a" * 64, "b" * 64],
        rule_pack_digest="c" * 64,
        code_commit="9148634",
        output_digest="e" * 64,
        created_at="2026-11-06T14:00:00Z",
    )
    assert first["manifest_digest"] == later["manifest_digest"]
    assert first["manifest_digest"] != changed["manifest_digest"]


def test_financial_headlines_and_the_historical_gate_stay_closed() -> None:
    # Seed arithmetic, restated here. It is not taken from the engine's summary.
    under = Decimal("100.00")
    over = Decimal("50.00") + Decimal("80.00")
    unverified = Decimal("40.00") + Decimal("60.00") + Decimal("30.00") + Decimal("25.00")
    withheld = Decimal("80.00") + Decimal("70.00")
    identified_total = under + over + unverified
    assert identified_total == Decimal("385.00")
    assert withheld == Decimal("150.00")
    golden = _golden_fixture()
    report = RevenueLeakageEngine("golden").reconcile_records(golden.build_dataset())
    summary = report["financial_summary"]
    assert summary["identified_exposure_usd"] == f"{identified_total:.2f}"
    assert summary["withheld_unresolved_usd"] == f"{withheld:.2f}"
    assert summary["confirmed_recovery_usd"] == "0.00"
    assert summary["confirmed_recovery_usd"] != summary["identified_exposure_usd"]
    assert report["authority_state"] == "HOLD"
    assert all(item["qualification"] != "CONFIRMED_DISCREPANCY" for item in report["findings"])
    identified = Decimal("110.00") - Decimal("100.00")
    dataset = {
        "tenant_id": "tenant-asc",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
        "rates": [
            {
                "rate_id": "R1",
                "customer_id": "C1",
                "service_code": "S",
                "start": "2026-01-01",
                "end": "2026-12-31",
                "amount": "100.00",
            }
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "110.00", "status": "open"}],
        "payments": [],
    }
    dossier = run_authorized_audit(
        {
            "authorization_id": "auth-lab",
            "tenant_id": "tenant-asc",
            "purpose": "SYNTHETIC_VALIDATION",
            "privacy_control": "SYNTHETIC_ONLY",
            "expires_at": NOW + timedelta(days=1),
            "grantor_kind": "HUMAN",
            "reviewer_id": "reviewer-lab",
        },
        NOW,
        dataset,
        source_sha256=digest(dataset),
        byte_length=admitted_byte_length(dataset),
    )
    assert dossier["financial_summary"]["identified_exposure_usd"] == f"{identified:.2f}"
    assert dossier["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    proposal = historical_validation_proposal()
    assert proposal["activated"] is False
    assert proposal["status"] == "PROPOSED"
