#!/usr/bin/env python3
"""Fail-closed, read-only AUREX v1 production transport verifier.

This verifies transport/contract only. It cannot grant identity, model or release authority.
No job submission, model execution or website owner session is performed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any

PRODUCTION_HOST = "aurex-api-production-c535.up.railway.app"
PRODUCTION_BASE = f"https://{PRODUCTION_HOST}"
ENDPOINTS = (
    "/v1/health",
    "/v1/capabilities",
    "/v1/evidence",
    "/v1/budgets",
    "/v1/jobs",
)
MAX_PAYLOAD_BYTES = 256 * 1024
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
CAP_ID_PATTERN = re.compile(r"[a-z_-]{1,64}\Z")
HEX_SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z")
JOB_KINDS = frozenset(("benchmark", "hypothesis_test", "regression_scan"))
JOB_STATES = frozenset(("queued", "running", "succeeded", "failed", "cancelled"))
EVIDENCE_KINDS = frozenset(("test_run", "health_probe", "benchmark_record", "offline_probe"))


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never redirect requests carrying bearer credentials, even within the same host."""

    def redirect_request(  # type: ignore[override]
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("Non-finite JSON constant")


def _parse_response(raw: bytes) -> Any:
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_no_duplicate_keys,
        parse_constant=_reject_constant,
    )


def _keys(v: Any, required: frozenset[str], optional: frozenset[str] = frozenset()) -> bool:
    return isinstance(v, dict) and required <= v.keys() and v.keys() <= required | optional


def _string(v: Any, max_len: int, min_len: int = 0) -> bool:
    return isinstance(v, str) and min_len <= len(v) <= max_len


def _id(v: Any) -> bool:
    return isinstance(v, str) and ID_PATTERN.fullmatch(v) is not None


def _date(v: Any) -> bool:
    if not isinstance(v, str) or not TIME_PATTERN.fullmatch(v):
        return False
    try:
        t = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return False
    return t.tzinfo is not None and t.utcoffset() is not None


def _number(v: Any, maximum: float | None = None) -> bool:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    try:
        return math.isfinite(v) and v >= 0 and (maximum is None or v <= maximum)
    except OverflowError:
        return False


def _capability(c: Any) -> bool:
    keys = frozenset(("id", "available", "evidenceId", "verifiedAt"))
    return (
        _keys(c, keys)
        and isinstance(c["id"], str)
        and CAP_ID_PATTERN.fullmatch(c["id"]) is not None
        and isinstance(c["available"], bool)
        and (c["evidenceId"] is None or _id(c["evidenceId"]))
        and (c["verifiedAt"] is None or _date(c["verifiedAt"]))
    )


def _evidence(e: Any) -> bool:
    keys = frozenset(("id", "capabilityId", "kind", "collectedAt", "sha256", "summary"))
    return (
        _keys(e, keys)
        and _id(e["id"])
        and isinstance(e["capabilityId"], str)
        and CAP_ID_PATTERN.fullmatch(e["capabilityId"]) is not None
        and isinstance(e["kind"], str)
        and e["kind"] in EVIDENCE_KINDS
        and _date(e["collectedAt"])
        and isinstance(e["sha256"], str)
        and HEX_SHA_PATTERN.fullmatch(e["sha256"]) is not None
        and _string(e["summary"], 500)
    )


def _job(j: Any) -> bool:
    keys = frozenset(("id", "kind", "state", "createdAt", "updatedAt", "reservationUsd"))
    return (
        _keys(j, keys)
        and _id(j["id"])
        and isinstance(j["kind"], str)
        and j["kind"] in JOB_KINDS
        and isinstance(j["state"], str)
        and j["state"] in JOB_STATES
        and _date(j["createdAt"])
        and _date(j["updatedAt"])
        and _number(j["reservationUsd"], 10_000)
    )


def validate_endpoint_schema(path: str, body: Any) -> bool:
    """Mirror the strict frontend Zod v1 response contracts, without allowing extra fields."""
    if path == "/v1/health":
        return (
            _keys(body, frozenset(("status", "version", "time")))
            and body["status"] == "ok"
            and _string(body["version"], 32)
            and _date(body["time"])
        )
    if path == "/v1/capabilities":
        return (
            _keys(body, frozenset(("capabilities",)))
            and isinstance(body["capabilities"], list)
            and len(body["capabilities"]) <= 100
            and all(_capability(c) for c in body["capabilities"])
        )
    if path == "/v1/evidence":
        return (
            _keys(body, frozenset(("evidence",)))
            and isinstance(body["evidence"], list)
            and len(body["evidence"]) <= 200
            and all(_evidence(e) for e in body["evidence"])
        )
    if path == "/v1/budgets":
        return (
            _keys(body, frozenset(("limitUsd", "reservedUsd", "spentUsd", "period")))
            and all(_number(body[k]) for k in ("limitUsd", "reservedUsd", "spentUsd"))
            and body["period"] in ("day", "month")
        )
    if path == "/v1/jobs":
        return (
            _keys(body, frozenset(("jobs", "nextCursor")))
            and isinstance(body["jobs"], list)
            and len(body["jobs"]) <= 200
            and all(_job(j) for j in body["jobs"])
            and (body["nextCursor"] is None or _string(body["nextCursor"], 128))
        )
    return False


