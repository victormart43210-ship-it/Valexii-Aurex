"""Read-only AUREX v1 bridge. No AI inference, jobs, or computer use enabled."""
import hmac
import http.client
import json
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request

app = FastAPI(title="AUREX read-only bridge", docs_url=None, redoc_url=None, openapi_url=None)
CAPABILITIES = ("memory-graph", "evidence-vault", "model-benchmarking", "hypothesis-testing", "computer-use")

def authorize(authorization: str = Header(default="")):
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "service not configured")
    if not hmac.compare_digest(authorization.encode("utf-8"), ("Bearer " + token).encode("utf-8")):
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


# Fixed-fixture private inference; no customer prompts or financial authority.
QWEN_BASE = "http://qwen-private-staging.railway.internal:8080"
QWEN_RESPONSE_LIMIT = 32768
_qwen_slot = threading.Lock()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def qwen_configuration():
    if os.environ.get("AUREX_QWEN_STAGING_ENABLED") != "true":
        raise HTTPException(503, "QWEN_STAGING_DISABLED")
    if os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        raise HTTPException(503, "STAGING_ONLY")
    # Exact canonical URL rejects credentials, alternate ports, paths and encodings.
    if os.environ.get("AUREX_QWEN_BASE_URL") != QWEN_BASE:
        raise HTTPException(503, "INVALID_PRIVATE_QWEN_ENDPOINT")
    key = os.environ.get("AUREX_MODEL_API_KEY", "")
    if not key or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise HTTPException(503, "QWEN_AUTH_NOT_CONFIGURED")
    return key


def qwen_json(path, key, payload=None):
    # Never inherit HTTP(S)_PROXY, follow redirects, or retry a request.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(
        QWEN_BASE + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    try:
        with opener.open(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("status")
            raw = response.read(QWEN_RESPONSE_LIMIT + 1)
            if len(raw) > QWEN_RESPONSE_LIMIT:
                raise ValueError("size")
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ValueError("schema")
            return result
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, http.client.HTTPException, RecursionError):
        raise HTTPException(502, "QWEN_UPSTREAM_UNAVAILABLE") from None


def qwen_model_ids(key):
    result = qwen_json("/v1/models", key)
    items = result.get("data")
    if not isinstance(items, list) or not 1 <= len(items) <= 16:
        raise HTTPException(502, "INVALID_QWEN_MODELS")
    models = []
    for item in items:
        model = item.get("id") if isinstance(item, dict) else None
        if not isinstance(model, str) or not model or len(model) > 256:
            raise HTTPException(502, "INVALID_QWEN_MODELS")
        if any(ord(c) < 33 or ord(c) > 126 for c in model):
            raise HTTPException(502, "INVALID_QWEN_MODELS")
        models.append(model)
    return models


@app.get("/v1/staging/qwen/models", dependencies=[Depends(authorize)])
def qwen_models():
    return {"models": qwen_model_ids(qwen_configuration()), "authority": "NONE",
            "independentVerification": "NOT_VERIFIED", "release": "HOLD"}


@app.post("/v1/staging/qwen/synthetic-probe", dependencies=[Depends(authorize)])
async def qwen_synthetic_probe(request: Request):
    key = qwen_configuration()
    # Do not read an unbounded body, or accept caller-supplied prompts/options.
    if request.url.query:
        raise HTTPException(400, "SYNTHETIC_ONLY")
    async for chunk in request.stream():
        if chunk:
            raise HTTPException(400, "SYNTHETIC_ONLY")
    # Blocking I/O runs off the event loop; one inference in flight per process.
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(run_qwen_probe, key)


def run_qwen_probe(key):
    if not _qwen_slot.acquire(blocking=False):
        raise HTTPException(429, "QWEN_BUSY")
    try:
        model = os.environ.get("AUREX_QWEN_MODEL", "")
        if not model:
            raise HTTPException(503, "QWEN_MODEL_NOT_CONFIGURED")
        if model not in qwen_model_ids(key):
            raise HTTPException(503, "QWEN_MODEL_MISMATCH")
        started = time.monotonic()
        request_id = str(uuid4())
        data = qwen_json("/v1/chat/completions", key, {
            "model": model,
            "messages": [{"role": "system", "content": "Synthetic connectivity test only. No authority. Reply READY."},
                         {"role": "user", "content": "Synthetic test: respond READY."}],
            "max_tokens": 16, "temperature": 0, "stream": False,
        })
        try:
            answer = data["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip() or len(answer) > 256:
                raise ValueError("answer")
            if data.get("model") != model:
                raise ValueError("model")
        except (ValueError, KeyError, IndexError, TypeError):
            raise HTTPException(502, "INVALID_QWEN_RESPONSE") from None
        return {
            "schema": "aurex.synthetic.qwen_probe.v1", "synthetic": True,
            "modelResponded": True, "model": model, "answer": answer,
            "requestId": request_id, "timestamp": datetime.now(UTC).isoformat(),
            "latencyMs": round((time.monotonic() - started) * 1000),
            "authority": "NONE", "independentVerification": "NOT_VERIFIED", "release": "HOLD",
        }
    finally:
        _qwen_slot.release()
