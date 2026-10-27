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


# Owner-only, synthetic-only Qwen connectivity probe. Never accepts user/customer prompts.
# Deliberately separate from production inference and all financial/security authority.
@app.post("/v1/staging/qwen/synthetic-probe", dependencies=[Depends(authorize)])
def qwen_synthetic_probe():
    import json
    import urllib.error
    import urllib.request
    from urllib.parse import urlsplit

    if os.environ.get("AUREX_QWEN_STAGING_ENABLED") != "true":
        raise HTTPException(503, "QWEN_STAGING_DISABLED")
    if os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        raise HTTPException(503, "STAGING_ONLY")

    base = os.environ.get("AUREX_QWEN_BASE_URL", "").rstrip("/")
    parsed = urlsplit(base)
    host = parsed.hostname or ""
    # Railway's internal DNS only; never forward to a user-supplied URL.
    if parsed.scheme != "http" or not host.endswith(".railway.internal") or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
        raise HTTPException(503, "INVALID_PRIVATE_QWEN_ENDPOINT")
    if parsed.port != 8080:
        raise HTTPException(503, "INVALID_QWEN_PORT")

    payload = json.dumps({
        "model": os.environ.get("AUREX_QWEN_MODEL", "qwen"),
        "messages": [
            {"role": "system", "content": "Synthetic connectivity test only. No authority. Reply with the single word READY."},
            {"role": "user", "content": "Synthetic test: respond READY."},
        ],
        "max_tokens": 16,
        "temperature": 0,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        base + "/v1/chat/completions", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                raise HTTPException(502, "QWEN_UPSTREAM_FAILURE")
            data = json.loads(response.read(32768))
        answer = data["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("empty response")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        raise HTTPException(502, "QWEN_UPSTREAM_UNAVAILABLE") from None

    return {
        "schema": "aurex.synthetic.qwen_probe.v1",
        "synthetic": True, "modelResponded": True,
        "answer": answer[:256], "authority": "NONE",
        "independentVerification": "NOT_VERIFIED", "release": "HOLD",
    }
