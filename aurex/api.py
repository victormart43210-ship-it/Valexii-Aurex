"""Operational AUREX HTTP API conforming to VALEXII Website contracts."""

import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from aurex.database import (
    DEFAULT_DB_PATH,
    create_job,
    get_job,
    list_evidence,
    list_jobs,
)
from aurex.fenced_worker import cancel_job, claim_job, finalize_job
from aurex.governance_math.industrial_api import router as industrial_demo_router
from aurex.governance_math.research_api import router as research_advice_router
from aurex.industrial_execution import router as towing_router
from aurex.integrations.pilot_policy import review_synthetic_pilot
from aurex.real_offline_probe import execute_sqlite_roundtrip
from aurex.workflows.budget import BudgetGuard
from aurex_foundation.correlation import CorrelationMiddleware
from aurex_foundation.opa import evaluate_policy

app = FastAPI(
    title="VALEXII-AUREX",
    version="0.1.0a1",
    description="External evidence and challenge engine. AUREX never grants product authority.",
)

app.add_middleware(CorrelationMiddleware)

budget_guard = BudgetGuard(limit_usd=Decimal("0.00"))


def get_token() -> str:
    service_token = os.environ.get("AUREX_SERVICE_TOKEN")
    admin_token = os.environ.get("AUREX_ADMIN_TOKEN")

    if service_token and admin_token and service_token != admin_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conflicting authentication tokens configured",
        )

    token = service_token or admin_token
    if not token or len(token) < 32:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication token unconfigured or insecure",
        )
    return token


def authenticate(authorization: str | None = Header(default=None)) -> str:
    expected = get_token()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    supplied = authorization[7:]
    if not supplied.isascii() or supplied != supplied.strip():
        raise HTTPException(status_code=401, detail="Malformed authorization credentials")
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )
    return "authenticated"


# Opt-in, authenticated, advisory-only mathematics; no capability or authority claims.
app.include_router(research_advice_router, dependencies=[Depends(authenticate)])
app.include_router(industrial_demo_router, dependencies=[Depends(authenticate)])
app.include_router(towing_router, dependencies=[Depends(authenticate)])


class JobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(pattern=r"^(regression_scan|regression-scan|benchmark|hypothesis_test)$")
    params: dict[str, Any] = Field(default_factory=dict)
    maxCostUsd: float = Field(default=0.0, ge=0.0, le=100.0)


class JobResponse(BaseModel):
    id: str
    kind: str
    state: str
    createdAt: str
    updatedAt: str
    reservationUsd: float


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    nextCursor: str | None = None


class EvidenceItem(BaseModel):
    id: str
    capabilityId: str
    kind: str
    collectedAt: str
    sha256: str
    summary: str


class EvidenceListResponse(BaseModel):
    evidence: list[EvidenceItem]


class CapabilityItem(BaseModel):
    id: str
    available: bool
    evidenceId: str | None = None
    verifiedAt: str | None = None


class CapabilitiesResponse(BaseModel):
    capabilities: list[CapabilityItem]


class BudgetResponse(BaseModel):
    limitUsd: float
    reservedUsd: float
    spentUsd: float
    period: str = "month"


@app.get("/v1/health")
@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "0.1.0a1",
        "time": datetime.now(UTC).isoformat(),
    }


