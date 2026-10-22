"""AUREX activation preflight: read-only HTTPS wire-contract check.

Never deploys, bills, writes jobs, downloads files, or claims AI verification.
Without --execute, makes ZERO network calls. Requires the owner to set the
service token as an environment variable; never prints secrets or source data.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

MAX_RESPONSE_BYTES = 256 * 1024
CAP_ID = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
EVIDENCE_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
ENDPOINTS = ("health", "capabilities", "evidence", "budgets", "jobs")
ALLOWED_EVIDENCE_KINDS = {"test_run", "health_probe", "benchmark_record", "offline_probe"}


def check_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    hostname = parsed.hostname or ""
    if (parsed.scheme != "https" or not hostname.endswith(".up.railway.app")
            or hostname == ".up.railway.app" or parsed.port is not None
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ValueError("Only plain HTTPS *.up.railway.app service roots are supported")
    return f"https://{hostname}"


def _wire_shape(endpoint: str, obj: Any) -> bool:
    if type(obj) is not dict:
        return False
    if endpoint == "health":
        return (set(obj) == {"status", "version", "time"} and obj["status"] == "ok"
                and type(obj["version"]) is str and len(obj["version"]) <= 32
                and type(obj["time"]) is str)
    if endpoint == "capabilities":
        return (set(obj) == {"capabilities"} and type(obj["capabilities"]) is list
                and len(obj["capabilities"]) <= 100
                and all(type(c) is dict and set(c) == {"id", "available", "evidenceId", "verifiedAt"}
                        and type(c["id"]) is str and CAP_ID.fullmatch(c["id"])
                        and type(c["available"]) is bool
                        and (c["evidenceId"] is None or type(c["evidenceId"]) is str)
                        and (c["verifiedAt"] is None or type(c["verifiedAt"]) is str)
                        for c in obj["capabilities"]))
    if endpoint == "evidence":
        return (set(obj) == {"evidence"} and type(obj["evidence"]) is list
                and len(obj["evidence"]) <= 200
                and all(type(e) is dict
                        and set(e) == {"id", "capabilityId", "kind", "collectedAt", "sha256", "summary"}
                        and type(e["id"]) is str and EVIDENCE_ID.fullmatch(e["id"])
                        and type(e["capabilityId"]) is str and CAP_ID.fullmatch(e["capabilityId"])
                        and type(e["kind"]) is str and e["kind"] in ALLOWED_EVIDENCE_KINDS
                        and type(e["collectedAt"]) is str
                        and type(e["sha256"]) is str and DIGEST.fullmatch(e["sha256"])
                        and type(e["summary"]) is str and len(e["summary"]) <= 500
                        for e in obj["evidence"]))
    if endpoint == "budgets":
        return (set(obj) == {"limitUsd", "reservedUsd", "spentUsd", "period"}
                and obj["period"] in ("day", "month")
                and all(type(obj[k]) in (int, float) and 0 <= obj[k] <= 1000000
                        for k in ("limitUsd", "reservedUsd", "spentUsd")))
    if endpoint == "jobs":
        return (set(obj) == {"jobs", "nextCursor"} and type(obj["jobs"]) is list
                and len(obj["jobs"]) <= 200
                and (obj["nextCursor"] is None or type(obj["nextCursor"]) is str)
                and all(type(j) is dict
                        and set(j) == {"id", "kind", "state", "createdAt", "updatedAt", "reservationUsd"}
                        and type(j["id"]) is str and EVIDENCE_ID.fullmatch(j["id"])
                        and j["kind"] in ("regression_scan", "benchmark", "hypothesis_test")
                        and j["state"] in ("queued", "running", "succeeded", "failed", "cancelled")
                        and type(j["createdAt"]) is str and type(j["updatedAt"]) is str
                        and type(j["reservationUsd"]) in (int, float) and j["reservationUsd"] >= 0
                        for j in obj["jobs"]))
    return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request: Any, fp: Any, code: int,
                         msg: str, headers: Any, newurl: str) -> None:
        return None


def _distinct_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError("duplicate JSON key")
        obj[k] = v
    return obj


def check_service(url: str, token: str,
                  opener: Any | None = None) -> dict[str, Any]:
    root = check_url(url)
    if not isinstance(token, str) or len(token) < 32:
        raise ValueError("Service token missing or shorter than backend minimum")
    if opener is None:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect(),
            urllib.request.HTTPSHandler(context=ssl.create_default_context())
        )
    states: dict[str, str] = {}
    for endpoint in ENDPOINTS:
        request = urllib.request.Request(
            root + "/v1/" + endpoint,
            method="GET", headers={
                "Accept": "application/json",
                # The existing Railway read-only bridge protects /v1/health too.
                # Authenticate all five GETs; no browser receives this token.
                "Authorization": f"Bearer {token}",
            },
        )
        try:
            with opener.open(request, timeout=5) as response:
                if response.status != 200:
                    states[endpoint] = "HOLD_HTTP_STATUS"
                    continue
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    states[endpoint] = "HOLD_TOO_LARGE"
                    continue
                try:
                    obj = json.loads(raw.decode("utf-8", errors="strict"),
                                     object_pairs_hook=_distinct_keys,
                                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                except (ValueError, UnicodeError, RecursionError):
                    states[endpoint] = "HOLD_INVALID_JSON"
                    continue
                states[endpoint] = "RESPONSE_SHAPE_OK" if _wire_shape(endpoint, obj) else "HOLD_BAD_SCHEMA"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            states[endpoint] = "HOLD_UNAVAILABLE"
    return {
        "checked": list(ENDPOINTS),
        "checks": states,
        "transport": "READ_ONLY_SHAPES_ACCEPTED" if all(
            v == "RESPONSE_SHAPE_OK" for v in states.values()
        ) else "NOT_VERIFIED",
        "backend": "NOT_INDEPENDENTLY_VERIFIED",
        "model_inference": "NOT_RUN",
        "financial_accuracy": "NOT_MEASURED",
        "customer_data": "NONE_PROCESSED",
        "production_release": "HOLD",
        "financial_authority": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only, no-spend AUREX wire preflight")
    parser.add_argument("--execute", action="store_true",
                        help="explicitly send five read-only HTTPS requests")
    args = parser.parse_args(argv)
    if not args.execute:
        print(json.dumps({
            "status": "NOT_RUN",
            "message": "No network used. Set AUREX_SERVICE_URL and AUREX_SERVICE_TOKEN "
                       "as private environment variables and pass --execute explicitly.",
            "calls": list(ENDPOINTS),
            "production_release": "HOLD",
        }, indent=2))
        return 0
    try:
        report = check_service(os.getenv("AUREX_SERVICE_URL", ""),
                               os.getenv("AUREX_SERVICE_TOKEN", ""))
    except ValueError:
        print(json.dumps({"status": "HOLD_INVALID_CONFIGURATION",
                          "production_release": "HOLD"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["transport"] == "READ_ONLY_SHAPES_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
