#!/usr/bin/env python3
"""Staging promotion gate: fail if the XAELI conversation route is missing.

Usage: verify_xaeli_chat_route.py BASE_URL [--token-env AUREX_SERVICE_TOKEN] [--inference]

Without a token it checks only that the route exists and rejects anonymous callers
(401/403, never 404/405). With a token it sends one bounded message and, with --inference,
requires a PASS answer that names the private Qwen model. A passing run is route and
contract evidence; live website acceptance is still a separate, independent check.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit

PATH = "/v1/xaeli-chat/ask"
STAGING_PATH = "/v1/xaeli-staging/explain"
REQUIRED_FIELDS = (
    "state", "authority", "independent_verification", "execution",
    "generated_answer", "model", "diagnostic_ref", "error_code",
)


def classify_anonymous(status: int) -> str:
    if status in (404, 405):
        return "FAIL_ROUTE_MISSING"
    if status in (401, 403):
        return "PASS"
    return "FAIL_UNEXPECTED_STATUS"


def classify_openapi(spec: Any) -> str:
    paths = spec.get("paths") if isinstance(spec, dict) else None
    if not isinstance(paths, dict) or PATH not in paths or "post" not in paths[PATH]:
        return "FAIL_ROUTE_MISSING"
    return "PASS" if STAGING_PATH in paths else "FAIL_STAGING_ROUTE_MISSING"


def classify_answer(status: int, body: Any) -> str:
    if status == 404:
        return "FAIL_ROUTE_MISSING"
    if status != 200 or not isinstance(body, dict):
        return "FAIL_NOT_ANSWERED"
    if any(field not in body for field in REQUIRED_FIELDS):
        return "FAIL_CONTRACT"
    if body["authority"] != "NONE" or body["independent_verification"] != "NOT VERIFIED":
        return "FAIL_AUTHORITY_CLAIM"
    answer = body["generated_answer"]
    if body["execution"] != "PASS" or not isinstance(answer, str) or not answer.strip():
        return "FAIL_NO_GENERATED_ANSWER"
    model = body["model"]
    if not isinstance(model, dict) or "qwen" not in str(model.get("model", "")).lower():
        return "FAIL_MODEL_IDENTITY"
    return "PASS"


def _call(url: str, method: str, data: bytes | None, headers: dict[str, str],
          timeout: float) -> tuple[int, Any]:
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            status, raw = response.status, response.read(1_000_000)
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read(1_000_000)
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("--token-env", default="AUREX_SERVICE_TOKEN")
    parser.add_argument("--inference", action="store_true")
    args = parser.parse_args(argv)
    base = args.base_url.rstrip("/")
    if urlsplit(base).scheme not in ("https", "http"):
        print("FAIL base_url must be http(s)")
        return 2
    json_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    results: dict[str, str] = {}
    _, spec = _call(base + "/openapi.json", "GET", None, {"Accept": "application/json"}, 15)
    results["openapi_route_registered"] = classify_openapi(spec)
    status, _ = _call(base + PATH, "POST", b'{"message":"ping"}', json_headers, 15)
    results["anonymous_rejected_not_404"] = classify_anonymous(status)
    token = os.environ.get(args.token_env)
    if token and args.inference:
        headers = {**json_headers, "Authorization": f"Bearer {token}",
                   "x-aurex-operator-approval": "advisory-chat"}
        status, body = _call(base + PATH, "POST", b'{"message":"What is AUREX-OX?"}', headers, 120)
        results["generated_answer"] = classify_answer(status, body)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if all(value == "PASS" for value in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