@app.get("/v1/capabilities", response_model=CapabilitiesResponse)
def capabilities(_: str = Depends(authenticate)) -> CapabilitiesResponse:
    ev_records = list_evidence(DEFAULT_DB_PATH)
    latest_ev = ev_records[0] if ev_records else None
    ev_id = latest_ev["id"] if latest_ev else None

    return CapabilitiesResponse(
        capabilities=[
            CapabilityItem(
                id="regression_scan",
                available=os.environ.get("AUREX_ENABLE_OFFLINE_LAB") == "1",
                evidenceId=ev_id,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="memory_graph",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="evidence_vault",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="model_benchmarking",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="hypothesis_testing",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="computer_use",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="remote_inference",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
        ]
    )


@app.get("/v1/jobs", response_model=JobListResponse)
def get_jobs(_: str = Depends(authenticate)) -> JobListResponse:
    raw_jobs = list_jobs(DEFAULT_DB_PATH)
    res = [
        JobResponse(
            id=j["id"],
            kind=j["kind"],
            state=j["state"],
            createdAt=j["created_at"],
            updatedAt=j["updated_at"],
            reservationUsd=j["reservation_usd"],
        )
        for j in raw_jobs
    ]
    return JobListResponse(jobs=res, nextCursor=None)


@app.post("/v1/jobs", response_model=JobResponse)
def create_job_endpoint(
    req: JobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    _: str = Depends(authenticate),
) -> JobResponse:
    canonical_kind = "regression_scan" if req.kind == "regression-scan" else req.kind
    if canonical_kind != "regression_scan":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job kind '{req.kind}' is currently unsupported or disabled",
        )

    if req.maxCostUsd > 0:
        raise HTTPException(status_code=402, detail="Paid execution disabled")
    if os.environ.get("AUREX_ENABLE_OFFLINE_LAB") != "1":
        raise HTTPException(status_code=503, detail="Worker unavailable: offline worker disabled")
    if req.params != {"probe": "sqlite_roundtrip_v1"}:
        raise HTTPException(status_code=422, detail="Unsupported probe")
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(status_code=422, detail="Idempotency-Key required")
    if os.environ.get("AUREX_OPA_PILOT_ENABLED") == "1":
        if os.environ.get("AUREX_OPA_OPERATOR_APPROVED") != "1":
            raise HTTPException(status_code=503, detail="Policy approval required")

        if os.environ.get("AUREX_OPA_SYNTHETIC_ONLY") != "1":
            raise HTTPException(status_code=503, detail="Synthetic-only policy gate required")

        policy = evaluate_policy({
            "kind": canonical_kind,
            "synthetic": True,
            "probe": "sqlite_roundtrip_v1",
            "max_cost_usd": 0,
        })

        decision = review_synthetic_pilot(
            synthetic=True,
            explicit_operator_approval=True,
            policy_response={
                "result": {"allow": policy.disposition == "QUALIFIED"}
            },
        )

        if not decision.permitted_for_review:
            raise HTTPException(status_code=503, detail="Policy review HOLD")

    try:
        job = create_job(
            DEFAULT_DB_PATH, f"job-{secrets.token_hex(12)}", canonical_kind,
            req.params, idempotency_key=idempotency_key, reservation_usd=0.0,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    job_id = str(job["id"])
    resolved_job: dict[str, Any] | None = job
    if job["state"] == "queued":
        worker_id = "aurex-local-worker-1"
        claimed = claim_job(DEFAULT_DB_PATH, job_id, worker_id)
        if claimed is not None:
            try:
                observation = execute_sqlite_roundtrip(req.params)
                digest = hashlib.sha256(
                    json.dumps(observation, sort_keys=True).encode()
                ).hexdigest()
                resolved_job = finalize_job(
                    DEFAULT_DB_PATH, job_id, worker_id,
                    str(claimed["lease_token"]), int(claimed["lease_generation"]),
                    observation, digest, f"ev-{secrets.token_hex(12)}",
                )
            except Exception:
                # Do not rewrite a cancelled or superseded worker's terminal state.
                raise HTTPException(status_code=503, detail="Probe not finalized; execution not verified") from None
        else:
            resolved_job = get_job(DEFAULT_DB_PATH, job_id)
    else:
        resolved_job = get_job(DEFAULT_DB_PATH, job_id)
    if resolved_job is None:
        raise HTTPException(status_code=500, detail="Job state unavailable")
    return JobResponse(
        id=resolved_job["id"], kind=resolved_job["kind"], state=resolved_job["state"],
        createdAt=resolved_job["created_at"], updatedAt=resolved_job["updated_at"],
        reservationUsd=resolved_job["reservation_usd"],
    )

@app.get("/v1/jobs/{job_id}", response_model=JobResponse)
def get_job_endpoint(job_id: str, _: str = Depends(authenticate)) -> JobResponse:
    j = get_job(DEFAULT_DB_PATH, job_id)
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResponse(
        id=j["id"],
        kind=j["kind"],
        state=j["state"],
        createdAt=j["created_at"],
        updatedAt=j["updated_at"],
        reservationUsd=j["reservation_usd"],
    )


@app.post("/v1/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job_endpoint(job_id: str, _: str = Depends(authenticate)) -> JobResponse:
    j = get_job(DEFAULT_DB_PATH, job_id)
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    updated = cancel_job(DEFAULT_DB_PATH, job_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResponse(
        id=updated["id"],
        kind=updated["kind"],
        state=updated["state"],
        createdAt=updated["created_at"],
        updatedAt=updated["updated_at"],
        reservationUsd=updated["reservation_usd"],
    )


@app.get("/v1/evidence", response_model=EvidenceListResponse)
def get_evidence(_: str = Depends(authenticate)) -> EvidenceListResponse:
    raw_ev = list_evidence(DEFAULT_DB_PATH)
    items = [
        EvidenceItem(
            id=e["id"],
            capabilityId=e["capability_id"],
            kind=e["kind"],
            collectedAt=e["collected_at"],
            sha256=e["sha256"],
            summary=e["summary"],
        )
        for e in raw_ev
    ]
    return EvidenceListResponse(evidence=items)


@app.get("/v1/budgets", response_model=BudgetResponse)
def get_budgets(_: str = Depends(authenticate)) -> BudgetResponse:
    return BudgetResponse(
        limitUsd=float(budget_guard.limit_usd),
        reservedUsd=float(budget_guard.reserved_usd),
        spentUsd=float(budget_guard.spent_usd),
        period="month",
    )
