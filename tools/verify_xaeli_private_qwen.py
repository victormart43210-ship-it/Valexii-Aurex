"""Live XAELI → AUREX → private Qwen checks. No secret values are printed.

Exit 0 only when all 12 live checks pass. A local unit test is not a live pass.
From outside Railway, private DNS and authenticated inference stay fail or blocked.

Qwen authentication, confirmed from llama.cpp server documentation, is not enabled
by an AUREX flag. The server enforces a key only when LLAMA_API_KEY or
LLAMA_ARG_API_KEY_FILE is set. Clients send Authorization: Bearer. The key file
keeps the secret out of the process command. AUREX reads the same secret from
AUREX_MODEL_API_KEY and will not call the private host unless
AUREX_RAILWAY_PRIVATE_QWEN_ENABLED=1 and RAILWAY_ENVIRONMENT_ID are set.
The served model id must be aliased to qwen2.5-0.5b-instruct-q4_k_m
(LLAMA_ARG_ALIAS) or identity validation fails closed.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
from typing import Any

PRIVATE_HOST = "qwen-private-staging.railway.internal"
STAGING_ORIGIN = "https://aurex-api-aurex-staging.up.railway.app"
STAGING_HEALTH = STAGING_ORIGIN + "/v1/health"
STAGING_EXPLAIN = STAGING_ORIGIN + "/v1/xaeli-staging/explain"
WEBSITE = "https://valexii.com/xaeli"
EXPECTED_MODEL = "qwen2.5-0.5b-instruct-q4_k_m"
SOURCE_REVISION = os.environ.get("SOURCE_REVISION", "fc2bed4dd98054503254ad1a4c11fbecd7b0deca")
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
CONTRACT_FIELDS = ("process", "readiness", "stores", "model")


def assess(checks: dict[str, str]) -> dict[str, Any]:
    """checks values are pass, fail, or blocked. Missing checks are blocked."""
    ordered = {name: checks.get(name, "blocked") for name in REQUIRED}
    passed = sum(1 for value in ordered.values() if value == "pass")
    failed = any(value == "fail" for value in ordered.values())
    blocked = any(value == "blocked" for value in ordered.values())
    if passed == len(REQUIRED):
        state = "CONNECTED_VERIFIED"
    elif failed and passed:
        state = "PARTIALLY_CONNECTED"
    elif failed and blocked:
        state = "BLOCKED"
    elif failed:
        state = "FAILED"
    else:
        state = "BLOCKED"
    return {
        "state": state,
        "passed": passed,
        "required": len(REQUIRED),
        "checks": ordered,
        "source_revision": SOURCE_REVISION,
        "scope": "live",
    }


def health_payload(body: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    detail = parsed.get("detail")
    if isinstance(detail, dict) and "readiness" in detail:
        return detail
    return parsed


def classify_health(status: int, body: str) -> str:
    """The current contract can be served with HTTP 503 when a store is down."""
    payload = health_payload(body)
    if not isinstance(payload, dict):
        return "fail"
    if all(field in payload for field in CONTRACT_FIELDS):
        return "pass" if status in {200, 503} else "fail"
    return "fail"


def classify_unauthorized(status: int) -> str:
    return "pass" if status == 401 else "fail"


def classify_inference(status: int, body: str) -> dict[str, str]:
    """Map one authenticated explain response. Never treats HTTP 200 alone as success."""
    blocked = {
        "aurex_to_qwen_authenticated": "blocked",
        "qwen_generated_text": "blocked",
        "invalid_model_identity_rejected": "blocked",
        "model_unavailable_explicit": "blocked",
        "timeout_bounded": "blocked",
        "synthetic_end_to_end": "blocked",
    }
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = None
    if status == 401:
        blocked["aurex_to_qwen_authenticated"] = "fail"
        return blocked
    if not isinstance(payload, dict):
        blocked["aurex_to_qwen_authenticated"] = "fail"
        return blocked
    if status == 503 and payload.get("detail") in {
        "Staging disabled",
        "Zero budget required",
    }:
        return blocked
    code = payload.get("error_code")
    execution = payload.get("execution")
    answer = payload.get("generated_answer")
    text = answer.strip() if isinstance(answer, str) else ""
    if execution == "PASS" and text and status == 200:
        blocked["aurex_to_qwen_authenticated"] = "pass"
        blocked["qwen_generated_text"] = "pass"
        blocked["synthetic_end_to_end"] = "pass"
        return blocked
    if code == "MODEL_IDENTITY_MISMATCH":
        blocked["aurex_to_qwen_authenticated"] = "pass"
        blocked["invalid_model_identity_rejected"] = "pass"
        blocked["qwen_generated_text"] = "fail"
        return blocked
    if code == "MODEL_UNAVAILABLE":
        blocked["model_unavailable_explicit"] = "pass"
        blocked["aurex_to_qwen_authenticated"] = "fail"
        return blocked
    if code == "TIMEOUT":
        blocked["timeout_bounded"] = "pass"
        blocked["aurex_to_qwen_authenticated"] = "fail"
        return blocked
    if code == "AUTHENTICATION_FAILURE":
        blocked["aurex_to_qwen_authenticated"] = "fail"
        return blocked
    blocked["aurex_to_qwen_authenticated"] = "fail"
    blocked["qwen_generated_text"] = "fail"
    return blocked


def classify_website_bundle(text: str) -> tuple[str, str]:
    """The public bundle must not contain a service token. Prompts alone are not a round trip."""
    if "AUREX_SERVICE_TOKEN" in text or "Bearer " in text:
        return "fail", "fail"
    has_prompt = "Explain a synthetic field ticket discrepancy." in text
    has_live_label = "Staging answer, not financial or security authority:" in text
    reaches = "blocked"
    displays = "pass" if has_prompt and has_live_label else "fail"
    return reaches, displays


def _read(
    url: str,
    timeout: float,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, str]:
    request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(20_000).decode("utf-8", "replace")


def observe_here() -> tuple[dict[str, str], dict[str, Any]]:
    checks = {name: "blocked" for name in REQUIRED}
    evidence: dict[str, Any] = {"scope": "live", "source_revision": SOURCE_REVISION}
    try:
        socket.getaddrinfo(PRIVATE_HOST, 8080)
        checks["private_qwen_dns"] = "pass"
        evidence["private_qwen_dns"] = "resolved"
    except socket.gaierror as exc:
        checks["private_qwen_dns"] = "fail"
        evidence["private_qwen_dns"] = exc.strerror or "unresolved"
    try:
        status, body = _read(STAGING_HEALTH, 20)
        checks["railway_aurex_current_contract"] = classify_health(status, body)
        payload = health_payload(body) or {}
        evidence["health"] = {
            "http_status": status,
            "readiness": payload.get("readiness"),
            "model": payload.get("model"),
            "stores": payload.get("stores"),
        }
    except (urllib.error.URLError, TimeoutError, OSError):
        checks["railway_aurex_current_contract"] = "fail"
        evidence["health"] = {"http_status": None}
    try:
        status, _body = _read(
            STAGING_EXPLAIN,
            20,
            "POST",
            b'{"prompt":"Explain a synthetic field ticket discrepancy."}',
            {"Content-Type": "application/json"},
        )
        checks["unauthorized_rejected"] = classify_unauthorized(status)
        evidence["unauthorized_http_status"] = status
    except (urllib.error.URLError, TimeoutError, OSError):
        checks["unauthorized_rejected"] = "fail"
    token = os.environ.get("AUREX_STAGING_SERVICE_TOKEN", "")
    if len(token) < 32:
        evidence["authenticated_inference"] = "blocked: staging service token is unset"
    else:
        try:
            status, body = _read(
                STAGING_EXPLAIN,
                110,
                "POST",
                b'{"prompt":"Explain a synthetic field ticket discrepancy."}',
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                    "x-aurex-operator-approval": "synthetic-only",
                },
            )
            checks.update(classify_inference(status, body))
            payload = {}
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    payload = parsed
            except json.JSONDecodeError:
                payload = {}
            evidence["authenticated_inference"] = {
                "http_status": status,
                "execution": payload.get("execution"),
                "error_code": payload.get("error_code"),
                "answer_present": bool(str(payload.get("generated_answer") or "").strip()),
                "input_sha256": payload.get("input_sha256"),
                "output_sha256": payload.get("output_sha256"),
            }
        except TimeoutError:
            checks["aurex_to_qwen_authenticated"] = "fail"
            checks["timeout_bounded"] = "pass"
            evidence["authenticated_inference"] = "timeout"
        except (urllib.error.URLError, OSError):
            checks["aurex_to_qwen_authenticated"] = "fail"
            evidence["authenticated_inference"] = "unreachable"
    try:
        status, html = _read(WEBSITE, 20, headers={"User-Agent": "aurex-connectivity-check"})
        if status != 200:
            evidence["website"] = {"http_status": status, "bundle": False}
        else:
            src = ""
            marker = "/assets/xaeli-"
            start = html.find(marker)
            if start >= 0:
                end = html.find(".js", start)
                src = html[start : end + 3] if end > start else ""
            bundle = ""
            if src.startswith("/assets/xaeli-") and src.endswith(".js"):
                bundle_status, bundle = _read(
                    "https://valexii.com" + src,
                    20,
                    headers={"User-Agent": "aurex-connectivity-check"},
                )
                if bundle_status != 200:
                    bundle = ""
            reaches, displays = classify_website_bundle(bundle or html)
            checks["xaeli_website_reaches_aurex"] = reaches
            checks["xaeli_displays_generated_text"] = displays
            evidence["website"] = {
                "http_status": status,
                "bundle": bool(bundle),
                "prompt_ui": displays,
            }
    except (urllib.error.URLError, TimeoutError, OSError):
        evidence["website"] = "unreachable"
    evidence["not_executed_from_this_network"] = [
        name
        for name in (
            "invalid_model_identity_rejected",
            "model_unavailable_explicit",
            "tenant_isolation_preserved",
            "xaeli_website_reaches_aurex",
        )
        if checks[name] == "blocked"
    ]
    return checks, evidence


def main() -> int:
    checks, evidence = observe_here()
    report = assess(checks)
    report["evidence"] = evidence
    report["paid_inference"] = "OFF"
    report["expected_model"] = EXPECTED_MODEL
    report["verified_model"] = None
    report["secret_material"] = "omitted"
    report["qwen_auth"] = {
        "server_env": "LLAMA_API_KEY or LLAMA_ARG_API_KEY_FILE",
        "client_env": "AUREX_MODEL_API_KEY",
        "header": "Authorization: Bearer",
        "values": "omitted",
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report["state"] == "CONNECTED_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
