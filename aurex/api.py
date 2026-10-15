"""Operational AUREX HTTP API conforming to VALEXII Website contracts."""

import hmac
import json
import math
import os
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from starlette.requests import Request

from aurex.database import (
    DEFAULT_DB_PATH,
    create_job,
    get_db,
    get_job,
    list_evidence,
    list_jobs,
    update_job_state,
)
from aurex.http_controls import HTTPControls
from aurex.request_limits import RequestLimits
from aurex.workflows.budget import BudgetGuard

app = FastAPI(
    title="VALEXII-AUREX",
    version="0.1.0a1",
    description="External evidence and challenge engine. AUREX never grants product authority.",
)

app.add_middleware(RequestLimits)
app.add_middleware(HTTPControls)

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


def credential_identities() -> dict[str, str]:
    identities = {"service": get_token()}
    try:
        configured = json.loads(os.environ.get("AUREX_USER_TOKENS", "{}"))
        if not isinstance(configured, dict) or len(configured) > 100:
            raise ValueError("Invalid identities")
        for owner, token in configured.items():
            if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", owner) or owner == "service":
                raise ValueError("Invalid identity")
            if not isinstance(token, str) or len(token) < 32 or token in identities.values():
                raise ValueError("Invalid credential")
            identities[owner] = token
    except (ValueError, TypeError) as exc:
        raise HTTPException(503, "Invalid authentication configuration") from exc
    return identities


def authenticate(authorization: str | None = Header(default=None)) -> str:
    identities = credential_identities()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or malformed Authorization header")
    supplied = authorization[7:].strip()
    matched = None
    for owner, token in identities.items():
        if hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8")):
            matched = owner
    if matched is None:
        raise HTTPException(401, "Invalid authorization credentials")
    return matched



class JobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(pattern=r"^(regression_scan|benchmark|hypothesis_test|local_inference)$")
    params: dict[str, Any] = Field(default_factory=dict)
    maxCostUsd: float = Field(default=0.0, ge=0.0, le=100.0, allow_inf_nan=False)

    @field_validator("params", mode="before")
    @classmethod
    def bounded_params(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict) or len(value) > 16:
            raise ValueError("params must contain at most 16 scalar values")
        for key, item in value.items():
            if not isinstance(key, str) or not re.fullmatch(r"[a-z_]{1,32}", key):
                raise ValueError("invalid parameter name")
            if type(item) not in (str, int, float, bool):
                raise ValueError("parameter values must be scalar")
            if isinstance(item, str) and len(item.encode("utf-8")) > 8192:
                raise ValueError("parameter string too long")
            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError("parameter must be finite")
        return value

    @model_validator(mode="after")
    def validate_kind_params(self) -> "JobCreateRequest":
        if self.kind == "local_inference":
            if set(self.params) != {"prompt"} or not isinstance(self.params["prompt"], str) or not self.params["prompt"].strip():
                raise ValueError("local_inference requires one nonempty prompt")
        elif any(isinstance(v, str) and len(v) > 256 for v in self.params.values()):
            raise ValueError("parameter string too long")
        return self


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
def health(_: str = Depends(authenticate)) -> dict[str, str]:
    return {
        "status": "ok",
        "version": "0.1.0a1",
        "time": datetime.now(UTC).isoformat(),
    }


