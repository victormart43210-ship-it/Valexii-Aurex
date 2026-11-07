"""DISPATER routes for linked records and stored-finding explanations.

These routes use the existing tenant grant. They do not call a model and they
do not change confirmed recovery.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from aurex.customer_sovereignty import assert_no_effect
from aurex.dispater_api import MAX_ROWS, TENANT_PATTERN, PrincipalDep, authorize_tenant
from aurex.dispater_intelligence import InvalidSnapshot, RevenueLeakageEngine
from aurex.dispater_store import get_run, latest_run, save_run
from aurex.relationships.documents import parser_inventory
from aurex.relationships.explain import explain_finding
from aurex.relationships.log import project
from aurex.relationships.store import read_projection, save_projection

router = APIRouter(prefix="/v1/dispater", tags=["dispater-relationships"])


class RelationshipRequest(BaseModel):
    tenant_id: str = Field(pattern=TENANT_PATTERN, max_length=64)
    dataset_type: str = Field(default="SYNTHETIC_ONLY")
    jobs: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    invoices: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    rates: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    payments: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_ROWS)
    equipment: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    labor: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    companies: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    wells: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    crews: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    contracts: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)
    approvals: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_ROWS)


def _financial_dataset(payload: RelationshipRequest) -> dict[str, Any]:
    dataset: dict[str, Any] = {
        "tenant_id": payload.tenant_id,
        "dataset_type": payload.dataset_type,
        "jobs": payload.jobs,
        "invoices": payload.invoices,
        "rates": payload.rates,
        "payments": payload.payments,
    }
    if payload.equipment is not None:
        dataset["equipment"] = payload.equipment
    if payload.labor is not None:
        dataset["labor"] = payload.labor
    return dataset


def _context_dataset(payload: RelationshipRequest, financial: dict[str, Any]) -> dict[str, Any]:
    dataset = dict(financial)
    for name in ("companies", "wells", "crews", "contracts", "approvals"):
        value = getattr(payload, name)
        if value:
            dataset[name] = value
    return dataset


@router.get("/parser-inventory")
def get_parser_inventory(principal: PrincipalDep, tenant_id: str = Query(pattern=TENANT_PATTERN)) -> dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, tenant_id)
    return parser_inventory()


@router.post("/relationships")
def post_relationships(payload: RelationshipRequest, principal: PrincipalDep) -> dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, payload.tenant_id)
    financial = _financial_dataset(payload)
    try:
        report = RevenueLeakageEngine(tenant_id=payload.tenant_id).reconcile_records(financial)
        projection = project(_context_dataset(payload, financial), str(report["dataset_sha256"]))
        stored_report, _created = save_run(payload.tenant_id, report)
        stored_links = save_projection(payload.tenant_id, projection)
    except InvalidSnapshot as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    summary = stored_report["financial_summary"]
    return {
        "authority_state": "HOLD",
        "financial_authority": "NONE",
        "effect": "NONE",
        "confirmed_recovery_usd": summary["confirmed_recovery_usd"],
        "identified_exposure_usd": summary["identified_exposure_usd"],
        "withheld_unresolved_usd": summary["withheld_unresolved_usd"],
        "potential_underbilling_usd": summary["potential_underbilling_usd"],
        "potential_overbilling_usd": summary["potential_overbilling_usd"],
        "unverified_exposure_usd": summary["unverified_exposure_usd"],
        "dataset_sha256": stored_report["dataset_sha256"],
        "run_id": stored_report["run_id"],
        "relationships": {
            "object_count": len(stored_links["objects"]),
            "event_count": len(stored_links["events"]),
            "relation_count": len(stored_links["relations"]),
            "unresolved": projection["unresolved"],
            "context_sha256": projection["context_sha256"],
        },
    }


@router.get("/relationships")
def get_relationships(
    principal: PrincipalDep,
    tenant_id: str = Query(pattern=TENANT_PATTERN),
    dataset_sha256: str = Query(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"),
) -> dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, tenant_id)
    stored = read_projection(tenant_id, dataset_sha256)
    if not stored["objects"] and not stored["events"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No relationship projection for this tenant")
    return stored


@router.get("/explanations")
def get_explanation(
    principal: PrincipalDep,
    tenant_id: str = Query(pattern=TENANT_PATTERN),
    finding_id: str = Query(min_length=1, max_length=200),
    run_id: str | None = Query(default=None, min_length=1, max_length=80),
) -> dict[str, Any]:
    assert_no_effect()
    authorize_tenant(principal, tenant_id)
    report = get_run(tenant_id, run_id) if run_id else latest_run(tenant_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No stored run for this tenant")
    finding = next((item for item in report.get("findings", []) if item.get("finding_id") == finding_id), None)
    if finding is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Finding is not in the stored run")
    try:
        return explain_finding(finding)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
