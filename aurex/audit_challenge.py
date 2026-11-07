"""Connect synthetic audit claims to canonical AUREX no-self-witness engine."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from aurex.engine import AurexEngine
from aurex.protocol import ChallengeRequest, EvidenceRef


def hold_challenges(findings: list[dict[str, Any]], receipts: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Submit evidence-linked financial claims; no independent challenger => HOLD."""
    receipts_by_id = {item["id"]: item for item in receipts}
    engine = AurexEngine(challengers=())
    responses: list[dict[str, Any]] = []
    for item in findings:
        linked = [receipts_by_id[i] for i in item["sources"]]
        req = ChallengeRequest(
            request_id=f"synthetic-{item['code']}", claim=item["reason"],
            evidence=[EvidenceRef(
                evidence_id=src["id"], source="synthetic_company_packet",
                observed_at=datetime(2026, 10, 18, tzinfo=UTC), sha256=src["sha256"],
            ) for src in linked],
        )
        [outcome] = engine.evaluate(req)
        responses.append({
            "code": item["code"], "status": str(outcome.status),
            "source_ids": item["sources"], "evidence_ids_supplied": len(req.evidence),
            "independent_challenger": "NONE_CONFIGURED",
            "authority_granted": outcome.authority_granted,
        })
    return responses
