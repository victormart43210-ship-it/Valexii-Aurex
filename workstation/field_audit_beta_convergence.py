"""Combine the existing nine-document AUREX pilot, 100 cases, and assurance.

Strictly local/synthetic. This does not make real audit accuracy or independent
review claims; release authority stays HOLD even when calculations match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from aurex.audit_pilot import run_packet, verify_report
from aurex.field_assurance import assess, blank_claims
from workstation.field_audit_beta_gate import score_candidate, suite
from workstation.field_audit_beta_pipeline import candidate_from_suite

PACKET = Path(__file__).resolve().parents[1] / "fixtures/synthetic_company_packet"


def run_convergence(packet: Path = PACKET) -> dict[str, Any]:
    doc_report = run_packet(packet)
    replay = verify_report(packet, doc_report)
    packet_holds = (
        replay and doc_report["source_count"] == 9
        and doc_report["finding_count"] == 7
        and all(x["status"] == "HOLD" for x in doc_report["challenge_results"])
        and doc_report["production_authority"] == "HOLD"
        and doc_report["independent_verification"] == "NOT_VERIFIED"
    )
    score, candidate_matched = score_candidate(candidate_from_suite(suite()))
    assurance, _ = assess(blank_claims())
    receipt = {
        "kind": "AUREX_FIELD_AUDIT_SYNTHETIC_CONVERGENCE_V1",
        "synthetic": True,
        "source_count": doc_report["source_count"],
        "replay_hash": doc_report["report_sha256"],
        "nine_source_local_replay_match": bool(replay),
        "nine_source_challengers_hold": bool(packet_holds),
        "nine_source_finding_count": doc_report["finding_count"],
        "field_candidate": score,
        "candidate_100_synthetic_cases_matched": candidate_matched,
        "assurance_profile_sha256": assurance["profile_sha256"],
        "assurance_controls": assurance["control_count"],
        "assurance_status": assurance["claim_consistency"],
        "independent_verification": "NOT_VERIFIED",
        "customer_document_processing": "DISABLED",
        "production_release": "HOLD",
        "financial_authority": "NONE",
        "external_spend_usd": 0,
        "status": "SYNTHETIC_LOCAL_REPLAY_ONLY" if packet_holds and candidate_matched else "HOLD",
    }
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(
        receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")).hexdigest()
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX Field Audit synthetic beta convergence ($0, HOLD)")
    parser.add_argument("--packet", type=Path, default=PACKET)
    args = parser.parse_args(argv)
    try:
        receipt = run_convergence(args.packet)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "HOLD", "error": type(exc).__name__,
                          "production_release": "HOLD"}))
        return 2
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0 if receipt["status"] == "SYNTHETIC_LOCAL_REPLAY_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
