"""NON-DEPLOYED reference AUREX service (dev only). Requires `pip install fastapi uvicorn`.

Implements only /v1/health and /v1/capabilities. No job execution, no shell, no
arbitrary code, no paid providers. Every capability reports available=false
until real evidence exists. Run locally: AUREX_SERVICE_TOKEN=... uvicorn app:app
"""
import hmac
import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(title="AUREX reference (dev only)", version="1.0.0-draft", docs_url=None, redoc_url=None)

KNOWN_CAPABILITIES = ["memory-graph", "evidence-vault", "model-benchmarking", "hypothesis-testing"]


def require_token(authorization: str = Header(default="")) -> None:
    expected = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(expected) < 16:
        raise HTTPException(status_code=503, detail="not configured")
    if not hmac.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/v1/health")
def health(_: None = Depends(require_token)):
    # break long mapping into multiple lines to satisfy linters
    return {
        "status": "ok",
        "version": "1.0.0-draft",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/capabilities")
def capabilities(_: None = Depends(require_token)):
    return {
        "capabilities": [
            {"id": c, "available": False, "evidenceId": None, "verifiedAt": None}
            for c in KNOWN_CAPABILITIES
        ]
    }
