"""Sovereign Studio: evidence-gated build, intelligence, and growth operations.

Read-only local launch assessment. Never publishes, merges, or grants authority.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Status = Literal["PASS", "FAIL", "NOT RUN", "NOT VERIFIED"]
VALID_STATUSES = frozenset(("PASS", "FAIL", "NOT RUN", "NOT VERIFIED"))
REQUIRED_GATES = (
    "engineering_tests",
    "security_review",
    "independent_verification",
    "frontend_backend_e2e",
    "privacy_review",
    "owner_release_approval",
)
DIVISIONS = ("engineering", "intelligence", "growth")


@dataclass(frozen=True)
class Gate:
    status: Status
    evidence_ref: str | None = None


def assess_launch(gates: dict[str, Gate]) -> dict[str, object]:
    """PASS requires every required gate to have an evidence reference."""
    result: dict[str, dict[str, str | None]] = {}
    for name in REQUIRED_GATES:
        gate = gates.get(name, Gate("NOT RUN"))
        if gate.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status for {name}")
        effective = gate.status
        if effective == "PASS" and not (gate.evidence_ref or "").strip():
            effective = "NOT VERIFIED"
        result[name] = {"status": effective, "evidence_ref": gate.evidence_ref}
    ready = all(item["status"] == "PASS" for item in result.values())
    return {
        "release_ready": ready,
        "decision": "REVIEW_ELIGIBLE" if ready else "HOLD",
        "gates": result,
        "automated_release_authority": "NONE",
    }


def build_campaign_brief(
    *,
    product: str,
    audience: str,
    claim: str,
    claim_evidence: Gate,
) -> dict[str, object]:
    """Generate a draft brief, never an automatic marketing publication."""
    if not product.strip() or not audience.strip() or not claim.strip():
        raise ValueError("Product, audience, and claim are required")
    supported = (
        claim_evidence.status == "PASS"
        and bool((claim_evidence.evidence_ref or "").strip())
    )
    return {
        "division": "growth",
        "product": product,
        "audience": audience,
        "draft_claim": claim,
        "claim_status": "EVIDENCE_LINKED" if supported else "UNVERIFIED",
        "evidence_ref": claim_evidence.evidence_ref if supported else None,
        "publication_status": "DRAFT_ONLY",
        "publish_authority": "NONE",
        "requires_human_review": True,
    }


def load_gates(path: Path) -> dict[str, Gate]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    gates = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            raise ValueError("Gate must be an object")
        status = value.get("status")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status for {key}")
        evidence = value.get("evidence_ref")
        if evidence is not None and not isinstance(evidence, str):
            raise ValueError("Evidence reference must be text")
        gates[key] = Gate(status=status, evidence_ref=evidence)
    return gates


def main() -> None:
    parser = argparse.ArgumentParser(description="AUREX Sovereign Studio launch assessment")
    parser.add_argument("--gates", type=Path, required=True, help="JSON evidence gate input")
    args = parser.parse_args()
    print(json.dumps(assess_launch(load_gates(args.gates)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
