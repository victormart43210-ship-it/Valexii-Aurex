"""Run the synthetic industrial audit-readiness demonstration.

Usage: python -m aurex.governance_math.industrial_demo
No network, secrets, customer data, or regulatory certification.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

from .industrial_readiness import EvidenceRecord, assess_readiness


def build_demo(as_of: date | None = None) -> dict[str, object]:
    """Produce reproducible, clearly labeled findings from synthetic records."""
    today = as_of or date.today()
    records = (
        EvidenceRecord("demo-driver-01", "driver_qualification", "a" * 64),
        EvidenceRecord("demo-vehicle-01", "vehicle_inspection", "b" * 64, today - timedelta(days=1)),
        EvidenceRecord("demo-maint-01", "maintenance", "c" * 64),
        EvidenceRecord("demo-maint-02", "maintenance", "d" * 64),
        EvidenceRecord("demo-ticket-01", "service_ticket", "unknown"),
    )
    categories = (
        "driver_qualification",
        "vehicle_inspection",
        "maintenance",
        "service_ticket",
        "incident_register",
    )
    findings = assess_readiness(records, categories, as_of=today)
    return {
        "demo": True,
        "authority": "ADVISORY_ONLY_NO_CERTIFICATION",
        "operator": "SYNTHETIC_TOWING_COMPANY",
        "as_of": today.isoformat(),
        "now": [
            {
                "category": finding.category,
                "status": finding.status.value,
                "record_ids": list(finding.record_ids),
            }
            for finding in findings
        ],
        "changed": "NOT_VERIFIED_NO_PRIOR_SNAPSHOT",
        "next": [
            {"category": finding.category, "action": "HUMAN_REVIEW_REQUIRED"}
            for finding in findings if finding.status.value != "PRESENT_NOT_VERIFIED"
        ],
        "why": "Synthetic inventory-only demonstration; regulatory applicability not evaluated",
        "proof": {
            "status": "NOT_VERIFIED",
            "reason": "No authenticated evidence-ledger receipt or independent verifier in demo",
        },
    }


def main() -> None:
    print(json.dumps(build_demo(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