@app.get("/v1/capabilities", response_model=CapabilitiesResponse)
def capabilities(_: str = Depends(authenticate)) -> CapabilitiesResponse:
    from aurex.database import worker_status
    local_available = False
    if os.environ.get("AUREX_EXECUTION_ENABLED") == "true":
        worker = worker_status(DEFAULT_DB_PATH)
        local_available = bool(worker.get("active") and worker.get("modelConfigured"))
    return CapabilitiesResponse(
        capabilities=[
            CapabilityItem(id="local-inference", available=local_available),
            CapabilityItem(
                id="regression-scan",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
            CapabilityItem(
                id="remote-inference",
                available=False,
                evidenceId=None,
                verifiedAt=None,
            ),
        ]
    )


@app.get("/v1/jobs", response_model=JobListResponse)
def get_jobs(owner: str = Depends(authenticate), cursor: str | None = Query(default=None, max_length=64)) -> JobListResponse:
    raw_jobs = list_jobs(DEFAULT_DB_PATH, owner_id=owner, before_id=cursor)
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
    return JobListResponse(jobs=res, nextCursor=raw_jobs[-1]["id"] if len(raw_jobs) == 200 else None)


@app.post("/v1/jobs", response_model=JobResponse)
def create_job_endpoint(
    req: JobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    owner: str = Depends(authenticate),
) -> JobResponse:
    if req.kind not in ("regression_scan", "local_inference"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job kind '{req.kind}' is currently unsupported or disabled",
        )

    if req.maxCostUsd > 0.0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Paid execution disabled; budget limit is $0.00",
        )

    if req.kind == "regression_scan":
        raise HTTPException(503, "Regression worker unavailable; no execution or evidence produced")
    if os.environ.get("AUREX_EXECUTION_ENABLED") != "true":
        raise HTTPException(503, "Local execution disabled")
    from aurex.database import worker_status
    if not all(worker_status(DEFAULT_DB_PATH).get(k) for k in ("active", "modelConfigured")):
        raise HTTPException(503, "Local worker unavailable")
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key required")
    try:
        job = create_job(DEFAULT_DB_PATH, "job-" + uuid.uuid4().hex, req.kind, req.params, idempotency_key, owner_id=owner)
    except ValueError as exc:
        raise HTTPException(409, "Invalid or conflicting idempotency request") from exc
    return _job_response(job)


def _job_response(j: dict[str, Any]) -> JobResponse:
    return JobResponse(id=j["id"], kind=j["kind"], state=j["state"], createdAt=j["created_at"], updatedAt=j["updated_at"], reservationUsd=j["reservation_usd"])


@app.get("/v1/jobs/{job_id}", response_model=JobResponse)
def get_job_endpoint(job_id: str, owner: str = Depends(authenticate)) -> JobResponse:
    j = get_job(DEFAULT_DB_PATH, job_id, owner_id=owner)
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
def cancel_job_endpoint(job_id: str, owner: str = Depends(authenticate)) -> JobResponse:
    j = get_job(DEFAULT_DB_PATH, job_id, owner_id=owner)
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    try:
        updated = update_job_state(DEFAULT_DB_PATH, job_id, "cancelled", owner_id=owner)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Job is already terminal") from exc
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
def get_evidence(owner: str = Depends(authenticate)) -> EvidenceListResponse:
    raw_ev = list_evidence(DEFAULT_DB_PATH, owner_id=owner)
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


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


def dependency_status() -> dict[str, str]:
    from aurex.database import worker_status
    checks = {"database": "FAIL", "worker": "NOT VERIFIED", "model": "NOT VERIFIED", "configuration": "FAIL"}
    try:
        credential_identities()
        checks["configuration"] = "PASS"
    except HTTPException:
        pass
    try:
        with closing(get_db(DEFAULT_DB_PATH)) as conn:
            conn.execute("SELECT 1").fetchone()
        checks["database"] = "PASS"
        worker = worker_status(DEFAULT_DB_PATH)
        checks["worker"] = "PASS" if worker.get("active") and worker.get("modelConfigured") else "NOT VERIFIED"
    except (sqlite3.Error, ValueError, OSError):
        pass
    return checks


@app.get("/health/ready")
def ready() -> dict[str, str]:
    checks = dependency_status()
    if os.environ.get("AUREX_EXECUTION_ENABLED") != "true" or any(checks[k] != "PASS" for k in ("database", "configuration", "worker")):
        raise HTTPException(503, "Execution dependencies unavailable")
    return {"status": "ready", "model": "NOT VERIFIED"}


