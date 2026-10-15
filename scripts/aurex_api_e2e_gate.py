#!/usr/bin/env python3
"""Owner-triggered, zero-paid-cost AUREX API smoke gate. Never runs against prod by default."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4


def main() -> int:
    base = os.environ.get("AUREX_E2E_BASE_URL", "").rstrip("/")
    token = os.environ.get("AUREX_E2E_TOKEN", "")
    if not base or not token or len(token) < 32:
        print("NOT RUN: set AUREX_E2E_BASE_URL and a 32+ character AUREX_E2E_TOKEN", file=sys.stderr)
        return 2
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}):
        print("FAIL: HTTPS required except localhost", file=sys.stderr)
        return 2
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        print("FAIL: invalid base URL", file=sys.stderr)
        return 2
    auth = {"Authorization": "Bearer " + token}
    def request(method, path, data=None, authenticated=True, extra=None):
        headers = {"Accept": "application/json"}
        if authenticated:
            headers.update(auth)
        if data is not None:
            headers["Content-Type"] = "application/json"
        headers.update(extra or {})
        req = urllib.request.Request(base + path, data=json.dumps(data).encode() if data is not None else None, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as exc:
            return exc.code, None
    try:
        code, _ = request("GET", "/v1/capabilities", authenticated=False)
        assert code in (401, 403), f"unauthenticated capabilities returned {code}"
        code, health = request("GET", "/v1/health")
        assert code == 200 and health.get("status") == "ok", "health failed"
        code, caps = request("GET", "/v1/capabilities")
        assert code == 200 and isinstance(caps.get("capabilities"), list), "capabilities failed"
        code, budget = request("GET", "/v1/budgets")
        assert code == 200 and budget.get("limitUsd") == 0, "nonzero/unknown paid budget"
        key = "e2e-" + uuid4().hex
        code, job = request("POST", "/v1/jobs", {"kind": "regression_scan", "params": {"e2e": True}, "maxCostUsd": 0}, extra={"Idempotency-Key": key})
        assert code in (200, 201) and isinstance(job.get("id"), str), f"job create returned {code}"
        job_id = job["id"]
        assert job_id.startswith("job-"), "unexpected job id"
        code, jobs = request("GET", "/v1/jobs")
        assert code == 200 and any(j.get("id") == job_id for j in jobs.get("jobs", [])), "created job not persisted"
        code, evidence = request("GET", "/v1/evidence")
        assert code == 200 and isinstance(evidence.get("evidence"), list), "evidence endpoint failed"
        print(json.dumps({"status": "PASS_API_GATE_ONLY", "job_id": job_id, "job_state": job.get("state"), "evidence_records": len(evidence["evidence"]), "note": "Does not prove browser-to-backend integration or independent evidence validity"}))
        return 0
    except (AssertionError, ValueError, KeyError, urllib.error.URLError, TimeoutError) as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
