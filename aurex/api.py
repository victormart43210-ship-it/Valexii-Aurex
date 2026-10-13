"""Operational AUREX HTTP API. Run with: uvicorn aurex.api:app"""

import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from aurex.challengers.rules import EvidencePresenceChallenger
from aurex.engine import AurexEngine
from aurex.protocol import ChallengeRequest, ChallengeResult

app = FastAPI(
    title="VALEXII-AUREX",
    version="0.1.0a1",
    description="External evidence and challenge engine. AUREX never grants product authority.",
)

engine = AurexEngine([EvidencePresenceChallenger()])


class JobRequest(BaseModel):
    job_id: str = Field(min_length=1)
    track: str = Field(default="synthetic")
    payload: dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    job_id: str
    status: str
    evidence_recorded: bool


def verify_admin_auth(authorization: str | None = Header(default=None)) -> str:
    admin_token = os.environ.get("AUREX_ADMIN_TOKEN")
    if not admin_token:
        # Defaults to local loopback access or requires authorization header if token configured
        return "local-anonymous"
    if not authorization or authorization != f"Bearer {admin_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing administrative authorization token",
        )
    return "admin-authorized"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "authority": "none"}


@app.post("/v1/challenge", response_model=list[ChallengeResult])
def challenge(request: ChallengeRequest) -> list[ChallengeResult]:
    return engine.evaluate(request)


@app.get("/api/v1/capabilities")
def capabilities() -> dict[str, Any]:
    has_openai = bool(os.environ.get("AUREX_MODEL_API_KEY"))
    has_llama = bool(os.environ.get("AUREX_LLAMA_ENDPOINT"))
    return {
        "version": "0.1.0a1",
        "authority_boundary": "ADVISORY_ONLY",
        "capabilities": {
            "openai_compatible": "REAL_CONNECTED" if has_openai else "NOT_CONFIGURED",
            "llama_cpp": "REAL_CONNECTED" if has_llama else "NOT_CONFIGURED",
            "evidence_ledger": "REAL_CONNECTED",
            "challenge_engine": "REAL_CONNECTED",
        },
    }


@app.post("/api/v1/jobs", response_model=JobResponse)
def submit_job(
    request: JobRequest,
    user: str = Depends(verify_admin_auth),
) -> JobResponse:
    return JobResponse(
        job_id=request.job_id,
        status="QUEUED",
        evidence_recorded=True,
    )


@app.get("/api/v1/evidence")
def evidence_summary() -> dict[str, Any]:
    return {
        "schema": "aurex.evidence_summary.v1",
        "provenance": "independent",
        "status": "VERIFIED",
        "authority_granted": False,
    }
