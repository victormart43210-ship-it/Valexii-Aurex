"""Zero-inference checks for AUREX NVIDIA website bridge. NEVER calls /v1/agent/ask.

Use `railway run ... python3 tools/aurex_nvidia_readiness_v7.py staging`
for private staging checks. Does not print service secrets or response contents.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, request

BASE = "https://aurex-api-aurex-staging.up.railway.app"
CAP = 65_536
PATHS = ("/v1/agent/status", "/v1/budgets")


class Hold(Exception):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _fetch(path: str, token: str = "") -> tuple[int, object]:
    if path not in ("/v1/health", *PATHS):
        raise Hold("path not allowlisted")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(BASE + path, headers=headers, method="GET")
    opener = request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=10) as response:
            if response.status != 200:
                return response.status, None
            raw = response.read(CAP + 1)
            if len(raw) > CAP:
                raise Hold("response too large")
            return 200, json.loads(raw.decode("utf-8"))
    except error.HTTPError as exc:
        return exc.code, None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Hold("transport or invalid response: " + type(exc).__name__) from None


def evaluate(anonymous: int, agent: object, budget: object) -> dict[str, object]:
    if not isinstance(agent, dict) or not isinstance(budget, dict):
        raise Hold("API response shape missing")
    if anonymous != 401:
        raise Hold("anonymous request was not denied with 401")
    if agent.get("authority") != "NONE" or agent.get("verification") != "NOT_VERIFIED":
        raise Hold("agent status authority or verification invalid")
    if any(not isinstance(budget.get(k), (float, int)) for k in ("limitUsd", "reservedUsd", "spentUsd")):
        raise Hold("budget numerical fields missing")
    budget_zero = all(budget[k] == 0 for k in ("limitUsd", "reservedUsd", "spentUsd"))
    if not budget_zero:
        raise Hold("budget not zero; do not automatically exercise inference")
    return {
        "status": "PASS", "scope": "STAGING_ZERO_INFERENCE_SNAPSHOT",
        "anonymousDenied": True,
        "provider": agent.get("modelProvider") if agent.get("modelProvider") in ("NVIDIA_NIM", "OPENAI", "UNSUPPORTED") else "UNKNOWN",
        "modelConfigured": agent.get("chatConfigured") is True,
        "providerConnection": "NOT_VERIFIED", "budgetUsd": 0,
        "modelWasCalled": False,
        "siteNvidiaLive": "NOT_VERIFIED",
        "authority": "NONE", "verification": "NOT_VERIFIED", "release": "HOLD",
    }


def local(root: Path) -> dict[str, object]:
    base = root / "integrations" / "kusanagi-xvi" / "backend"
    files = [base / name for name in ("llm.py", "app.py", "store.py")]
    if any(not p.is_file() or p.is_symlink() for p in files):
        raise Hold("missing expected backend source; no code changed")
    llm, app, store = (p.read_text(encoding="utf-8") for p in files)
    symbols = {
        "nvidiaFixedHost": "https://integrate.api.nvidia.com/v1/chat/completions" in llm,
        "nvidiaProviderConfigured": "AUREX_NVIDIA_API_KEY" in llm and "AUREX_NVIDIA_MODEL" in llm,
        "providerRequiresBillingFlags": "AUREX_LLM_ALLOW_BILLING" in llm and "AUREX_LLM_ENABLED" in llm,
        "apiExposesOwnerGatedAsk": '@app.post("/v1/agent/ask"' in app and "Depends(authorize)" in app,
        "durableRequestQuotaExists": "def reserve_llm_call(" in store,
    }
    if not all(symbols.values()):
        raise Hold("backend missing expected NVIDIA or governance component")
    return {"status": "PASS", "scope": "STATIC_SOURCE_ONLY", "checks": symbols,
            "providerConnection": "NOT_VERIFIED", "liveInference": "NOT_RUN",
            "websiteBridge": "DRAFT_NOT_DEPLOYED", "authority": "NONE", "release": "HOLD"}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if not args or args[0] not in ("offline", "staging") or len(args) > 2:
            raise Hold("usage: offline [repo] | staging")
        if args[0] == "offline":
            out = local(Path(args[1] if len(args) == 2 else "."))
        else:
            if len(args) != 1:
                raise Hold("staging accepts no additional arguments")
            if os.environ.get("RAILWAY_ENVIRONMENT_NAME") != "aurex-staging":
                raise Hold("staging-only environment required")
            token = os.environ.get("AUREX_SERVICE_TOKEN", "")
            if len(token) < 32:
                raise Hold("Railway service bearer missing or too short")
            anon_code, _ = _fetch("/v1/health")
            agent_code, agent = _fetch("/v1/agent/status", token)
            budget_code, budget = _fetch("/v1/budgets", token)
            if (agent_code, budget_code) != (200, 200):
                raise Hold("read-only API did not return HTTP 200")
            out = evaluate(anon_code, agent, budget)
        print(json.dumps(out, sort_keys=True))
        return 0
    except (Hold, OSError, ValueError) as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc) if isinstance(exc, Hold) else type(exc).__name__,
                          "authority": "NONE", "release": "HOLD"}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