def _verified_destination(base_url: str, path: str, allow_loopback: bool) -> str | None:
    """Validate a canonical base and fixed path *before* a network request is constructed."""
    if path not in ENDPOINTS:
        return None
    try:
        parsed = urllib.parse.urlsplit(base_url)
        if (
            parsed.username is not None
            or parsed.password is not None
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            return None
        if parsed.hostname == PRODUCTION_HOST:
            if parsed.scheme != "https" or parsed.port not in (None, 443):
                return None
            origin = PRODUCTION_BASE
        elif allow_loopback and parsed.hostname in ("127.0.0.1", "localhost"):
            if parsed.scheme != "http":
                return None
            port = parsed.port
            if port is None or not 1 <= port <= 65535:
                return None
            origin = f"http://{parsed.hostname}:{port}"
        else:
            return None
    except (ValueError, TypeError):
        return None
    # Never use urljoin: absolute-path inputs cannot override the approved origin.
    return f"{origin}{path}"


def verify_live_endpoint(
    base_url: str,
    path: str,
    token: str | None = None,
    timeout: float = 5.0,
    *,
    allow_loopback: bool = False,
) -> dict[str, Any]:
    """Issue one authorized GET; report only sanitized transport/schema metadata."""
    url = _verified_destination(base_url, path, allow_loopback)
    if url is None:
        return {"path": path, "status": "REJECTED", "reason": "Unapproved URL or endpoint"}
    if not token or len(token) < 32 or "\n" in token or "\r" in token:
        return {"path": path, "status": "HOLD", "reason": "Valid bearer credential unavailable"}
    if not 0 < timeout <= 10:
        return {"path": path, "status": "REJECTED", "reason": "Invalid timeout"}

    req = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    # No HTTP redirects, proxy inherited from environment, no retries.
    opener = urllib.request.build_opener(NoRedirectHandler())
    started = time.monotonic()
    try:
        with opener.open(req, timeout=timeout) as response:
            code = response.status
            if code != 200:
                return {"path": path, "status": "HOLD", "http_code": code, "reason": "Unexpected HTTP status"}
            raw = response.read(MAX_PAYLOAD_BYTES + 1)
            if len(raw) > MAX_PAYLOAD_BYTES:
                return {"path": path, "status": "HOLD", "http_code": code, "reason": "Response too large"}
            try:
                body = _parse_response(raw)
            except (UnicodeError, ValueError, TypeError):
                return {"path": path, "status": "HOLD", "http_code": code, "reason": "Malformed JSON"}
            if not validate_endpoint_schema(path, body):
                return {"path": path, "status": "HOLD", "http_code": code, "reason": "FAIL — SCHEMA INVALID"}
            records_field = {"/v1/capabilities": "capabilities", "/v1/evidence": "evidence", "/v1/jobs": "jobs"}.get(path)
            count = len(body[records_field]) if records_field else None
            return {
                "path": path,
                "status": "PASS",
                "http_code": code,
                "schema_valid": True,
                "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
                "record_count": count,
            }
    except urllib.error.HTTPError as exc:
        return {
            "path": path,
            "status": "HOLD",
            "http_code": exc.code,
            "reason": "Redirect rejected" if 300 <= exc.code < 400 else "HTTP request unsuccessful",
        }
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return {"path": path, "status": "HOLD", "reason": "Network or transport failure"}


def run_bridge_verification(
    base_url: str = PRODUCTION_BASE,
    token: str | None = None,
    *,
    allow_loopback: bool = False,
) -> dict[str, Any]:
    """Summarize five GETs; isolated loopback mode never represents live production PASS."""
    effective_token = token if token is not None else os.environ.get("AUREX_SERVICE_TOKEN")
    results: dict[str, Any] = {
        path: verify_live_endpoint(base_url, path, token=effective_token, allow_loopback=allow_loopback)
        for path in ENDPOINTS
    }
    all_pass = all(result["status"] == "PASS" for result in results.values())
    mode = "ISOLATED_TEST" if allow_loopback else "PRODUCTION_BACKEND_DIRECT"
    report: dict[str, Any] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "target_host": "LOOPBACK" if allow_loopback else PRODUCTION_HOST,
        "verification_mode": mode,
        "token_present": bool(effective_token),
        "endpoint_results": results,
        "backend_transport": "PASS" if all_pass else "HOLD",
        "website_to_backend": "NOT VERIFIED",
        "authority": "NONE",
        "status": "PASS_TEST_ONLY" if all_pass and allow_loopback else "PASS_TRANSPORT_ONLY" if all_pass else "HOLD",
    }
    report_bytes = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    report["report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    return report


def main() -> None:
    if len(sys.argv) > 1:
        raise SystemExit("This verifier accepts no arbitrary URL arguments. Set AUREX_SERVICE_TOKEN securely.")
    report = run_bridge_verification()
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASS_TRANSPORT_ONLY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
