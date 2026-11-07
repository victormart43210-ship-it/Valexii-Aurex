"""Opt-in, bearer-protected read-only research-advice transport.

This endpoint requires inclusion by the existing AUREX API with authenticate
and AUREX_ENABLE_RESEARCH_ADVICE=1. It never modifies jobs, executes a command,
reviews its own evidence, or accesses privileged historic case stores.
Caller-supplied suggestions and probability estimates remain unverified.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

from .information_gain import Probe
from .optimization import FixStep
from .retrieval import Incident
from .spine import advise

router = APIRouter(tags=["research-advisory"])

_KEY = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$"
_MONEY = r"^(0|[1-9][0-9]*)(\.[0-9]{1,2})?$"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IncidentInput(_Strict):
    case_id: str = Field(pattern=_KEY)
    description: str = Field(min_length=1, max_length=4096)
    remedy_id: str = Field(pattern=_KEY)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    lineage_group: str = Field(pattern=_KEY)


class FixInput(_Strict):
    key: str = Field(pattern=_KEY)
    problem_code: str = Field(pattern=_KEY)
    lineage_group: str = Field(pattern=_KEY)
    fix: list[str] = Field(min_length=1, max_length=6)
    verify: list[str] = Field(min_length=1, max_length=6)
    rollback: list[str] = Field(min_length=1, max_length=6)
    minutes: int = Field(ge=1, le=3600)
    risk: int = Field(ge=0, le=5)
    cost_usd: str = Field(pattern=_MONEY)
    impact: float = Field(ge=0, le=100, allow_inf_nan=False)
    requires: list[str] = Field(default_factory=list, max_length=4)
    conflicts: list[str] = Field(default_factory=list, max_length=4)
    reversible: bool = True


class ProbeInput(_Strict):
    probe_id: str = Field(pattern=_KEY)
    sensitivity: float = Field(ge=0, le=1, allow_inf_nan=False)
    specificity: float = Field(ge=0, le=1, allow_inf_nan=False)
    duration_seconds: int = Field(ge=0, le=3600)
    risk: int = Field(ge=0, le=5)
    cost_usd: str = Field(pattern=_MONEY)
    # Don't accept 'calibration_reviewed' claims through HTTP. Until a real
    # trusted signed-calibration adapter exists, all probes are uncalibrated.


class AdviceInput(_Strict):
    problem_code: str = Field(pattern=_KEY)
    description: str = Field(min_length=1, max_length=512)
    incidents: list[IncidentInput] = Field(default_factory=list, max_length=40)
    fixes: list[FixInput] = Field(default_factory=list, max_length=12)
    probes: list[ProbeInput] = Field(default_factory=list, max_length=20)
    prior: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)


@router.post("/v1/research/advice")
def research_advice(req: AdviceInput) -> dict[str, Any]:
    if os.environ.get("AUREX_ENABLE_RESEARCH_ADVICE") != "1":
        raise HTTPException(status_code=503, detail="Research advisory disabled")
    if any(
        not all(isinstance(x, str) and 0 < len(x) <= 256 for x in f.fix + f.verify + f.rollback)
        for f in req.fixes
    ):
        raise HTTPException(status_code=422, detail="Invalid remediation instructions")
    cases = [
        Incident(
            r.case_id, r.description, r.remedy_id, r.evidence_sha256, r.lineage_group
        )
        for r in req.incidents
    ]
    steps = [
        FixStep(
            f.key, f.problem_code, f.lineage_group,
            tuple(f.fix), tuple(f.verify), tuple(f.rollback),
            f.minutes, f.risk, Decimal(f.cost_usd), f.impact,
            tuple(f.requires), tuple(f.conflicts), f.reversible,
        )
        for f in req.fixes
    ]
    tests = [
        Probe(
            p.probe_id, p.sensitivity, p.specificity,
            p.duration_seconds, p.risk, Decimal(p.cost_usd),
            calibration_reviewed=False,
        )
        for p in req.probes
    ]
    try:
        result = advise(
            req.problem_code, req.description, incidents=cases,
            fixes=steps, probes=tests, prior=req.prior,
        )
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid advisory candidate graph") from None
    return {
        "schema_version": 1,
        "status": result.gate,
        "independent_verification": "NOT VERIFIED",
        "authority": "NONE",
        "output": jsonable_encoder(asdict(result), custom_encoder={Decimal: str}),
    }
