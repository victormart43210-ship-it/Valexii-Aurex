"""Feature-disabled-by-default research API, attach under existing bearer auth.
This endpoint performs no model calls and grants no security authority.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

try:
    from . import evidence_science
except ImportError:
    import evidence_science  # type: ignore[no-redef]

router = APIRouter()

class EvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sourceId: str = Field(min_length=1, max_length=64)
    family: str = Field(min_length=1, max_length=64)
    stance: Literal["SUPPORT", "CONTRADICT"]
    capturedAt: datetime
    sha256: str = Field(min_length=64, max_length=64)

class AssessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claimId: str = Field(min_length=1, max_length=64)
    evidence: list[EvidenceRequest] = Field(max_length=16)

@router.post("/v1/research/assess")
def assess(body: AssessRequest):
    if os.environ.get("AUREX_RESEARCH_LAB_ENABLED") != "true" or os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        raise HTTPException(503, "research lab disabled; HOLD")
    payload = body.model_dump(mode="json")
    try:
        return evidence_science.assess_claim(payload)
    except ValueError:
        raise HTTPException(422, "invalid evidence metadata; HOLD") from None
