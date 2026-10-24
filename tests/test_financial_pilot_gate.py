"""Synthetic-only tests: no bank data, names, invoices or external calls."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aurex.commercial.pilot_gate import evaluate_financial_pilots


def model_pilot(i: int) -> dict:
    return {
        "customer_pseudonym": f"pilot-test{i}",
        "paid_pilot": True,
        "consent_attested": True,
        "contract_attested": True,
        "independent_review_attested": True,
        "costs_attested": True,
        "source_integrity_attested": True,
        "measurement_days": 35,
        "documents_reviewed": 400,
        "documents_text_available": 390,
        "critical_fields_labeled": 2000,
        "critical_fields_correct": 1990,
        "reconciliation_tp": 350,
        "reconciliation_fp": 1,
        "reconciliation_fn": 3,
        "reconciliation_tn": 200,
        "critical_discrepancy_misses": 0,
        "baseline_review_minutes": 10000,
        "assisted_review_minutes": 5000,
        "collected_revenue_cents": 100_000,
        "fully_loaded_cost_cents": 20_000,
        "privacy_incidents": 0,
    }


def payload() -> dict:
    return {"schema_version": 1, "pilots": [model_pilot(i) for i in range(3)]}


def test_valid_synthetic_claims_never_become_admitted() -> None:
    r = evaluate_financial_pilots(payload())
    assert r["candidate_thresholds_met"] is True
    assert r["status"] == "HOLD_EXTERNAL_AUDIT_REQUIRED"
    assert r["authority"] == "NONE"
    assert r["production_admission"] == "NOT VERIFIED"
    assert r["independent_evidence_verified_by_this_tool"] is False
    assert r["pilot_count"] == 3
    assert "pilot-test0" not in str(r)


def test_empty_input_does_not_pass() -> None:
    assert evaluate_financial_pilots({})["status"] == "HOLD"
    assert not evaluate_financial_pilots({"schema_version": 1, "pilots": []})[
        "candidate_thresholds_met"
    ]


def test_two_customers_hold() -> None:
    p = payload()
    p["pilots"].pop()
    assert "THREE_INDEPENDENT_PAID_PILOTS_REQUIRED" in evaluate_financial_pilots(p)["blocking_gates"]


def test_duplicate_customer_holds() -> None:
    p = payload()
    p["pilots"][1]["customer_pseudonym"] = p["pilots"][0]["customer_pseudonym"]
    assert "DUPLICATE_CUSTOMER_PILOT" in evaluate_financial_pilots(p)["blocking_gates"]


@pytest.mark.parametrize("field", [
    "paid_pilot", "consent_attested", "contract_attested",
    "independent_review_attested", "costs_attested", "source_integrity_attested"
])
def test_missing_paid_or_audit_attestation_holds(field: str) -> None:
    p = payload()
    p["pilots"][0][field] = False
    r = evaluate_financial_pilots(p)
    assert not r["candidate_thresholds_met"]


@pytest.mark.parametrize("field,value,gate", [
    ("measurement_days", 5, "THIRTY_DAY_CUSTOMER_EVIDENCE_REQUIRED"),
    ("documents_text_available", 50, "TEXT_COVERAGE_BELOW_95_PERCENT"),
    ("critical_fields_correct", 100, "CRITICAL_FIELD_ACCURACY_BELOW_99_PERCENT"),
    ("reconciliation_fp", 300, "RECONCILIATION_PRECISION_BELOW_99_PERCENT"),
    ("reconciliation_fn", 300, "RECONCILIATION_RECALL_BELOW_95_PERCENT"),
    ("assisted_review_minutes", 9500, "HUMAN_TIME_SAVING_BELOW_40_PERCENT"),
    ("fully_loaded_cost_cents", 80_000, "GROSS_MARGIN_BELOW_70_PERCENT"),
    ("privacy_incidents", 1, "PRIVACY_INCIDENT_PRESENT"),
    ("critical_discrepancy_misses", 1, "CRITICAL_DISCREPANCY_MISS_PRESENT"),
])
def test_metric_miss_holds(field: str, value: int, gate: str) -> None:
    p = payload()
    p["pilots"][0][field] = value
    r = evaluate_financial_pilots(p)
    assert gate in r["blocking_gates"]
    assert not r["candidate_thresholds_met"]


@pytest.mark.parametrize("field,value", [
    ("documents_reviewed", -1),
    ("reconciliation_tp", True),
    ("reconciliation_tp", "350"),
    ("critical_fields_labeled", 0.5),
    ("documents_text_available", 401),
    ("critical_fields_correct", 2001),
])
def test_bad_measurement_types_or_inconsistent_counts_fail_closed(field: str, value: object) -> None:
    p = payload()
    p["pilots"][0][field] = value
    r = evaluate_financial_pilots(p)
    assert not r["candidate_thresholds_met"]


def test_no_rounded_fraction_promotes_gate() -> None:
    p = payload()
    for pilot in p["pilots"]:
        pilot["reconciliation_tp"] = 98
        pilot["reconciliation_fp"] = 2
    r = evaluate_financial_pilots(p)
    assert "RECONCILIATION_PRECISION_BELOW_99_PERCENT" in r["blocking_gates"]


def test_unexpected_key_and_pii_rejected() -> None:
    p = payload()
    p["pilots"][0]["customer_name"] = "Synthetic Corp"
    r = evaluate_financial_pilots(p)
    assert r["blocking_gates"] == ["INVALID_PILOT_SCHEMA"]
    assert "Synthetic Corp" not in str(r)


def test_json_numeric_bool_invalid_and_string_not_accepted() -> None:
    p = payload()
    p["pilots"][0]["paid_pilot"] = "True"
    assert evaluate_financial_pilots(p)["blocking_gates"] == ["INVALID_ATTESTATION_TYPE"]


def test_schema_version_cannot_be_boolean() -> None:
    p = payload()
    p["schema_version"] = True
    assert evaluate_financial_pilots(p)["blocking_gates"] == ["INVALID_SCHEMA_VERSION"]


def test_source_payload_not_mutated() -> None:
    p = payload()
    before = deepcopy(p)
    evaluate_financial_pilots(p)
    assert p == before
