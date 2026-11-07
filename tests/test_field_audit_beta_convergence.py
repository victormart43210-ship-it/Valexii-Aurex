"""Cross-vertical synthetic beta convergence; no production authority."""
from __future__ import annotations

import hashlib
import json

import pytest

from workstation.field_audit_beta_convergence import PACKET, run_convergence


def test_nine_source_and_100_case_workflow_are_connected() -> None:
    receipt = run_convergence(PACKET)
    assert receipt["source_count"] == 9
    assert receipt["nine_source_local_replay_match"] is True
    assert receipt["nine_source_challengers_hold"] is True
    assert receipt["nine_source_finding_count"] == 7
    assert receipt["candidate_100_synthetic_cases_matched"] is True
    assert receipt["field_candidate"]["exact_case_matches"] == 100
    assert receipt["field_candidate"]["false_positive_flags"] == 0
    assert receipt["field_candidate"]["false_negative_flags"] == 0
    assert receipt["assurance_controls"] == 12
    assert receipt["assurance_status"] == "HOLD"
    assert receipt["external_spend_usd"] == 0
    assert receipt["production_release"] == "HOLD"
    assert receipt["independent_verification"] == "NOT_VERIFIED"
    assert receipt["status"] == "SYNTHETIC_LOCAL_REPLAY_ONLY"
    digested = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    assert hashlib.sha256(json.dumps(digested, sort_keys=True,
                                    separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == receipt["receipt_sha256"]


def test_incomplete_or_corrupted_packet_does_not_generate_success(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        run_convergence(tmp_path)
