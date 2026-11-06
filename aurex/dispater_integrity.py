"""Conservative evidence adapter for submitted synthetic financial snapshots.

A submitted snapshot is one unauthenticated root. Row count and uploader labels
cannot turn it into independent corroboration. No clock is invented for imports.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from aurex.evidence_integrity import EvidenceGraph, EvidenceNode, evaluate_evidence


def qualify_findings(findings: list[dict[str, Any]], *, tenant_id: str,
                     snapshot_digest: str) -> None:
    """Add qualification to calculated candidates before the report is sealed."""
    root = EvidenceNode(node_id="snapshot", tenant_id=tenant_id, domain="financial",
                        content_digest=snapshot_digest)
    for finding in findings:
        nodes = {entry["record_sha256"]: EvidenceNode(
            node_id=entry["record_sha256"], tenant_id=tenant_id, domain="financial",
            content_digest=entry["record_sha256"], parent_ids=("snapshot",),
        ) for entry in finding["evidence"]}
        claim = EvidenceNode(node_id="finding", tenant_id=tenant_id, domain="financial",
                             content_digest=finding["finding_sha256"],
                             parent_ids=tuple(nodes) or ("snapshot",))
        graph = EvidenceGraph(nodes=(root, *nodes.values(), claim))
        assessment = evaluate_evidence(graph, "finding", tenant_id=tenant_id,
                                       domain="financial", now=datetime.now(UTC),
                                       conflict=finding["code"] == "AMBIGUOUS_RATE")
        state = assessment.state.value
        if finding["code"] in {"RATE_UNVERIFIED", "ORPHAN_INVOICE", "ORPHAN_PAYMENT"}:
            state = "UNAVAILABLE"
        finding["evidence_integrity"] = {
            "qualification": "CALCULATED",
            "observation_state": state,
            "independent_root_count": assessment.structural_root_count,
            "independent_verification": "NOT VERIFIED",
            "source_root_sha256": snapshot_digest,
            "reasons": list(assessment.reasons) + [
                "Submitted snapshot is one unauthenticated source; structural roots are not independent witnesses.",
                "Import observation time and original source authenticity are unavailable.",
            ],
        }
        finding["xaeli_explanation"]["next"] = (
            "Human review required before any financial action. "
            + finding["xaeli_explanation"]["next"]
        )
        finding["xaeli_explanation"]["proof"] += (
            f"; Submitted source root SHA-256: {snapshot_digest}. "
            "Calculated candidate only; source authenticity and freshness NOT VERIFIED."
        )
