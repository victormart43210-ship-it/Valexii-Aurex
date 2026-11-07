"""Diagnose XAELI → AUREX → private Qwen without printing secrets or inventing a model answer.

Run from a Railway service that can resolve the private hostname:

    AUREX_XAELI_STAGING_ENABLED=1 AUREX_XAELI_OPERATOR_APPROVED=1 \
    AUREX_QWEN_BASE_URL=http://qwen-private-staging.railway.internal:8080/v1 \
    AUREX_MODEL_API_KEY=... AUREX_SERVICE_TOKEN=... RAILWAY_ENVIRONMENT_ID=... \
    python tools/verify_xaeli_private_qwen.py

Exit 0 only when every required live check passed. This process is not that witness
when it is outside the Railway private network.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit

PRIVATE_HOST = "qwen-private-staging.railway.internal"
STAGING_HEALTH = "https://aurex-api-aurex-staging.up.railway.app/v1/health"
STAGING_EXPLAIN = "https://aurex-api-aurex-staging.up.railway.app/v1/xaeli-staging/explain"
REQUIRED = (
    "railway_aurex_current_contract",
    "private_qwen_dns",
    "aurex_to_qwen_authenticated",
    "qwen_generated_text",
    "xaeli_website_reaches_aurex",
    "xaeli_displays_generated_text",
    "unauthorized_rejected",
    "invalid_model_identity_rejected",
    "model_unavailable_explicit",
    "timeout_bounded",
    "tenant_isolation_preserved",
    "synthetic_end_to_end",
)


def assess(checks: dict[str, str]) -> dict[str, Any]:
    """checks values are pass, fail, or blocked. Missing checks are blocked."""
    ordered = {name: checks.get(name, "blocked") for name in REQUIRED}
    passed = sum(1 for value in ordered.values() if value == "pass")
    failed = any(value == "fail" for value in ordered.values())
    blocked = any(value == "blocked" for value in ordered.values())
    if all(value == "pass" for value in ordered.values()):
        state = "CONNECTED_VERIFIED"
    elif failed and passed:
        state = "PARTIALLY_CONNECTED"
    elif failed and blocked:
        state = "BLOCKED"
    elif failed:
        state = "FAILED"
    else:
        state = "BLOCKED"
    return {"state": state, "passed": passed, "required": len(REQUIRED), "checks": ordered}


def _get(url: str, timeout: float = 15) -> tuple[int, str]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(4000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(4000).decode("utf-8", "replace")


def _post(url: str, body: bytes, headers: dict[str, str], timeout: float = 15) -> tuple[int, str]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(4000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(4000).decode("utf-8", "replace")


def observe_here() -> dict[str, str]:
    """Live observations this process can make. No model call is invented."""
    checks = {name: "blocked" for name in REQUIRED}
    try:
        socket.getaddrinfo(PRIVATE_HOST, 8080)
        checks["private_qwen_dns"] = "pass"
    except socket.gaierror:
        checks["private_qwen_dns"] = "fail"
    try:
        status, body = _get(STAGING_HEALTH)
        current = '"readiness"' in body and '"process"' in body
        checks["railway_aurex_current_contract"] = "pass" if status == 200 and current else "fail"
    except (urllib.error.URLError, TimeoutError, OSError):
        checks["railway_aurex_current_contract"] = "fail"
    try:
        status, _body = _post(
            STAGING_EXPLAIN,
            b'{"prompt":"Explain a synthetic field ticket discrepancy."}',
            {"Content-Type": "application/json"},
        )
        checks["unauthorized_rejected"] = "pass" if status == 401 else "fail"
    except (urllib.error.URLError, TimeoutError, OSError):
        checks["unauthorized_rejected"] = "fail"
    flags = (
        os.environ.get("AUREX_XAELI_STAGING_ENABLED") == "1"
        and os.environ.get("AUREX_XAELI_OPERATOR_APPROVED") == "1"
        and bool(os.environ.get("AUREX_QWEN_BASE_URL"))
        and bool(os.environ.get("RAILWAY_ENVIRONMENT_ID"))
        and bool(os.environ.get("AUREX_MODEL_API_KEY"))
    )
    service = os.environ.get("AUREX_SERVICE_URL", "")
    host = urlsplit(service).hostname or ""
    if not flags or host in {"", "127.0.0.1", "localhost"}:
        for name in (
            "aurex_to_qwen_authenticated",
            "qwen_generated_text",
            "xaeli_website_reaches_aurex",
            "xaeli_displays_generated_text",
            "synthetic_end_to_end",
        ):
            checks[name] = "blocked"
    checks["invalid_model_identity_rejected"] = "blocked"
    checks["model_unavailable_explicit"] = "blocked"
    checks["timeout_bounded"] = "blocked"
    checks["tenant_isolation_preserved"] = "blocked"
    return checks


def main() -> int:
    report = assess(observe_here())
    report["paid_inference"] = "OFF"
    report["private_host"] = PRIVATE_HOST
    report["staging_health"] = STAGING_HEALTH
    report["secret_material"] = "omitted"
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report["state"] == "CONNECTED_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
