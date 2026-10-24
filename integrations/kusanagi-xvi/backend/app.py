"""AUREX authenticated read-only bridge with disabled-by-default document candidate route."""
import hmac
import os
from datetime import UTC, datetime

from doc_intelligence import budget_snapshot, register_document_routes
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(title="AUREX governed bridge", docs_url=None, redoc_url=None, openapi_url=None)
CAPABILITIES = ("memory-graph", "evidence-vault", "model-benchmarking", "hypothesis-testing", "computer-use")

def authorize(authorization: str = Header(default="")):
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "service not configured")
    if not hmac.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "unauthorized")

@app.get("/v1/health", dependencies=[Depends(authorize)])
def health():
    return {"status": "ok", "version": "1.1.0-docs-staged", "time": datetime.now(UTC).isoformat()}

@app.get("/v1/capabilities", dependencies=[Depends(authorize)])
def capabilities():
    # Capability != API route. No independent efficacy witness admitted.
    return {"capabilities": [{"id": x, "available": False, "evidenceId": None, "verifiedAt": None} for x in CAPABILITIES]}

@app.get("/v1/evidence", dependencies=[Depends(authorize)])
def evidence():
    return {"evidence": []}

@app.get("/v1/budgets", dependencies=[Depends(authorize)])
def budgets():
    # If explicitly enabled, reports only conservative daily estimated provider charges.
    return budget_snapshot()

@app.get("/v1/jobs", dependencies=[Depends(authorize)])
def jobs():
    return {"jobs": [], "nextCursor": None}

register_document_routes(app, authorize)
