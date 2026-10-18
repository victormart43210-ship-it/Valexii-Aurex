"""Read-only AUREX development preview. Never expose backend writes or credentials."""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPHandler, HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse

PORTAL = Path(__file__).resolve().parents[1] / "dev" / "private-preview"
MAX_BYTES = 256 * 1024
ENDPOINTS = ("health", "capabilities", "evidence", "budgets", "jobs")
API_ROOT = "http://127.0.0.1:8766"

app = FastAPI(title="AUREX Private Development Preview", docs_url=None, redoc_url=None, openapi_url=None)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


OPENER = build_opener(HTTPHandler(), HTTPSHandler(), NoRedirect())


def _limited_get(url: str, *, headers: dict[str, str] | None = None) -> bytes:
    try:
        with OPENER.open(Request(url, headers=headers or {}, method="GET"), timeout=4) as resp:
            if resp.status != 200:
                raise ValueError("non-success HTTP status")
            data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError("response too large")
            return data
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ValueError("network or HTTP failure") from exc


def _b64url(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, binascii.Error) as exc:
        raise ValueError("invalid JWT encoding") from exc


def _team_domain() -> str:
    domain = os.environ.get("CF_ACCESS_TEAM_DOMAIN", "").lower().strip()
    if not domain.endswith(".cloudflareaccess.com") or "/" in domain or ":" in domain or domain.startswith("."):
        raise ValueError("Cloudflare Access team domain missing or invalid")
    return domain


@lru_cache(maxsize=8)
def _certs_cached(domain: str, bucket: int) -> dict[str, Any]:
    data = _limited_get(f"https://{domain}/cdn-cgi/access/certs")
    parsed = json.loads(data.decode("utf-8", errors="strict"))
    if not isinstance(parsed, dict) or not isinstance(parsed.get("keys"), list):
        raise ValueError("unusable Access JWKS")
    return parsed


def _verify_access_jwt(token: str) -> bool:
    audience = os.environ.get("CF_ACCESS_AUD", "")
    owner = os.environ.get("CF_ACCESS_OWNER_EMAIL", "").strip().lower()
    if not audience or not owner or "@" not in owner:
        return False
    try:
        domain = _team_domain()
        if len(token) > 12000:
            return False
        parts = token.split(".")
        if len(parts) != 3:
            return False
        header = json.loads(_b64url(parts[0]))
        claims = json.loads(_b64url(parts[1]))
        if not isinstance(header, dict) or not isinstance(claims, dict):
            return False
        if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
            return False
        jwks = _certs_cached(domain, int(time.time() // 900))
        key = next((k for k in jwks["keys"] if k.get("kid") == header["kid"] and k.get("kty") == "RSA"), None)
        if not key:
            return False
        n = int.from_bytes(_b64url(key["n"]), "big")
        e = int.from_bytes(_b64url(key["e"]), "big")
        pubkey = rsa.RSAPublicNumbers(e, n).public_key()
        pubkey.verify(_b64url(parts[2]), (parts[0] + "." + parts[1]).encode("ascii"), padding.PKCS1v15(), hashes.SHA256())
        now = int(time.time())
        audiences = claims.get("aud", [])
        if isinstance(audiences, str):
            audiences = [audiences]
        return bool(
            claims.get("iss", "").rstrip("/") == f"https://{domain}"
            and audience in audiences
            and isinstance(claims.get("exp"), int)
            and now < claims["exp"]
            and isinstance(claims.get("nbf", 0), int)
            and now >= claims.get("nbf", 0)
            and claims.get("email", "").lower() == owner
        )
    except Exception:  # noqa: BLE001
        # Fail closed: do not leak issuer details, key material, or auth diagnostics.
        return False


def _authorize(authorization: str | None = Header(default=None), cf_access_jwt_assertion: str | None = Header(default=None)) -> None:
    expected = os.environ.get("AUREX_PREVIEW_PASSWORD", "")
    if len(expected) < 32:
        raise HTTPException(503, detail="Private preview authentication not configured")
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(401, detail="Private preview authentication required", headers={"WWW-Authenticate": 'Basic realm="AUREX local development"'})
    try:
        decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
        username, password = decoded.split(":", 1)
    except (ValueError, UnicodeError, binascii.Error):
        raise HTTPException(401, detail="Invalid credentials") from None
    if not hmac.compare_digest(username, "aurex") or not hmac.compare_digest(password, expected):
        raise HTTPException(401, detail="Invalid credentials")
    mode = os.environ.get("AUREX_PREVIEW_MODE", "access")
    if mode == "local":
        # Only for loopback-bound bootstrap. NEVER attach Cloudflare Tunnel in local mode.
        return
    if mode != "access" or not cf_access_jwt_assertion or not _verify_access_jwt(cf_access_jwt_assertion):
        raise HTTPException(403, detail="Cloudflare Access verification required")


@app.middleware("http")
async def add_security_headers(request: Any, call_next: Any) -> Any:
    response = await call_next(request)
    response.headers.update({
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; form-action 'none'; frame-ancestors 'none'; base-uri 'none'",
    })
    return response


@app.get("/")
def index(_: None = Depends(_authorize)) -> FileResponse:
    return FileResponse(PORTAL / "index.html", media_type="text/html")


@app.get("/dashboard.js")
def frontend_js(_: None = Depends(_authorize)) -> FileResponse:
    return FileResponse(PORTAL / "dashboard.js", media_type="text/javascript")


@app.get("/dashboard.css")
def frontend_css(_: None = Depends(_authorize)) -> FileResponse:
    return FileResponse(PORTAL / "dashboard.css", media_type="text/css")


def _fetch_readonly(name: str) -> dict[str, Any]:
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32:
        return {"endpoint": name, "status": "HOLD", "reason": "backend token unavailable"}
    try:
        raw = _limited_get(f"{API_ROOT}/v1/{name}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
        value = json.loads(raw.decode("utf-8", errors="strict"))
        if not isinstance(value, dict):
            raise ValueError("wrong root schema")
        if name == "health":
            if value.get("status") != "ok" or not isinstance(value.get("version"), str):
                raise ValueError("invalid health")
            return {"endpoint": name, "status": "PASS", "version": value["version"]}
        if name == "budgets":
            if not all(isinstance(value.get(x), (int, float)) and not isinstance(value.get(x), bool) for x in ("limitUsd", "reservedUsd", "spentUsd")):
                raise ValueError("invalid budgets")
            return {"endpoint": name, "status": "PASS", "zeroDollarBudget": value["limitUsd"] == 0}
        field = {"capabilities": "capabilities", "evidence": "evidence", "jobs": "jobs"}[name]
        if not isinstance(value.get(field), list):
            raise ValueError("invalid result list")
        return {"endpoint": name, "status": "PASS", "count": len(value[field])}
    except (ValueError, UnicodeDecodeError):
        return {"endpoint": name, "status": "HOLD", "reason": "backend unavailable or response invalid"}


@app.get("/api/status")
def status(_: None = Depends(_authorize)) -> JSONResponse:
    records = [_fetch_readonly(name) for name in ENDPOINTS]
    return JSONResponse({
        "environment": "LOCAL DEVELOPMENT — NO PRODUCTION AUTHORITY",
        "mode": "read-only",
        "independentVerification": "NOT VERIFIED",
        "externalBudgetUsd": 0,
        "checks": records,
        "overall": "PASS" if all(r["status"] == "PASS" for r in records) else "HOLD",
    })
