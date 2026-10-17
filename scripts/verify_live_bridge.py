#!/usr/bin/env python3
"""AUREX Live Bridge Verification Utility (Operation IRON BRIDGE Sovereign Remediation)."""

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any

ALLOWED_HOSTS = {"aurex-api-production-c535.up.railway.app", "127.0.0.1", "localhost", "testserver"}
MAX_PAYLOAD_BYTES = 256 * 1024  # 256 KiB max


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        # Disable redirects at transport layer to prevent Bearer credential leakage
        return None


def validate_endpoint_schema(path: str, body: dict[str, Any]) -> bool:
    if not isinstance(body, dict) or not body:
        return False

    if path in ("/v1/health", "/health"):
        return "status" in body and isinstance(body.get("status"), str)

    if path == "/v1/capabilities":
        caps = body.get("capabilities")
        if not isinstance(caps, list):
            return False
        for c in caps:
            if not isinstance(c, dict) or "id" not in c or "available" not in c:
                return False
        return True

    if path == "/v1/evidence":
        ev = body.get("evidence")
        if not isinstance(ev, list):
            return False
        for item in ev:
            if not isinstance(item, dict) or "id" not in item or "sha256" not in item:
                return False
        return True

    if path == "/v1/budgets":
        return "limitUsd" in body and isinstance(body.get("limitUsd"), (int, float))

    if path == "/v1/jobs":
        jobs = body.get("jobs")
        if not isinstance(jobs, list):
            return False
        for j in jobs:
            if not isinstance(j, dict) or "id" not in j or "state" not in j:
                return False
        return True

    return False


def verify_live_endpoint(
    base_url: str,
    path: str,
    token: str | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(base_url)

    # Require HTTPS in production
    if parsed.hostname == "aurex-api-production-c535.up.railway.app" and parsed.scheme != "https":
        return {
            "path": path,
            "status": "REJECTED",
            "reason": "Production endpoint requires HTTPS scheme",
        }

    if parsed.hostname not in ALLOWED_HOSTS:
        return {
            "path": path,
            "status": "REJECTED",
            "reason": f"Host '{parsed.hostname}' is not in allowlist",
        }

    url = urllib.parse.urljoin(base_url, path)
    req = urllib.request.Request(url, method="GET")

    if token:
        req.add_header("Authorization", f"Bearer {token}")

    opener = urllib.request.build_opener(NoRedirectHandler())
    start_time = datetime.now(UTC)

    try:
        with opener.open(req, timeout=timeout) as resp:
            data = resp.read(MAX_PAYLOAD_BYTES + 1)
            if len(data) > MAX_PAYLOAD_BYTES:
                return {
                    "path": path,
                    "status": "FAIL",
                    "reason": "Response exceeded maximum payload size (256 KiB)",
                }

            elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000.0
            body_json = json.loads(data.decode("utf-8"))

            if not validate_endpoint_schema(path, body_json):
                return {
                    "path": path,
                    "http_code": resp.status,
                    "status": "FAIL",
                    "reason": "FAIL — SCHEMA INVALID: Response payload does not satisfy schema",
                }

            # Sanitized summary without dumping raw response
            record_count = len(body_json.get("capabilities") or body_json.get("evidence") or body_json.get("jobs") or [])
            return {
                "path": path,
                "http_code": resp.status,
                "elapsed_ms": round(elapsed_ms, 2),
                "schema_valid": True,
                "record_count": record_count,
                "status": "PASS",
            }
    except urllib.error.HTTPError as exc:
        return {
            "path": path,
            "http_code": exc.code,
            "status": "FAIL",
            "reason": f"HTTP {exc.code}: {exc.reason}",
        }
    except Exception as exc:
        return {
            "path": path,
            "status": "FAIL",
            "reason": str(exc),
        }


def run_bridge_verification(
    base_url: str = "https://aurex-api-production-c535.up.railway.app",
    token: str | None = None,
) -> dict[str, Any]:
    effective_token = token or os.environ.get("AUREX_SERVICE_TOKEN") or os.environ.get("AUREX_ADMIN_TOKEN")

    endpoints = ["/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs"]
    results = {}
    all_pass = True

    for ep in endpoints:
        res = verify_live_endpoint(base_url, ep, token=effective_token)
        results[ep] = res
        if res.get("status") != "PASS":
            all_pass = False

    report = {
        "verified_at": datetime.now(UTC).isoformat(),
        "base_url": base_url,
        "token_present": bool(effective_token),
        "endpoint_results": results,
        "status": "PASS" if all_pass else "HOLD",
    }
    report_bytes = json.dumps(report, sort_keys=True).encode("utf-8")
    report["report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    return report


def main() -> None:
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://aurex-api-production-c535.up.railway.app"
    report = run_bridge_verification(target_url)
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
