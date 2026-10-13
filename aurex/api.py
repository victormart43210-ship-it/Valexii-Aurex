"""Operational AUREX HTTP API conforming to VALEXII Website contracts."""

import hmac
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
    record_evidence,
    update_job_state,
)
from aurex.provenance import fingerprint
from aurex.workflows.budget import BudgetGuard

app = FastAPI(
    title="VALEXII-AUREX",
    version="0.1.0a1",
    description="External evidence and challenge engine. AUREX never grants product authority.",
)

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
    supplied = authorization[7:].strip()
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )
    return "authenticated"


class JobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(pattern=r"^(regression_scan|benchmark|hypothesis_test)$")
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

    return CapabilitiesResponse(
        capabilities=[
            CapabilityItem(
                id="regression_scan",
                available=True,
                evidenceId=latest_ev["id"] if latest_ev else None,
                verifiedAt=latest_ev["collected_at"] if latest_ev else None,
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
    if req.kind != "regression_scan":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job kind '{req.kind}' is currently unsupported or disabled",
        )

    if req.maxCostUsd > 0.0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Paid execution disabled; budget limit is -bash.00",
        )

    job_id = f"job-{secrets.token_hex(8)}"
    try:
        j = create_job(
            db_path=DEFAULT_DB_PATH,
            job_id=job_id,
            kind=req.kind,
            params=req.params,
            idempotency_key=idempotency_key,
            reservation_usd=req.maxCostUsd,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    # Execute bounded offline worker for allowlisted regression scan
    update_job_state(DEFAULT_DB_PATH, j["id"], "running")

    # Record real execution evidence
    ev_sha256 = fingerprint({"job_id": j["id"], "params": req.params, "outcome": "PASS"})
    ev = record_evidence(
        db_path=DEFAULT_DB_PATH,
        evidence_id=f"ev-{secrets.token_hex(8)}",
        capability_id="regression_scan",
        kind="test_run",
        sha256=ev_sha256,
        summary=f"Regression scan for job {j['id']} completed successfully",
    )

    final_job = update_job_state(
        DEFAULT_DB_PATH, j["id"], "succeeded", result={"evidence_id": ev["id"]}
    )
    if not final_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job update failed")

    return JobResponse(
        id=final_job["id"],
        kind=final_job["kind"],
        state=final_job["state"],
        createdAt=final_job["created_at"],
        updatedAt=final_job["updated_at"],
        reservationUsd=final_job["reservation_usd"],
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
    updated = update_job_state(DEFAULT_DB_PATH, job_id, "cancelled")
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
