"""DISPATER offline synthetic demo orchestrator, no external calls or actions.

Binds the existing deterministic revenue and evidence-readiness pilot modules.
Review states are observations only; financial, tax, DOT, and dispatch effects
are never authorized by this module. NVIDIA remains NOT RUN by default.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aurex.dispater_evidence import assess_synthetic_readiness
from aurex.dispater_pilot import InvalidSnapshot, audit_synthetic, digest

MAX_INPUT_BYTES = 512 * 1024
DECISIONS = frozenset({"ACKNOWLEDGED", "DISPUTED", "REFER_TO_SPECIALIST"})
SECTORS = frozenset({"towing", "oilfield"})


def _valid_text(value: object, limit: int = 280) -> bool:
    return isinstance(value, str) and 0 < len(value) <= limit and "\x00" not in value


def _finding_key(domain: str, finding: dict[str, Any]) -> str:
    return digest({"domain": domain, "finding": finding})[:24]


def build_demo_report(package: dict[str, Any]) -> dict[str, Any]:
    """Generate a deterministic, non-authoritative manager-review report.

    Inputs MUST be fictional; the synthetic marker is a *declared* flag and not
    a reliable personal-data detector. Never expose this to customer uploads.
    """
    if not isinstance(package, dict) or set(package) != {
        "dataset_type", "sector", "revenue", "evidence", "review",
    }:
        raise InvalidSnapshot("unknown or missing package fields")
    if package["dataset_type"] != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("live/customer inputs are prohibited")
    sector = package["sector"]
    if not isinstance(sector, str) or sector not in SECTORS:
        raise InvalidSnapshot("sector must be towing or oilfield")
    revenue = audit_synthetic(package["revenue"])
    evidence = assess_synthetic_readiness(package["evidence"])

    review = package["review"]
    if not isinstance(review, dict) or set(review) != {"reviewer_id", "decisions"}:
        raise InvalidSnapshot("invalid review envelope")
    reviewer = review["reviewer_id"]
    if not _valid_text(reviewer, 80) or not reviewer.startswith("DEMO_"):
        raise InvalidSnapshot("reviewer must be a demo-only identifier")
    decisions = review["decisions"]
    if not isinstance(decisions, list) or len(decisions) > 2000:
        raise InvalidSnapshot("invalid decision list")

    findings: list[dict[str, Any]] = []
    for domain, rows in (
        ("REVENUE", revenue["findings"]),
        ("RECORD_READINESS", evidence["findings"]),
    ):
        for item in rows:
            identifier = _finding_key(domain, item)
            findings.append({
                "finding_id": identifier,
                "domain": domain,
                "code": item["code"],
                "source_evidence": item.get("evidence", []),
                "rule_evidence_hash": item.get("rule_sha256"),
                "subject": item.get("subject", item.get("subject_id")),
                "explanation": item.get("detail", "Rule metadata requires a human review."),
                "explanation_provenance": "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
                "review": {"status": "NOT_REVIEWED"},
            })
    findings.sort(key=lambda x: (x["domain"], x["code"], x["finding_id"]))
    indexed = {f["finding_id"]: f for f in findings}
    used: set[str] = set()
    for decision in decisions:
        if not isinstance(decision, dict) or set(decision) != {
            "finding_id", "decision", "note",
        }:
            raise InvalidSnapshot("invalid review decision fields")
        finding_id = decision["finding_id"]
        disposition = decision["decision"]
        note = decision["note"]
        if not isinstance(finding_id, str) or finding_id not in indexed or finding_id in used:
            raise InvalidSnapshot("unknown or duplicate finding review")
        if not isinstance(disposition, str) or disposition not in DECISIONS or not isinstance(note, str) or len(note) > 280:
            raise InvalidSnapshot("invalid review decision or note")
        used.add(finding_id)
        indexed[finding_id]["review"] = {
            "status": disposition,
            "note": note,
            "reviewer": reviewer,
            "effect_authority": "NONE",
        }

    report: dict[str, Any] = {
        "schema": "dispater.synthetic.end_to_end.v1",
        "sector": sector,
        "input_sha256": digest(package),
        "status": "HOLD",
        "dataset_classification": "FICTIONAL_DATA_ONLY",
        "independent_verification": "NOT VERIFIED",
        "nvidia_inference": "NOT RUN",
        "nvidia_reason": "Provider not connected or authorized for this demo.",
        "revenue_snapshot_sha256": revenue["dataset_sha256"],
        "readiness_snapshot_sha256": evidence["snapshot_sha256"],
        "reviewer": reviewer,
        "counts": {
            "revenue_findings": len(revenue["findings"]),
            "readiness_findings": len(evidence["findings"]),
            "reviewed": len(used),
            "awaiting_review": len(findings) - len(used),
        },
        "findings": findings,
        "limits": (
            "Not an IRS/DOT audit, tax opinion, regulatory certification, or financial authorization. "
            "Applicable legal obligations and source data have not been independently established. "
            "No customer uploads, connector writes, payments, dispatch changes, or model calls."
        ),
    }
    report["self_issued_receipt_sha256"] = digest(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="DISPATER fictional-data audit/review demo")
    parser.add_argument("--input", type=Path, required=True, help="synthetic JSON package")
    parser.add_argument("--output", type=Path, required=True, help="JSON report path")
    args = parser.parse_args()
    if args.input.stat().st_size > MAX_INPUT_BYTES:
        parser.error("synthetic input exceeds 512KiB")
    try:
        package = json.loads(args.input.read_text(encoding="utf-8"))
        result = build_demo_report(package)
    except (InvalidSnapshot, json.JSONDecodeError, UnicodeDecodeError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"sector": result["sector"], "counts": result["counts"], "status": result["status"], "nvidia": result["nvidia_inference"], "report": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
