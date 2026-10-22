"""Bounded, read-only AUREX staging bridge probe; offline unless explicitly authorized.

Never sends credentials outside the exact canonical staging host. Never publishes
status as security authority or independently verified model efficacy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

STAGING_HOST = "aurex-api-aurex-staging.up.railway.app"
STAGING_URL = "https://" + STAGING_HOST
TOKEN_ENV = "AUREX_SERVICE_TOKEN"
MAX_BYTES = 256 * 1024
ROUTES = ("/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs")
MAX_ITEMS = 200


class BridgeFailure(ValueError):
    """A bounded transport/schema failure with no sensitive exception details."""


def staging_origin_allowed(raw: str | None) -> bool:
    """Fail closed: userinfo, noncanonical port, path, query, fragment, or IP forbidden."""
    if not raw:
        return False
    try:
        parsed = urlsplit(raw)
        return (
            parsed.scheme == "https"
            and parsed.netloc == STAGING_HOST
            and parsed.hostname == STAGING_HOST
            and parsed.port is None
            and parsed.username is None
            and parsed.password is None
            and parsed.path in ("", "/")
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def _read_json(opener: Any, url: str, token: str) -> Any:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    try:
        with opener.open(request, timeout=5) as response:
            if response.status != 200:
                raise BridgeFailure("unexpected_http_status")
            if not response.headers.get("Content-Type", "").lower().startswith("application/json"):
                raise BridgeFailure("unexpected_content_type")
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        # Do not print provider payloads or errors containing credentials.
        raise BridgeFailure("http_" + str(exc.code)) from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise BridgeFailure("transport_unavailable") from None
    if len(raw) > MAX_BYTES:
        raise BridgeFailure("response_too_large")
    try:
        return json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, ValueError):
        raise BridgeFailure("malformed_json") from None


def _bounded_records(value: Any, key: str, limit: int = MAX_ITEMS) -> None:
    if not isinstance(value, dict) or not isinstance(value.get(key), list):
        raise BridgeFailure("invalid_" + key)
    if len(value[key]) > limit:
        raise BridgeFailure("too_many_" + key)


def validate_route(path: str, value: Any) -> None:
    """Transport-level shape validation only, not full schema or factual proof."""
    if path == "/v1/health":
        if not (isinstance(value, dict) and value.get("status") == "ok"
                and isinstance(value.get("version"), str)
                and isinstance(value.get("time"), str)):
            raise BridgeFailure("invalid_health")
        try:
            datetime.fromisoformat(value["time"].replace("Z", "+00:00"))
        except ValueError:
            raise BridgeFailure("invalid_health_time") from None
    elif path == "/v1/capabilities":
        _bounded_records(value, "capabilities", 100)
    elif path == "/v1/evidence":
        _bounded_records(value, "evidence")
    elif path == "/v1/jobs":
        _bounded_records(value, "jobs")
        if "nextCursor" not in value or not (value["nextCursor"] is None or isinstance(value["nextCursor"], str)):
            raise BridgeFailure("invalid_job_cursor")
    elif path == "/v1/budgets":
        if not isinstance(value, dict) or value.get("period") not in ("day", "month"):
            raise BridgeFailure("invalid_budget")
        for field in ("limitUsd", "reservedUsd", "spentUsd"):
            n = value.get(field)
            if isinstance(n, bool) or not isinstance(n, (int, float)) or n < 0 or n != n:
                raise BridgeFailure("invalid_budget")
    else:
        raise BridgeFailure("unapproved_path")


def run(*, execute: bool = False, approve_staging: bool = False,
        url: str | None = None, token: str | None = None, opener: Any = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "status": "STAGED", "execute": "NOT RUN", "target": "AUREX_STAGING_ONLY",
        "checks": {}, "authority": "NONE", "verification": "NOT VERIFIED",
        "release": "HOLD", "paid_inference": "NOT RUN", "effects": "NONE",
    }
    if not execute:
        return report
    if not approve_staging:
        return {**report, "status": "HOLD", "error": "explicit_staging_approval_required"}
    if not staging_origin_allowed(url):
        return {**report, "status": "HOLD", "error": "staging_origin_not_allowed"}
    if not token or len(token) < 32 or len(token) > 4096:
        return {**report, "status": "HOLD", "error": "token_not_configured"}
    transport = opener if opener is not None else urllib.request.build_opener(NoRedirect())
    checks = {}
    for path in ROUTES:
        try:
            value = _read_json(transport, STAGING_URL + path, token)
            validate_route(path, value)
        except BridgeFailure as exc:
            return {**report, "status": "FAIL", "execute": "RUN", "checks": checks,
                    "error": str(exc), "failed_route": path}
        # Digest binds received normalized JSON, not a published attestation.
        digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        checks[path] = {"transport": "PASS", "shape": "BOUNDED", "response_sha256": digest}
    return {**report, "status": "TRANSPORT_PASS", "execute": "RUN", "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Perform exactly five read-only staging GETs")
    parser.add_argument("--approve-staging", action="store_true", help="Explicitly approve remote staging reads")
    options = parser.parse_args()
    output = run(execute=options.execute, approve_staging=options.approve_staging,
                 url=os.environ.get("AUREX_STAGING_URL", STAGING_URL), token=os.environ.get(TOKEN_ENV))
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["status"] in ("STAGED", "TRANSPORT_PASS") else 2


if __name__ == "__main__":
    sys.exit(main())
