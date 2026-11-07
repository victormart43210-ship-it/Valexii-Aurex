"""Synthetic DISPATER two-industry end-to-end tests. Never uses customer data."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from aurex.dispater_demo import build_demo_report
from aurex.dispater_pilot import InvalidSnapshot

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def sample(name: str) -> dict:
    return json.loads((EXAMPLES / f"dispater_{name}_synthetic.json").read_text(encoding="utf-8"))


def test_towing_detects_revenue_and_record_gaps_without_authority() -> None:
    report = build_demo_report(sample("towing"))
    assert report["sector"] == "towing"
    assert report["counts"]["revenue_findings"] == 3
    assert report["counts"]["readiness_findings"] == 2
    assert report["counts"]["reviewed"] == 0
    assert report["counts"]["awaiting_review"] == 5
    assert {f["code"] for f in report["findings"]} == {
        "UNBILLED_JOB",
        "RATE_MISMATCH",
        "PAID_STATUS_UNRECONCILED",
        "EVIDENCE_MISSING_OR_EXPIRED",
    }
    assert report["status"] == "HOLD"
    assert report["nvidia_inference"] == "NOT RUN"
    assert report["independent_verification"] == "NOT VERIFIED"
    assert all(f["review"]["status"] == "NOT_REVIEWED" for f in report["findings"])


def test_oilfield_uses_same_engine() -> None:
    report = build_demo_report(sample("oilfield"))
    assert report["counts"]["revenue_findings"] == 1
    assert report["counts"]["readiness_findings"] == 0
    assert report["findings"][0]["code"] == "UNBILLED_JOB"
    assert report["sector"] == "oilfield"


def test_review_updates_evidence_only_not_financial_effects() -> None:
    package = sample("towing")
    finding_id = build_demo_report(package)["findings"][0]["finding_id"]
    package["review"]["decisions"] = [{
        "finding_id": finding_id,
        "decision": "ACKNOWLEDGED",
        "note": "Fictional manager requests reconciliation",
    }]
    result = build_demo_report(package)
    assert result["counts"]["reviewed"] == 1
    assert result["counts"]["awaiting_review"] == 4
    assert result["status"] == "HOLD"
    selected = next(f for f in result["findings"] if f["finding_id"] == finding_id)
    assert selected["review"]["effect_authority"] == "NONE"
    assert selected["explanation_provenance"] == "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN"


def test_stale_or_duplicated_review_keys_fail_closed() -> None:
    package = sample("towing")
    package["review"]["decisions"] = [{
        "finding_id": "unrecognized",
        "decision": "ACKNOWLEDGED",
        "note": "",
    }]
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)

    package = sample("towing")
    finding_id = build_demo_report(package)["findings"][0]["finding_id"]
    row = {"finding_id": finding_id, "decision": "ACKNOWLEDGED", "note": ""}
    package["review"]["decisions"] = [row, deepcopy(row)]
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)


def test_real_data_labels_and_real_reviewer_names_rejected() -> None:
    package = sample("towing")
    package["dataset_type"] = "CUSTOMER_EXPORT"
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)
    package = sample("towing")
    package["review"]["reviewer_id"] = "ACTUAL_MANAGER"
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)
    package = sample("towing")
    package["revenue"]["dataset_type"] = "ACTUAL_DATA"
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)


def test_unrecognized_fields_rejected_without_model_or_network() -> None:
    package = sample("towing")
    package["social_security_number"] = "unsafe"
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)
    package = sample("towing")
    package["review"]["decisions"] = [{
        "finding_id": build_demo_report(package)["findings"][0]["finding_id"],
        "decision": "PAY_INVOICE",
        "note": "",
    }]
    with pytest.raises(InvalidSnapshot):
        build_demo_report(package)


def test_deterministic_and_self_issued_receipt_not_independent() -> None:
    package = sample("towing")
    one, two = build_demo_report(package), build_demo_report(package)
    assert one == two
    assert one["self_issued_receipt_sha256"]
    assert one["independent_verification"] == "NOT VERIFIED"
    assert one["status"] == "HOLD"
    assert "Not an IRS/DOT audit" in one["limits"]


def test_unreviewed_legal_applicability_is_visible() -> None:
    package = sample("towing")
    package["evidence"]["requirements"][0]["reviewed"] = False
    report = build_demo_report(package)
    assert "APPLICABILITY_UNVERIFIED" in {x["code"] for x in report["findings"]}
