"""Authenticated fixed-fixture demo; no Onyx process, DB write or external calls."""

from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from aurex.dispater_pilot import audit_synthetic
from aurex.integrations.onyx import OnyxAdapter, OnyxConfig, Principal

router = APIRouter(prefix="/v1/retrieval/onyx")


class DemoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: Literal["unmatched_towing_invoice_v1"] = "unmatched_towing_invoice_v1"


def synthetic_corpus() -> bytes:
    """Server-owned records in the observed upstream SearchResponse wire schema."""
    import json

    records = [
        (
            "dispatch/TOW-101",
            "Towing dispatch",
            "Fictional TOW-101 dispatched; no approved invoice match.",
        ),
        (
            "invoice/INV-101",
            "Towing invoice",
            "Fictional INV-101 refers to TOW-999; amount USD 150.00.",
        ),
        (
            "service/TOW-101",
            "Service documentation",
            "Fictional TOW-101 service ticket awaits manager signature.",
        ),
        (
            "oilfield/FT-1",
            "Oilfield field ticket",
            "Fictional FT-1: 2 hours; approved rate missing.",
        ),
        (
            "equipment/EQ-1",
            "Equipment record",
            "Fictional EQ-1 inspection dated 2020; current condition unknown.",
        ),
        (
            "procedure/REVIEW",
            "Operational procedure",
            "Fictional procedure: human review required before billing.",
        ),
    ]
    return json.dumps(
        {
            "results": [
                dict(
                    citation_id=i,
                    title=title,
                    content=content,
                    link="https://records.example/" + locator,
                    source_type="file",
                    updated_at="2026-10-25T00:00:00Z",
                )
                for i, (locator, title, content) in enumerate(records, start=1)
            ]
        }
    ).encode()


@router.post("/demo")
def demo(request: DemoRequest) -> dict[str, Any]:
    config = OnyxConfig(
        origin="https://onyx.invalid",
        allowed_host="onyx.invalid",
        token="synthetic-unused",
        tenant_id="synthetic-owner",
        principal_id="owner",
        source_hosts=frozenset({"records.example"}),
        enabled=True,
        isolated_owner_admitted=True,
        local_only_inference_admitted=True,
    )
    retrieval = OnyxAdapter(config).search(
        "Find supporting records for unmatched towing invoice INV-101",
        Principal("owner", "synthetic-owner"),
        request_id=request.scenario,
        transport=lambda *_: (200, synthetic_corpus()),
        now=datetime(2026, 10, 26, tzinfo=UTC),
    )
    # Separate structured fixture: NEVER derive authoritative numbers from retrieved prose.
    reconciliation = audit_synthetic(
        dict(
            dataset_type="SYNTHETIC_ONLY",
            jobs=[
                dict(
                    job_id="TOW-101", customer_id="FICTIONAL", service_code="TOW", date="2026-10-25"
                )
            ],
            invoices=[dict(invoice_id="INV-101", job_id="TOW-999", amount="150.00", status="open")],
            payments=[],
            rates=[],
        )
    )
    return dict(
        mode="SYNTHETIC_CONTRACT_DEMO",
        authority="NONE",
        release="HOLD",
        retrieval=retrieval.model_dump(),
        admissible_evidence=[],
        reconciliation=reconciliation,
        xaeli=dict(
            NOW="Unmatched fictional invoice; supporting records are candidates only.",
            CHANGED="NOT_VERIFIED",
            NEXT="Human reviewer must verify source records and approvals.",
            WHY="Retrieved prose cannot authorize charges or establish a reconciliation match.",
            PROOF="Synthetic fixtures and consistency hashes only; Onyx live interoperability NOT RUN.",
        ),
    )
