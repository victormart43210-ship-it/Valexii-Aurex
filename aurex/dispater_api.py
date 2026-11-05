"""DISPATER Industrial Revenue Audit & Dashboard API Endpoints.

Mounts `/v1/dispater` routes for:
- POST /v1/dispater/reconciliation
- GET  /v1/dispater/findings
- GET  /v1/dispater/dashboard

Enforces tenant isolation, token-principal binding, durable SQLite storage, and strictly synthetic execution.
"""

from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from aurex.dispater_intelligence import (
    DEFAULT_DISPATER_DB,
    InvalidSnapshot,
    RevenueLeakageEngine,
    TenantAuthorizationError,
    get_latest_audit_run,
)

router = APIRouter(prefix="/v1/dispater", tags=["dispater"])


def authorize_tenant_principal(
    tenant_id: str,
    authorization: str | None = Header(default=None),
) -> str:
    """Authorize authenticated principal against requested tenant.

    Guarantees:
    - Never treat unverified caller tenant ID as proof of access.
    - Tenant isolation fails closed if principal is not authorized for tenant.
    - Rejects missing, invalid, or cross-tenant manipulation attempts.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    supplied = authorization[7:].strip()
    if not supplied.isascii() or len(supplied) < 32:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
        )

    # In production, tenant mapping derives from cryptographically verified claims or token binding
    # For synthetic demonstration and staging: tokens scoped to tenant-specific secrets or admin service token
    service_token = os.environ.get("AUREX_SERVICE_TOKEN")
    admin_token = os.environ.get("AUREX_ADMIN_TOKEN")

    # If tenant-specific token configured:
    tenant_env_var = f"AUREX_TENANT_TOKEN_{tenant_id.replace('-', '_').upper()}"
    tenant_token = os.environ.get(tenant_env_var)

    authorized = False
    if tenant_token and hmac.compare_digest(supplied, tenant_token):
        authorized = True
    elif service_token and hmac.compare_digest(supplied, service_token):
        # Global service token authorized for all synthetic tenants
        authorized = True
    elif admin_token and hmac.compare_digest(supplied, admin_token):
        authorized = True

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Principal not authorized for requested tenant",
        )

    return tenant_id


class ReconciliationRequest(BaseModel):
    tenant_id: str = Field(default="default", min_length=1, max_length=64)
    dataset_type: str = Field(default="SYNTHETIC_ONLY")
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    invoices: list[dict[str, Any]] = Field(default_factory=list)
    rates: list[dict[str, Any]] = Field(default_factory=list)
    payments: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/reconciliation")
def run_reconciliation(
    payload: ReconciliationRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    # 1. Authorize principal for target tenant
    authorize_tenant_principal(payload.tenant_id, authorization=authorization)

    if payload.dataset_type != "SYNTHETIC_ONLY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SYNTHETIC_ONLY datasets are admitted for demonstration.",
        )

    engine = RevenueLeakageEngine(tenant_id=payload.tenant_id, db_path=DEFAULT_DISPATER_DB)
    try:
        report = engine.reconcile_records(payload.model_dump())
    except TenantAuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except InvalidSnapshot as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation failure: {exc}",
        )

    return report


@router.get("/findings")
def get_findings(
    tenant_id: str = Query(default="default", min_length=1, max_length=64),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    authorize_tenant_principal(tenant_id, authorization=authorization)

    run = get_latest_audit_run(tenant_id, db_path=DEFAULT_DISPATER_DB)
    if not run:
        return {
            "tenant_id": tenant_id,
            "status": "NO_AUDIT_RUN",
            "findings": [],
            "count": 0,
        }
    return {
        "tenant_id": tenant_id,
        "run_id": run.get("run_id"),
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
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    authorize_tenant_principal(tenant_id, authorization=authorization)

    run = get_latest_audit_run(tenant_id, db_path=DEFAULT_DISPATER_DB)
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
        "run_id": run.get("run_id"),
        "status": run.get("status"),
        "last_reconciliation_sha256": run.get("receipt_sha256"),
        "identified_exposure_usd": run.get("financial_summary", {}).get(
            "identified_exposure_usd", "0.00"
        ),
        "potential_underbilling_usd": run.get("financial_summary", {}).get(
            "potential_underbilling_usd", "0.00"
        ),
        "potential_overbilling_usd": run.get("financial_summary", {}).get(
            "potential_overbilling_usd", "0.00"
        ),
        "unverified_exposure_usd": run.get("financial_summary", {}).get(
            "unverified_exposure_usd", "0.00"
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