@app.get("/health/dependencies")
def dependencies(owner: str = Depends(authenticate)) -> dict[str, str]:
    if owner != "service":
        raise HTTPException(403, "Owner diagnostics required")
    return dependency_status()


@app.get("/v1/jobs/{job_id}/result")
def job_result(job_id: str, owner: str = Depends(authenticate)) -> dict[str, Any]:
    from aurex.database import job_evidence
    try:
        job = get_job(DEFAULT_DB_PATH, job_id, owner_id=owner)
    except (ValueError, TypeError) as exc:
        raise HTTPException(409, "Stored result integrity check failed") from exc
    if job is None:
        raise HTTPException(404, "Job not found")
    result = None
    if job["state"] == "succeeded":
        evidence = job_evidence(DEFAULT_DB_PATH, job_id, owner_id=owner)
        if not evidence or any(r["integrity"] != "PASS" for r in evidence):
            raise HTTPException(409, "Stored result integrity check failed")
        raw = job.get("result")
        if not isinstance(raw, dict) or any(not isinstance(raw.get(k), str) for k in ("text", "model", "provider")):
            raise HTTPException(409, "Stored result schema check failed")
        result = {k: raw[k] for k in ("text", "model", "provider")}
        result.update({"verification": "NOT VERIFIED", "authorityGranted": False})
    return {"jobId": job_id, "state": job["state"], "result": result, "verification": "NOT VERIFIED"}



@app.get("/v1/jobs/{job_id}/evidence")
def evidence_for_job(job_id: str, owner: str = Depends(authenticate)) -> dict[str, Any]:
    from aurex.database import job_evidence
    if get_job(DEFAULT_DB_PATH, job_id, owner_id=owner) is None:
        raise HTTPException(404, "Job not found")
    records = job_evidence(DEFAULT_DB_PATH, job_id, owner_id=owner)
    return {"evidence": [{"id": r["id"], "capabilityId": r["capability_id"], "kind": r["kind"], "collectedAt": r["collected_at"], "sha256": r["sha256"], "summary": r["summary"], "verification": "NOT VERIFIED", "integrity": r.get("integrity", "NOT VERIFIED"), "authorityGranted": False} for r in records]}


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Pydantic's default includes the complete input, including private prompts.
    return JSONResponse({"detail": "Invalid request payload"}, status_code=422)


@app.exception_handler(sqlite3.Error)
async def database_error(_: Request, exc: sqlite3.Error) -> JSONResponse:
    return JSONResponse({"detail": "Storage unavailable"}, status_code=503)


class AnalyticsEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event: str = Field(pattern=r"^(page_view|navigation)$")
    route: str = Field(default="/", max_length=2048)
    device: str = Field(default="unknown", pattern=r"^(unknown|mobile|tablet|desktop)$")


@app.post("/v1/analytics/events", status_code=202)
def analytics_event(event: AnalyticsEvent, owner: str = Depends(authenticate)) -> dict[str, str]:
    from aurex.analytics import record_event, retention
    if owner != "service":
        raise HTTPException(403, "Owner collector required")
    try:
        retention(DEFAULT_DB_PATH)
        event_id = record_event(DEFAULT_DB_PATH, event.event, event.route, event.device)
    except ValueError as exc:
        raise HTTPException(422, "Invalid analytics dimensions") from exc
    return {"id": event_id}


@app.get("/v1/analytics")
def analytics_summary(owner: str = Depends(authenticate)) -> dict[str, Any]:
    from aurex.analytics import retention, summary
    if owner != "service":
        raise HTTPException(403, "Owner dashboard required")
    retention(DEFAULT_DB_PATH)
    counts = summary(DEFAULT_DB_PATH)
    # Job metrics come from durable state, not browser-submitted operational events.
    with closing(get_db(DEFAULT_DB_PATH)) as conn:
        job_counts = {r[0]: r[1] for r in conn.execute("SELECT state, COUNT(*) FROM jobs GROUP BY state")}
    return {"counts": counts, "measurement": "event_counts", "uniqueVisitors": None, "jobsByState": job_counts}
