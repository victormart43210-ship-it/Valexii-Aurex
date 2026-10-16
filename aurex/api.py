"""Operational AUREX HTTP API conforming to VALEXII Website contracts."""

import hmac
import os
import json
import hashlib
import secrets
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from aurex.database import (
    DEFAULT_DB_PATH,
    create_job,
    record_evidence,
    get_job,
    list_evidence,
    list_jobs,
    update_job_state,
)
from aurex.real_offline_probe import execute_sqlite_roundtrip
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
    ev_id = latest_ev["id"] if latest_ev else None
    ev_time = latest_ev["collected_at"] if latest_ev else None

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
    if req.kind != "regression_scan":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job kind '{req.kind}' is currently unsupported or disabled",
        )

    if req.maxCostUsd > 0.0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Paid execution disabled; budget limit is $0.00",
        )

    if os.environ.get("AUREX_ENABLE_OFFLINE_LAB") != "1":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Offline evaluation worker disabled; no job or evidence created",
        )
    if req.params != {"probe": "sqlite_roundtrip_v1"}:
        raise HTTPException(status_code=422, detail="Unsupported offline probe parameters")
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(status_code=422, detail="Bounded Idempotency-Key required")
    try:
        job = create_job(
            DEFAULT_DB_PATH, f"job-{secrets.token_hex(12)}", req.kind,
            req.params, idempotency_key=idempotency_key, reservation_usd=0.0,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    job_id = str(job["id"])
    claimed = None
    if job["state"] == "queued":
        claimed = update_job_state(DEFAULT_DB_PATH, job_id, "running")
        if claimed is None:
            current = get_job(DEFAULT_DB_PATH, job_id)
            if current is None:
                raise HTTPException(status_code=500, detail="Job disappeared")
            job = current
        else:
            job = claimed
    if claimed is not None:
        try:
            observation = execute_sqlite_roundtrip(req.params)
            digest = hashlib.sha256(
                json.dumps(observation, sort_keys=True).encode("utf-8")
            ).hexdigest()
            ev_id = f"ev-{secrets.token_hex(12)}"
            record_evidence(
                DEFAULT_DB_PATH, ev_id, "regression_scan", "offline_probe",
                digest, f"SQLite roundtrip executed for {job_id}; independent verification NOT VERIFIED",
            )
            job = update_job_state(
                DEFAULT_DB_PATH, job_id, "succeeded",
                result={"evidence_id": ev_id, "observation": observation},
            )
        except Exception:
            update_job_state(DEFAULT_DB_PATH, job_id, "failed")
            raise HTTPException(
                status_code=500, detail="Offline probe execution failed"
            ) from None
    if job is None:
        raise HTTPException(status_code=500, detail="Job state unavailable")
    return JobResponse(
        id=job["id"], kind=job["kind"], state=job["state"],
        createdAt=job["created_at"], updatedAt=job["updated_at"],
        reservationUsd=job["reservation_usd"],
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
