"""Fixed fictional offline observations; no provider or user data admission."""
from __future__ import annotations

from typing import Any

from aurex.real_offline_probe import execute_sqlite_roundtrip


def execute_probe(params: dict[str, Any]) -> dict[str, Any]:
    if params == {"probe": "synthetic_field_audit_v1"}:
        # Selective, source-pinned PR #99 deterministic candidate; the
        # independent reference is a transparent *fixture*, not an
        # external witness of model intelligence or field accuracy.
        from workstation.field_audit_beta_gate import score_candidate, suite
        from workstation.field_audit_beta_pipeline import candidate_from_suite

        cases = suite()
        candidate = candidate_from_suite(cases)
        report, matched = score_candidate(candidate)
        if not matched:
            raise ValueError("Synthetic candidate did not match its fixture")
        observation = {
            "probe": "synthetic_field_audit_v1",
            "synthetic": True,
            "suite_sha256": cases["suite_sha256"],
            "case_count": report["total_cases"],
            "exact_case_matches": report["exact_case_matches"],
            "finding_labels": report["true_positive_flags"],
            "false_positive_flags": report["false_positive_flags"],
            "false_negative_flags": report["false_negative_flags"],
            "result": report["status"],
            "independent_verification": "NOT_VERIFIED",
            "real_document_accuracy": "NOT_MEASURED",
            "authority": "HOLD",
            "effect": "NONE",
            "production_release": "HOLD",
        }
    else:
        observation = execute_sqlite_roundtrip(params)
    return observation
