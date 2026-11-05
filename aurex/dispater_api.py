"""DISPATER Industrial Revenue Audit & Dashboard API Endpoints.

Mounts `/v1/dispater` routes for:
- POST /v1/dispater/reconciliation
- GET  /v1/dispater/findings
- GET  /v1/dispater/dashboard

Enforces tenant isolation, authentication, and strictly synthetic execution.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from aurex.dispater_intelligence import InvalidSnapshot, RevenueLeakageEngine

router = APIRouter(prefix="/v1/dispater", tags=["dispater"])

# In-memory tenant store for demonstration results (tenant-isolated)
_DISPATER_RUNS: dict[str, dict[str, Any]] = {}


class ReconciliationRequest(BaseModel):
    tenant_id: str = Field(default="default", min_length=1, max_length=64)
    dataset_type: str = Field(default="SYNTHETIC_ONLY")
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    invoices: list[dict[str, Any]] = Field(default_factory=list)
    rates: list[dict[str, Any]] = Field(default_factory=list)
    payments: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/reconciliation")
def run_reconciliation(payload: ReconciliationRequest) -> dict[str, Any]:
    if payload.dataset_type != "SYNTHETIC_ONLY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SYNTHETIC_ONLY datasets are admitted for demonstration.",
        )
    engine = RevenueLeakageEngine(tenant_id=payload.tenant_id)
    try:
        report = engine.reconcile_records(payload.model_dump())
    except InvalidSnapshot as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation failure: {exc}",
        )

    _DISPATER_RUNS[payload.tenant_id] = report
    return report


@router.get("/findings")
def get_findings(
    tenant_id: str = Query(default="default", min_length=1, max_length=64),
) -> dict[str, Any]:
    run = _DISPATER_RUNS.get(tenant_id)
    if not run:
        return {
            "tenant_id": tenant_id,
            "status": "NO_AUDIT_RUN",
            "findings": [],
            "count": 0,
        }
    return {
        "tenant_id": tenant_id,
        "status": run.get("status"),
        "dataset_sha256": run.get("dataset_sha256"),
        "receipt_sha256": run.get("receipt_sha256"),
        "financial_summary": run.get("financial_summary"),
        "findings": run.get("findings", []),
        "count": len(run.get("findings", [])),
    }


@router.get("/dashboard")
def get_dashboard(
    tenant_id: str = Query(default="default", min_length=1, max_length=64),
) -> dict[str, Any]:
    run = _DISPATER_RUNS.get(tenant_id)
    if not run:
        return {
            "tenant_id": tenant_id,
            "status": "INITIALIZED",
            "last_reconciliation_sha256": None,
            "identified_exposure_usd": "0.00",
            "confirmed_recovery_usd": "0.00",
            "finding_counts": {"total": 0, "critical": 0, "high": 0, "medium": 0},
            "recent_findings": [],
            "system_state": {
                "production_release": "HOLD",
                "financial_authority": "NONE",
                "external_paid_inference": "OFF",
            },
        }
    findings = run.get("findings", [])
    crit = sum(1 for f in findings if f.get("severity") == "CRITICAL")
    high = sum(1 for f in findings if f.get("severity") == "HIGH")
    med = sum(1 for f in findings if f.get("severity") == "MEDIUM")

    return {
        "tenant_id": tenant_id,
        "status": run.get("status"),
        "last_reconciliation_sha256": run.get("receipt_sha256"),
        "identified_exposure_usd": run.get("financial_summary", {}).get(
            "identified_exposure_usd", "0.00"
        ),
        "confirmed_recovery_usd": "0.00",
        "finding_counts": {
            "total": len(findings),
            "critical": crit,
            "high": high,
            "medium": med,
        },
        "recent_findings": findings[:10],
        "system_state": {
            "production_release": "HOLD",
            "financial_authority": "NONE",
            "external_paid_inference": "OFF",
        },
    }
