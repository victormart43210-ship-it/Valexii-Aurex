"""Read-only, operator-triggered five-contract Railway AUREX probe.

Never posts, deploys, accesses Cloudflare, changes jobs or emits the bearer secret.
Direct Railway success must not be described as a Cloudflare-to-Railway attestation.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import math
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

BASE = "https://aurex-api-production-c535.up.railway.app"
LIMIT = 256 * 1024
PATHS = ("/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
CAP = re.compile(r"^[a-z_-]{1,64}$")
HEX = re.compile(r"^[0-9a-f]{64}$")
VER = re.compile(r"^[A-Za-z0-9._-]{1,32}$")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def exact(v, keys):
    return isinstance(v, dict) and set(v) == set(keys)


def iso(s):
    if not isinstance(s, str) or len(s) > 48:
        return False
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.tzinfo is not None and d.utcoffset() is not None
    except ValueError:
        return False


def money(n):
    return type(n) in (float, int) and math.isfinite(n) and 0 <= n <= 10_000


def cap(c):
    return (exact(c, ("id", "available", "evidenceId", "verifiedAt"))
            and isinstance(c["id"], str) and bool(CAP.fullmatch(c["id"]))
            and type(c["available"]) is bool
            and (c["evidenceId"] is None or isinstance(c["evidenceId"], str)
                 and bool(ID.fullmatch(c["evidenceId"])))
            and (c["verifiedAt"] is None or iso(c["verifiedAt"])))


def evidence(e):
    return (exact(e, ("id", "capabilityId", "kind", "collectedAt", "sha256", "summary"))
            and isinstance(e["id"], str) and bool(ID.fullmatch(e["id"]))
            and isinstance(e["capabilityId"], str) and bool(CAP.fullmatch(e["capabilityId"]))
            and e["kind"] in ("test_run", "health_probe", "benchmark_record", "offline_probe")
            and iso(e["collectedAt"])
            and isinstance(e["sha256"], str) and bool(HEX.fullmatch(e["sha256"]))
            and isinstance(e["summary"], str) and len(e["summary"]) <= 500)


def job(j):
    return (exact(j, ("id", "kind", "state", "createdAt", "updatedAt", "reservationUsd"))
            and isinstance(j["id"], str) and bool(ID.fullmatch(j["id"]))
            and j["kind"] in ("benchmark", "hypothesis_test", "regression_scan")
            and j["state"] in ("queued", "running", "succeeded", "failed", "cancelled")
            and iso(j["createdAt"]) and iso(j["updatedAt"]) and money(j["reservationUsd"]))


def valid(path, d):
    if path == "/v1/health":
        return (exact(d, ("status", "version", "time")) and d["status"] == "ok"
                and isinstance(d["version"], str) and bool(VER.fullmatch(d["version"]))
                and iso(d["time"]))
    if path == "/v1/capabilities":
        return (exact(d, ("capabilities",)) and isinstance(d["capabilities"], list)
                and len(d["capabilities"]) <= 100 and all(cap(x) for x in d["capabilities"]))
    if path == "/v1/evidence":
        return (exact(d, ("evidence",)) and isinstance(d["evidence"], list)
                and len(d["evidence"]) <= 200 and all(evidence(x) for x in d["evidence"]))
    if path == "/v1/budgets":
        return (exact(d, ("limitUsd", "reservedUsd", "spentUsd", "period"))
                and all(money(d[x]) for x in ("limitUsd", "reservedUsd", "spentUsd"))
                and d["period"] in ("day", "month"))
    if path == "/v1/jobs":
        return (exact(d, ("jobs", "nextCursor")) and isinstance(d["jobs"], list)
                and len(d["jobs"]) <= 200
                and (d["nextCursor"] is None or isinstance(d["nextCursor"], str)
                     and len(d["nextCursor"]) <= 128)
                and all(job(x) for x in d["jobs"]))
    return False


def expected_readonly(path, d):
    if path == "/v1/capabilities":
        return all(c["available"] is False and c["evidenceId"] is None for c in d["capabilities"])
    if path == "/v1/evidence":
        return d["evidence"] == []
    if path == "/v1/budgets":
        return all(d[k] == 0 for k in ("limitUsd", "reservedUsd", "spentUsd"))
    if path == "/v1/jobs":
        return d["jobs"] == [] and d["nextCursor"] is None
    return True


def fetch(path, token):
    """Fixed HTTPS origin, no proxies/redirects, bounded body, GET only."""
    if path not in PATHS:
        raise ValueError("unsupported path")
    request = Request(BASE + path, method="GET", headers={
        "Authorization": "Bearer " + token, "Accept": "application/json",
        "User-Agent": "AUREX-operator-readonly-probe/1",
    })
    with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=7) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read(LIMIT + 1)


def probe(token, transport=fetch):
    report = {
        "schema": "AUREX_OPERATOR_DIRECT_RAILWAY_V1",
        "observedAt": datetime.now(UTC).isoformat(),
        "targetHost": "aurex-api-production-c535.up.railway.app",
        "checks": [], "directRailwayVerified": False,
        "cloudflareOriginVerified": False, "websiteRenderingVerified": False,
        "productionAuthority": "HOLD",
    }
    if len(token) < 32:
        report["checks"].append({"path": "CONFIG", "status": "FAIL", "reason": "TOKEN_INVALID"})
        return report
    for path in PATHS:
        result = {"path": path, "status": "FAIL"}
        try:
            status, ctype, body = transport(path, token)
            result["httpStatus"] = status
            if status != 200:
                result["reason"] = "HTTP_NON_200"
            elif ctype.split(";", 1)[0].strip().lower() != "application/json":
                result["reason"] = "BAD_CONTENT_TYPE"
            elif len(body) > LIMIT:
                result["reason"] = "TOO_LARGE"
            else:
                try:
                    value = json.loads(body.decode("utf-8", "strict"))
                    if valid(path, value) and expected_readonly(path, value):
                        result["status"] = "PASS"
                        result["reason"] = "READONLY_CONTRACT_VALID"
                        result["responseSHA256"] = hashlib.sha256(body).hexdigest()
                    else:
                        result["reason"] = "SCHEMA_OR_POLICY_MISMATCH"
                except (ValueError, UnicodeDecodeError):
                    result["reason"] = "MALFORMED"
        except (HTTPError, Exception):
            # Never echo upstream exceptions, tokens or response bodies into reports.
            result["reason"] = "HTTP_OR_NETWORK_FAILURE"
        report["checks"].append(result)
    report["directRailwayVerified"] = all(x["status"] == "PASS" for x in report["checks"])
    return report


def main():
    p = argparse.ArgumentParser(description="Five direct Railway GETs; no deployment, jobs or Cloudflare changes")
    p.add_argument("--live", action="store_true", help="Explicitly allow real Railway GETs")
    p.add_argument("--report", type=Path, help="Save sanitized evidence once with 0600 file permissions")
    args = p.parse_args()
    if not args.live:
        p.error("No network executed. Specify --live to check actual Railway.")
    token = os.getenv("AUREX_SERVICE_TOKEN", "")
    if not token:
        if not sys.stdin.isatty():
            p.error("Missing AUREX_SERVICE_TOKEN; run interactively for hidden prompt.")
        token = getpass.getpass("AUREX_SERVICE_TOKEN (hidden): ")
    result = probe(token)
    output = json.dumps(result, indent=2, sort_keys=True)
    print(output)
    if args.report:
        fd = os.open(args.report, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(output + "\n")
    return 0 if result["directRailwayVerified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
