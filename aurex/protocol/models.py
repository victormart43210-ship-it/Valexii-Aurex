"""Canonical public AUREX protocol models."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ChallengeStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    CONTESTED = "CONTESTED"
    INSUFFICIENT = "INSUFFICIENT"
    STALE = "STALE"
    HOLD = "HOLD"


class EvidenceRef(BaseModel):
    evidence_id: str
    source: str
    observed_at: datetime
    sha256: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChallengeRequest(BaseModel):
    request_id: str
    claim: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ChallengeResult(BaseModel):
    request_id: str
    status: ChallengeStatus
    rationale: str
    evidence_used: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    authority_granted: bool = False
