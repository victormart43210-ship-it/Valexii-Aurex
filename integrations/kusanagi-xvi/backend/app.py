"""Read-only AUREX v1 bridge with governed financial job & document analysis support."""
import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime
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
from aurex.fenced_worker import cancel_job, claim_job, fail_job, finalize_job
from aurex.pipeline_receipts import read_pipeline_receipt
from aurex.real_offline_probe import execute_sqlite_roundtrip

try:
    from aurex.doc_intelligence import budget_snapshot, register_document_routes
except ImportError:
    from doc_intelligence import budget_snapshot, register_document_routes  # type: ignore[no-redef]

app = FastAPI(title="AUREX governed bridge", docs_url=None, redoc_url=None, openapi_url=None)
CAPABILITIES = ("regression_scan", "memory_graph", "evidence_vault", "model_benchmarking", "hypothesis_testing")


def authorize(authorization: str = Header(default="")):
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "service not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "unauthorized")
    supplied = authorization[7:].strip()
    if not hmac.compare_digest(supplied, token):
        raise HTTPException(401, "unauthorized")


class JobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(pattern=r"^(regression_scan|regression-scan|benchmark|hypothesis_test|synthetic_field_audit_v1)$")
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


@app.get("/v1/health", dependencies=[Depends(authorize)])
def health():
    return {"status": "ok", "version": "1.1.0-governed", "time": datetime.now(UTC).isoformat()}


@app.get("/v1/capabilities", dependencies=[Depends(authorize)])
def capabilities():
    ev_records = list_evidence(DEFAULT_DB_PATH)
    latest_ev = ev_records[0] if ev_records else None
    ev_id = latest_ev["id"] if latest_ev else None

    return {
        "capabilities": [
            {
                "id": "regression_scan",
                "available": os.environ.get("AUREX_ENABLE_OFFLINE_LAB") == "1",
                "evidenceId": ev_id,
                "verifiedAt": None,
            },
            {"id": "memory_graph", "available": False, "evidenceId": None, "verifiedAt": None},
            {"id": "evidence_vault", "available": False, "evidenceId": None, "verifiedAt": None},
            {"id": "model_benchmarking", "available": False, "evidenceId": None, "verifiedAt": None},
            {"id": "hypothesis_testing", "available": False, "evidenceId": None, "verifiedAt": None},
        ]
    }


@app.get("/v1/evidence", dependencies=[Depends(authorize)])
def evidence():
    raw_ev = list_evidence(DEFAULT_DB_PATH)
    items = [
        {
            "id": e["id"],
            "capabilityId": e["capability_id"],
            "kind": e["kind"],
            "collectedAt": e["collected_at"],
            "sha256": e["sha256"],
            "summary": e["summary"],
        }
        for e in raw_ev
    ]
    return {"evidence": items}


@app.get("/v1/budgets", dependencies=[Depends(authorize)])
def budgets():
    return budget_snapshot()


@app.get("/v1/jobs", response_model=JobListResponse, dependencies=[Depends(authorize)])
def jobs():
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


@app.post("/v1/jobs", response_model=JobResponse, dependencies=[Depends(authorize)])
def create_job_endpoint(
    req: JobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
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
    try:
        job = create_job(
            DEFAULT_DB_PATH,
            f"job-{secrets.token_hex(12)}",
            canonical_kind,
            req.params,
            idempotency_key=idempotency_key,
            reservation_usd=0.0,
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
                    DEFAULT_DB_PATH,
                    job_id,
                    worker_id,
                    str(claimed["lease_token"]),
                    int(claimed["lease_generation"]),
                    observation,
                    digest,
                    f"ev-{secrets.token_hex(12)}",
                )
            except Exception:
                try:
                    fail_job(
                        DEFAULT_DB_PATH,
                        job_id,
                        worker_id,
                        str(claimed["lease_token"]),
                        int(claimed["lease_generation"]),
                    )
                except Exception:
                    raise HTTPException(
                        status_code=503, detail="Job persistence unavailable; execution not verified"
                    ) from None
                raise HTTPException(status_code=503, detail="Probe not finalized; execution not verified") from None
        else:
            resolved_job = get_job(DEFAULT_DB_PATH, job_id)
    else:
        resolved_job = get_job(DEFAULT_DB_PATH, job_id)

    if resolved_job is None:
        raise HTTPException(status_code=500, detail="Job state unavailable")
    return JobResponse(
        id=resolved_job["id"],
        kind=resolved_job["kind"],
        state=resolved_job["state"],
        createdAt=resolved_job["created_at"],
        updatedAt=resolved_job["updated_at"],
        reservationUsd=resolved_job["reservation_usd"],
    )


@app.get("/v1/jobs/{job_id}", response_model=JobResponse, dependencies=[Depends(authorize)])
def get_job_endpoint(job_id: str) -> JobResponse:
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


@app.get("/v1/jobs/{job_id}/receipt", dependencies=[Depends(authorize)])
def get_job_receipt_endpoint(job_id: str) -> dict[str, Any]:
    try:
        receipt = read_pipeline_receipt(DEFAULT_DB_PATH, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    return receipt


@app.post("/v1/jobs/{job_id}/cancel", response_model=JobResponse, dependencies=[Depends(authorize)])
def cancel_job_endpoint(job_id: str) -> JobResponse:
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


register_document_routes(app, authorize)
