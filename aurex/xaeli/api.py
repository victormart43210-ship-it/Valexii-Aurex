"""XAELI HTTP surface. Public chat is unauthenticated and public-knowledge only;
audit endpoints require the service token and an allow-listed tenant."""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from aurex.xaeli import core

router = APIRouter()

adapter = core.CloudflareAdapter()
store = core.KnowledgeStore(core.SYNTHETIC_PUBLIC)
limiter = core.RateLimiter(per_user=int(os.environ.get("AUREX_XAELI_USER_LIMIT", "10")), window_s=60,
                           daily=int(os.environ.get("AUREX_XAELI_DAILY_LIMIT", "1000")))
ledger = core.Ledger()
JOBS: dict[str, dict] = {}


def _auth(authorization: str | None = Header(default=None)) -> str:
    from aurex.api import authenticate
    return authenticate(authorization)


def _tenant_ok(tenant: str | None) -> bool:
    allowed = {t for t in os.environ.get("AUREX_XAELI_TENANTS", "").split(",") if t}
    return bool(tenant) and tenant in allowed


class ChatIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=2000)


@router.get("/v1/xaeli/status")
def xaeli_status():
    ok, why = adapter.ready()
    t2 = core.Tier2Config.from_env()
    return {"tier1": {"ready": ok, "reason": why}, "tier2": {"enabled": t2.enabled, "state": "HOLD"}}


@router.post("/v1/xaeli/chat")
def chat(body: ChatIn, request: Request):
    user = "ip:" + (request.client.host if request.client else "unknown")
    return core.everyday_answer(body.message, None, store, adapter, limiter, user)


class AuditIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: str = Field(min_length=1, max_length=64)
    provider: str = Field(max_length=64)
    estimate_usd: str = "0"
    authorization_receipt: str | None = Field(default=None, max_length=256)


@router.post("/v1/xaeli/audit/{tenant}/jobs")
def audit_request(tenant: str, body: AuditIn, _: str = Depends(_auth)):
    try:
        est = Decimal(body.estimate_usd)
    except InvalidOperation:
        raise HTTPException(422, "invalid estimate")
    job = JOBS.setdefault(body.job_id, {"id": body.job_id, "tenant": tenant, "state": "READY"})
    result = core.tier2_gate(core.Tier2Config.from_env(), ledger, authenticated=True, tenant=tenant,
                             tenant_authorized=_tenant_ok(tenant), job=job, provider=body.provider,
                             estimate_usd=est, authorization_receipt=body.authorization_receipt)
    return {"jobId": body.job_id, "state": "HOLD", "estimateUsd": str(est), **result}


@router.post("/v1/xaeli/audit/{tenant}/jobs/{job_id}/cancel")
def audit_cancel(tenant: str, job_id: str, _: str = Depends(_auth)):
    job = JOBS.get(job_id)
    if not _tenant_ok(tenant) or not job or job["tenant"] != tenant:
        raise HTTPException(404, "not found")
    job["state"] = "CANCELLED"
    ledger.jobs[job_id] = "CANCELLED"
    return {"jobId": job_id, "state": "CANCELLED"}
