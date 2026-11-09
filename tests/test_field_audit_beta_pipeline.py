"""Synthetic business-rule integration: candidate is separate from scorer oracle."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from pathlib import Path

import pytest

from aurex.field_reconciliation import invoice_ticket_difference, reconcile_field_cases
from workstation.field_audit_beta_gate import score_candidate, suite
from workstation.field_audit_beta_pipeline import candidate_from_suite, read_suite


def test_candidate_100_synthetic_cases_matches_independent_fixture_oracle() -> None:
    output = candidate_from_suite(suite())
    report, passed = score_candidate(output)
    assert passed and report["exact_case_matches"] == 100
    assert report["true_positive_flags"] == 70
    assert report["false_negative_flags"] == 0
    assert report["false_positive_flags"] == 0
    assert report["production_readiness"] == "HOLD"
    assert report["independent_verification"] == "NOT_VERIFIED"


def test_real_or_non_synthetic_input_refused() -> None:
    s = suite()
    s["cases"][0]["synthetic"] = False
    with pytest.raises(ValueError):
        candidate_from_suite(s)


def test_tampered_case_payload_refused() -> None:
    s = suite()
    s["cases"][0]["invoice_cents"] += 1
    with pytest.raises(ValueError, match="digest"):
        candidate_from_suite(s)


def test_duplicate_case_id_refused() -> None:
    s = suite()
    s["cases"][1]["case_id"] = s["cases"][0]["case_id"]
    with pytest.raises(ValueError):
        reconcile_field_cases(s["cases"])


def test_input_shape_and_bool_amount_refused() -> None:
    s = suite()
    s["cases"][0]["ticket_cents"] = True
    with pytest.raises(ValueError, match="fixed-cent"):
        reconcile_field_cases(s["cases"])
    s = suite()
    s["cases"][0]["unknown"] = "injected"
    with pytest.raises(ValueError, match="invalid"):
        reconcile_field_cases(s["cases"])


def test_human_hold_and_no_auto_effect_even_no_findings() -> None:
    clean = deepcopy(suite()["cases"][0])
    rows = reconcile_field_cases([clean])
    assert rows == [{"case_id": "BETA-001", "flags": []}]
    output = candidate_from_suite(suite())
    assert all(row["authority"] == "HOLD" and row["effect"] == "NONE" for row in output["results"])


def test_decimal_amounts_are_exact_and_nonfinite_rejected() -> None:
    assert invoice_ticket_difference(Decimal("2.03"), Decimal("2.01")) == Decimal("0.02")
    with pytest.raises(ValueError, match="nonfinite"):
        invoice_ticket_difference(Decimal("NaN"), Decimal("1"))


def test_file_reader_rejects_symlinks_and_json_duplicates(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"synthetic":true,"synthetic":true}')
    with pytest.raises(ValueError, match="invalid source JSON"):
        read_suite(bad)
    link = tmp_path / "ln"
    link.symlink_to(bad)
    with pytest.raises(ValueError, match="invalid source file"):
        read_suite(link)
