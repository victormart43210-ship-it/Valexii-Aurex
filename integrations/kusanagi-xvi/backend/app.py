"""AUREX v1 transport/API; strictly bounded offline-only worker, no inference."""
from __future__ import annotations

import hmac
import os
import re
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

try:
    from . import agent, llm, store
except ImportError:
    import agent  # type: ignore[no-redef]
    import llm  # type: ignore[no-redef]
    import store  # type: ignore[no-redef]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    store.initialize(store.path_from_env())
    yield

app = FastAPI(title="AUREX v1 bounded offline API", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
IDS = ("memory-graph","evidence-vault","model-benchmarking","hypothesis-testing","computer-use","regression_scan")
JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
KEY = re.compile(r"^[A-Za-z0-9_-]{16,128}$")

class JobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["regression_scan"]
    params: dict[str, str]
    maxCostUsd: float = Field(ge=0, le=0)


def offline_enabled() -> bool:
    return os.environ.get("AUREX_ENABLE_OFFLINE_LAB", "").lower() == "true"


def authorize(authorization: Annotated[str, Header()] = "") -> None:
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "service not configured")
    if not hmac.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "unauthorized")


@app.middleware("http")
async def no_store(request: Request, call_next):
    res = await call_next(request)
    res.headers["Cache-Control"] = "no-store"
    res.headers["X-Content-Type-Options"] = "nosniff"
    return res


@app.get("/v1/health", dependencies=[Depends(authorize)])
def health():
    return {"status":"ok", "version":"1.1.0-sqlite-offline", "time":datetime.now(UTC).isoformat()}


@app.get("/v1/capabilities", dependencies=[Depends(authorize)])
def capabilities():
    online = offline_enabled() and store.worker_recent(store.path_from_env())
    return {"capabilities":[{"id":cid,"available":cid == "regression_scan" and online,
                             "evidenceId":None,"verifiedAt":None} for cid in IDS]}


@app.get("/v1/evidence", dependencies=[Depends(authorize)])
def evidence():
    return {"evidence":store.evidence(store.path_from_env())}


@app.get("/v1/budgets", dependencies=[Depends(authorize)])
def budgets():
    return {"limitUsd":0,"reservedUsd":0,"spentUsd":0,"period":"month"}


@app.get("/v1/agent/status", dependencies=[Depends(authorize)])
def agent_status():
    return {
        **agent.snapshot(store.path_from_env()),
        "chatConfigured": llm.configured(),
        "modelProvider": llm.status()["provider"],
        "modelName": llm.status()["model"],
        "providerConnection": "NOT_VERIFIED",
        "mode": "OWNER_ONLY_STAGING",
    }


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=1000)


@app.post("/v1/agent/ask", dependencies=[Depends(authorize)])
def agent_ask(request: AskRequest):
    # Never enable paid inference without TWO explicit flags, provider secret,
    # and an atomic per-service SQLite request quota. Owner session is enforced
    # in website server code, NOT by this shared service bearer alone.
    if not llm.configured():
        raise HTTPException(503, "LLM disabled; HOLD")
    if not store.reserve_llm_call(store.path_from_env()):
        raise HTTPException(429, "LLM request quota exhausted; HOLD")
    try:
        return llm.answer(request.question)
    except ValueError:
        raise HTTPException(422, "invalid question") from None
    except llm.AgentUnavailable:
        raise HTTPException(503, "LLM unavailable; HOLD") from None


@app.get("/v1/jobs", dependencies=[Depends(authorize)])
def jobs():
    return {"jobs":store.list_jobs(store.path_from_env()),"nextCursor":None}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(authorize)])
def job_status(job_id: str):
    if not JOB_ID.fullmatch(job_id):
        raise HTTPException(422,"invalid id")
    result=store.get_job(store.path_from_env(),job_id)
    if not result:
        raise HTTPException(404,"job not found")
    return result


@app.get("/v1/jobs/{job_id}/receipt", dependencies=[Depends(authorize)])
def job_receipt(job_id: str):
    """Authenticated integrity-bound SQLite observation, never an audit verdict."""
    if not JOB_ID.fullmatch(job_id):
        raise HTTPException(422, "invalid id")
    try:
        value = store.read_receipt(store.path_from_env(), job_id)
    except ValueError:
        raise HTTPException(409, "receipt unavailable or integrity invalid") from None
    if value is None:
        raise HTTPException(404, "job not found")
    return value


@app.post("/v1/jobs", dependencies=[Depends(authorize)])
def submit(job: JobRequest, idempotency_key: Annotated[str, Header()] = ""):
    if not offline_enabled() or not store.worker_recent(store.path_from_env()):
        raise HTTPException(503, "offline worker unavailable; HOLD")
    if not KEY.fullmatch(idempotency_key):
        raise HTTPException(422,"invalid idempotency key")
    if job.params != {"probe":"sqlite_roundtrip_v1"}:
        raise HTTPException(422,"only the bounded offline SQLite probe is admitted")
    try:
        return store.create_job(store.path_from_env(),job.kind,job.params,idempotency_key)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/v1/jobs/{job_id}/cancel", dependencies=[Depends(authorize)])
def cancel_job(job_id: str, idempotency_key: Annotated[str, Header()] = ""):
    if not JOB_ID.fullmatch(job_id) or not KEY.fullmatch(idempotency_key):
        raise HTTPException(422,"invalid id or key")
    if not offline_enabled():
        raise HTTPException(503,"offline worker disabled")
    result=store.cancel(store.path_from_env(),job_id)
    if not result:
        raise HTTPException(409,"job already terminal or not found")
    return result
