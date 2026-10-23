"""Explicit CXXXII synthetic runtime; never migrates legacy evidence implicitly."""
from __future__ import annotations

import hmac
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def validate_environment(env: dict[str, str]) -> str:
    if env.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
        raise ValueError("Canonical activation is staging-only")
    if env.get("AUREX_JOB_EXECUTION_MODE") != "queued":
        raise ValueError("Detached worker required")
    for flag in ("AUREX_LLM_ENABLED", "AUREX_LLM_ALLOW_BILLING", "AUREX_OBSERVER_ENABLED"):
        if env.get(flag, "false") not in ("false", "0"):
            raise ValueError("Optional providers and observer must remain disabled")
    if env.get("AUREX_ENABLE_OFFLINE_LAB") != "1":
        raise ValueError("Canonical worker requires explicit enablement")
    if len(env.get("AUREX_SERVICE_TOKEN", "")) < 32 or env.get("AUREX_ADMIN_TOKEN"):
        raise ValueError("One staging service token required")
    path = env.get("AUREX_DB_PATH", "")
    if not Path(path).is_absolute() or path == "/data/aurex.sqlite3":
        raise ValueError("Dedicated canonical synthetic database required")
    if env.get("RAILWAY_PROJECT_ID") and path != "/data/aurex-cxxxii-synthetic.sqlite3":
        raise ValueError("Hosted canonical database path must be fixed")
    return path


def initialize_canonical(path: str) -> None:
    """Reject incompatible existing storage before canonical initialization writes."""
    target = Path(path)
    if target.is_symlink():
        raise ValueError("Database symlink refused")
    if target.exists():
        with sqlite3.connect(f"file:{target}?mode=ro", uri=True) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "evidence" in tables:
                raise ValueError("Legacy evidence schema requires explicit migration; HOLD")
            if "jobs" in tables:
                columns = {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}
                if "params_json" not in columns or "params" in columns:
                    raise ValueError("Legacy jobs schema refused; HOLD")
    from aurex.database import get_db
    conn = get_db(path)
    conn.close()
    target.chmod(0o600)


def create_app() -> FastAPI:
    from aurex import api
    from aurex.database import DEFAULT_DB_PATH

    path = validate_environment(dict(os.environ))
    if DEFAULT_DB_PATH != path:
        raise ValueError("API database configuration mismatch")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):  # type: ignore[no-untyped-def]
        initialize_canonical(path)
        yield

    app = FastAPI(title="AUREX canonical synthetic staging", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.router.routes.extend(api.app.router.routes)
    # Avoid exposing canonical auto-generated docs under the wrapper.
    app.router.routes[:] = [r for r in app.router.routes
                           if getattr(r, "path", "").startswith(("/v1/", "/health"))]

    @app.middleware("http")
    async def boundary(request: Request, call_next: Any) -> Any:
        expected = "Bearer " + os.environ["AUREX_SERVICE_TOKEN"]
        if not hmac.compare_digest(request.headers.get("authorization", ""), expected):
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/v1/agent/status")
    def agent_status() -> dict[str, Any]:
        return {"chatConfigured": False, "providerConnection": "NOT_VERIFIED",
                "mode": "OWNER_ONLY_STAGING", "authority": "NONE", "release": "HOLD"}

    @app.post("/v1/agent/ask")
    def agent_ask() -> JSONResponse:
        return JSONResponse({"detail": "LLM disabled; HOLD"}, status_code=503)

    return app
