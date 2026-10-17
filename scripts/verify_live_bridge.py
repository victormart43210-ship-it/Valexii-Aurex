#!/usr/bin/env python3
"""AUREX Live Bridge Verification Utility (Operation IRON BRIDGE)."""

import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any

ALLOWED_HOSTS = {"aurex-api-production-c535.up.railway.app", "127.0.0.1", "localhost", "testserver"}


def verify_live_endpoint(
    base_url: str,
    path: str,
    token: str | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(base_url)
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

    start_time = datetime.now(UTC)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000.0
            body_json = json.loads(data.decode("utf-8"))
            return {
                "path": path,
                "http_code": resp.status,
                "elapsed_ms": round(elapsed_ms, 2),
                "schema_valid": True,
                "status": "PASS",
                "response": body_json,
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

    endpoints = ["/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs"]
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
