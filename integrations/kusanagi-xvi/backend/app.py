"""Read-only AUREX v1 bridge. No AI inference, jobs, or computer use enabled."""
import hmac
import os
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(title="AUREX read-only bridge", docs_url=None, redoc_url=None, openapi_url=None)
CAPABILITIES = ("memory-graph", "evidence-vault", "model-benchmarking", "hypothesis-testing", "computer-use")

def authorize(authorization: str = Header(default="")):
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "service not configured")
    if not hmac.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "unauthorized")

@app.get("/v1/health", dependencies=[Depends(authorize)])
def health():
    return {"status": "ok", "version": "1.0.0-readonly", "time": datetime.now(UTC).isoformat()}

@app.get("/v1/capabilities", dependencies=[Depends(authorize)])
def capabilities():
    return {"capabilities": [{"id": x, "available": False, "evidenceId": None, "verifiedAt": None} for x in CAPABILITIES]}

@app.get("/v1/evidence", dependencies=[Depends(authorize)])
def evidence():
    return {"evidence": []}

@app.get("/v1/budgets", dependencies=[Depends(authorize)])
def budgets():
    return {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": "month"}

@app.get("/v1/jobs", dependencies=[Depends(authorize)])
def jobs():
    return {"jobs": [], "nextCursor": None}

# Public synthetic industrial audit: deterministic, read-only, no customer data.
# Health does not imply audit authorization, verification, or deployment readiness.
SYNTHETIC_CHARGES = (
    ("heavy_recovery", 1, 2500),
    ("wrecker_hours", 3, 300),
    ("scene_support_hours", 3, 150),
)

@app.get("/v1/demo/industrial-audit")
def industrial_audit_demo():
    """Return a fictional towing exception for UI integration testing only."""
    charges = [
        {"code": code, "quantity": quantity, "unitPriceUsd": unit_price,
         "amountUsd": quantity * unit_price}
        for code, quantity, unit_price in SYNTHETIC_CHARGES
    ]
    candidate_total = sum(item["amountUsd"] for item in charges)
    return {
        "schemaVersion": "1.0",
        "demoId": "synthetic-towing-heavy-recovery-001",
        "industry": "towing_and_recovery",
        "synthetic": True,
        "dataClassification": "FICTIONAL",
        "sourceVerified": False,
        "independentVerification": "NOT_VERIFIED",
        "auditRuntimeConnected": False,
        "authority": "NONE",
        "release": "HOLD",
        "finding": {
            "kind": "POTENTIAL_UNBILLED_SERVICES",
            "status": "REVIEW_REQUIRED",
            "candidateAmountUsd": candidate_total,
            "confirmedRevenueUsd": 0,
            "charges": charges,
            "explanation": "Illustrative missing-invoice candidate; no real billing records checked.",
        },
        "gates": [
            {"stage": stage, "status": "DEMONSTRATION_ONLY"}
            for stage in ("EVIDENCE", "QUALIFICATION", "REALITY", "AUTHORITY", "EFFECT")
        ],
        "permittedEffects": [],
    }
