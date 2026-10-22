"""AUREX XXV read-only staging / website / repository release probes.

No user-configurable outbound hosts, credentials in logs, autonomous actions,
paid models, production changes, or positive security authority.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

STAGING = "https://aurex-api-aurex-staging.up.railway.app"
WEBSITE = "https://valexii.com/aurex/ox"
PINNED_COMMIT = "d22e06e9412a07e06ab8bd597e0e5ebf5b8c125c"
PINNED_BRANCH = "work/kusanagi-xxiv-cxxviii-convergence"
MAX_REPLY = 65536
GET_PATHS = ("/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs", "/v1/agent/status")

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _json_bytes(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def emit(result: dict[str, Any]) -> int:
    clean = {**result, "authority": "NONE", "release": "HOLD"}
    print(json.dumps(clean, indent=2, sort_keys=True))
    return 0 if clean.get("status") == "PASS" else 2


def _open(url: str, token: str | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, method="GET", headers={
        "Accept": "application/json" if token else "text/html,application/json",
        "User-Agent": "AUREX-XXV-StagingProbe/1.0",
        **({"Authorization": "Bearer " + token} if token else {}),
    })
    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=10) as res:
            if int(res.headers.get("Content-Length") or "0") > MAX_REPLY:
                raise ValueError("response too large")
            data = res.read(MAX_REPLY + 1)
            if len(data) > MAX_REPLY:
                raise ValueError("response too large")
            return res.status, data
    except urllib.error.HTTPError as ex:
        # Never read or reflect upstream error bodies / headers; no redirect follows.
        return ex.code, b""


def stage_readonly() -> dict[str, Any]:
    """Read-only authenticated staging smoke. Does not prove 24/7 uptime."""
    token = os.environ.get("AUREX_SERVICE_TOKEN", "")
    if len(token) < 32 or '\n' in token or '\r' in token:
        return {"status": "HOLD", "reason": "STAGING_TOKEN_NOT_AVAILABLE", "checks": {}}
    checks: dict[str, Any] = {}
    try:
        # Confirm ingress denies anonymous callers; exact expected code is 401.
        status, _ = _open(STAGING + "/v1/health")
        checks["anonymousDenied"] = status == 401
        if status != 401:
            return {"status": "FAIL", "reason": "ANONYMOUS_NOT_REJECTED_AS_EXPECTED", "checks": checks}
        for path in GET_PATHS:
            code, payload = _open(STAGING + path, token)
            if code != 200:
                checks[path] = {"httpStatus": code, "valid": False}
                return {"status": "FAIL", "reason": "AUTHENTICATED_ENDPOINT_FAILURE", "checks": checks}
            try:
                obj = json.loads(payload.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return {"status": "FAIL", "reason": "MALFORMED_JSON", "checks": checks}
            if not isinstance(obj, dict):
                return {"status": "FAIL", "reason": "UNEXPECTED_SCHEMA", "checks": checks}
            okay = (path != "/v1/health" or obj.get("status") == "ok")
            if path == "/v1/budgets":
                okay &= obj.get("limitUsd") == 0 and obj.get("spentUsd") == 0
            if path == "/v1/agent/status":
                okay &= obj.get("chatConfigured") is False
            checks[path] = {"httpStatus": code, "valid": bool(okay)}
            if not okay:
                return {"status": "FAIL", "reason": "RELEASE_GATE_NOT_MET", "checks": checks}
        return {"status": "PASS", "scope": "STAGING_READ_ONLY_SNAPSHOT", "checks": checks,
                "persistenceAcrossRestart": "NOT_VERIFIED", "continuousReliability": "NOT_VERIFIED",
                "modelInference": "NOT_RUN", "independentEfficacy": "NOT_VERIFIED"}
    except (OSError, ValueError) as exc:
        return {"status": "FAIL", "reason": "TRANSPORT_OR_SIZE_ERROR", "errorType": type(exc).__name__, "checks": checks}


def website_readonly() -> dict[str, Any]:
    """Static first-response smoke; not Lighthouse, SSR proof, or user journey QA."""
    start = time.monotonic()
    try:
        code, html = _open(WEBSITE)
        ms = round((time.monotonic() - start) * 1000)
        if code != 200:
            return {"status": "FAIL", "httpStatus": code, "reason": "WEBSITE_HTTP_NOT_200"}
        content = html.lower()
        present = (b"aurex" in content)
        return {"status": "PASS" if present else "FAIL", "scope": "PUBLIC_HTML_SNAPSHOT",
                "httpStatus": code, "sampleResponseMs": ms, "bodyBytes": len(html),
                "aurexMarkerPresent": present, "javascriptRenderedUI": "NOT_VERIFIED",
                "frontendSecurity": "NOT_VERIFIED", "coreWebVitals": "NOT_MEASURED"}
    except (OSError, ValueError) as exc:
        return {"status": "FAIL", "reason": "WEBSITE_TRANSPORT_ERROR", "errorType": type(exc).__name__}


def repo_readonly(repo: Path) -> dict[str, Any]:
    """Verify Git exact head and clean worktree; no fetch/merge/push."""
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True,
                                       stderr=subprocess.DEVNULL, timeout=12).strip()
    try:
        branch = git("branch", "--show-current")
        sha = git("rev-parse", "HEAD")
        changed = git("status", "--porcelain")
    except (OSError, subprocess.SubprocessError):
        return {"status": "FAIL", "reason": "GIT_UNAVAILABLE_OR_INVALID_WORKTREE"}
    ok = sha == PINNED_COMMIT and branch == PINNED_BRANCH and not changed
    expected = ("integrations/kusanagi-xvi/backend/boot.py",
                "integrations/kusanagi-xvi/backend/evidence_science.py",
                "integrations/kusanagi-xvi/backend/evaluation_science.py",
                "integrations/kusanagi-xvi/backend/nvidia_research.py")
    files_ok = all((repo / p).is_file() and not (repo / p).is_symlink() for p in expected)
    return {"status": "PASS" if ok and files_ok else "HOLD",
            "expectedCommit": PINNED_COMMIT, "actualCommit": sha,
            "branchMatches": branch == PINNED_BRANCH, "cleanWorktree": not bool(changed),
            "requiredFilesPresent": files_ok, "CI": "CHECK_EXACT_HEAD_EXTERNALLY"}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="cmd", required=True)
    rp = subs.add_parser("repo", help="Read-only exact Git SHA gate")
    rp.add_argument("--target", type=Path, required=True)
    subs.add_parser("staging", help="Read-only authenticated staging API probe")
    subs.add_parser("website", help="Public static website response smoke")
    args = p.parse_args(argv)
    if args.cmd == "repo":
        return emit(repo_readonly(args.target))
    if args.cmd == "staging":
        return emit(stage_readonly())
    return emit(website_readonly())

if __name__ == "__main__":
    raise SystemExit(main())
