"""Standalone authenticated, read-only AUREX workflow bridge.

Run from repository root: uvicorn xxv_website_bridge.backend:app --host 127.0.0.1 --port 8765
Never expose to the public without a secure gateway and persistent database configuration.
"""
import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse

from aurex_workflows.read_model import WorkflowReadModel

app = FastAPI(title="AUREX XXV read-only preview", docs_url=None, redoc_url=None, openapi_url=None)


def authenticate(authorization: str | None = Header(default=None)) -> None:
    secret = os.environ.get("AUREX_READ_TOKEN", "")
    if not secret or len(secret) < 24:
        raise HTTPException(status_code=503, detail="Read access not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})
    supplied = authorization.removeprefix("Bearer ")
    if not hmac.compare_digest(supplied.encode(), secret.encode()):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})


def reader() -> WorkflowReadModel:
    location = os.environ.get("AUREX_WORKFLOW_DB", "")
    if not location or not Path(location).is_file():
        raise HTTPException(status_code=503, detail="Workflow database unavailable")
    return WorkflowReadModel(location)


@app.get("/v1/health", dependencies=[Depends(authenticate)])
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "read-only", "authority": "none"}


@app.get("/v1/capabilities", dependencies=[Depends(authenticate)])
def capabilities() -> dict[str, object]:
    return {"jobs_read": True, "approval": False, "execution": False, "spend_usd": 0.0}


@app.get("/v1/jobs", dependencies=[Depends(authenticate)])
def jobs(limit: int = Query(default=20, ge=1, le=100), cursor: str | None = None) -> dict[str, object]:
    try:
        return reader().list_jobs(limit=limit, cursor=cursor)
    except (FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail="Workflow read unavailable") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid pagination cursor") from exc


@app.get("/")
def home() -> FileResponse:
    return FileResponse(Path(__file__).parent / "website" / "index.html", headers={
        "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        "Cache-Control": "no-store",
    })


@app.get("/app.js")
def script() -> FileResponse:
    return FileResponse(Path(__file__).parent / "website" / "app.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})


@app.get("/app.css")
def style() -> FileResponse:
    return FileResponse(Path(__file__).parent / "website" / "app.css", media_type="text/css", headers={"Cache-Control": "no-store"})
