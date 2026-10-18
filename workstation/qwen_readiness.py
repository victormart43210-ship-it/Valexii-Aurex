"""Bounded local-only Qwen readiness and explicitly approved synthetic smoke.

This is a local CLI, not a web route. A model being listed does not prove
inference works, and an observed inference does not grant security authority.
No model download, paid provider, remote endpoint, or auto-execution.
"""
from __future__ import annotations

import argparse
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_MODEL_LIST_BYTES = 65_536
_MODEL = re.compile(r"^[^\r\n\x00]{1,200}$")
_BACKEND_PATH = {"llama.cpp": "/v1/models", "ollama": "/api/tags"}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


def _validate(backend: str, model: str, port: int) -> None:
    if backend not in _BACKEND_PATH:
        raise ValueError("unsupported local backend")
    if not isinstance(model, str) or not _MODEL.fullmatch(model) or model != model.strip():
        raise ValueError("invalid model identifier")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("invalid local port")


def check_local_qwen(*, backend: str, model: str, port: int,
                     opener: Any | None = None) -> dict[str, object]:
    """Check only numeric loopback model LIST, never inference or a raw model path."""
    _validate(backend, model, port)
    # Bypass HTTP(S)_PROXY environment variables, even on a hostile host.
    client = opener if opener is not None else build_opener(ProxyHandler({}), _NoRedirect())
    request = Request(f"http://127.0.0.1:{port}{_BACKEND_PATH[backend]}", method="GET")
    status = "SERVER_UNAVAILABLE"
    models_listed = 0
    try:
        with client.open(request, timeout=3) as response:
            if response.status != 200:
                raise ValueError("unexpected HTTP status")
            raw = response.read(MAX_MODEL_LIST_BYTES + 1)
        if len(raw) > MAX_MODEL_LIST_BYTES:
            raise ValueError("oversized model list")
        data = json.loads(raw.decode("utf-8", errors="strict"))
        items = data["data"] if backend == "llama.cpp" else data["models"]
        if not isinstance(items, list) or len(items) > 100:
            raise ValueError("invalid model list")
        field = "id" if backend == "llama.cpp" else "name"
        names = [item[field] for item in items if isinstance(item, dict)
                 and isinstance(item.get(field), str)]
        if len(names) != len(items):
            raise ValueError("invalid model entry")
        models_listed = len(names)
        status = "MODEL_ADVERTISED_UNVERIFIED" if model in names else "MODEL_NOT_LISTED"
    except (HTTPError, URLError, TimeoutError, OSError):
        status = "SERVER_UNAVAILABLE"
    except (UnicodeError, ValueError, KeyError, TypeError, AttributeError):
        status = "INVALID_MODEL_LIST"
    return {
        "backend": backend,
        "status": status,
        "models_listed": models_listed,
        "inference": "NOT_RUN",
        "independent_verification": "NOT_VERIFIED",
        "authority": "NONE",
        "external_spend_usd": 0,
    }


def synthetic_smoke(*, backend: str, model: str, port: int, approved: bool,
                    opener: Any | None = None, runner: Any | None = None) -> dict[str, object]:
    """Only explicitly approved operator-invoked local synthetic inference."""
    if approved is not True:
        raise PermissionError("explicit --approve-local required")
    readiness = check_local_qwen(backend=backend, model=model, port=port, opener=opener)
    if readiness["status"] != "MODEL_ADVERTISED_UNVERIFIED":
        return readiness
    if runner is None:
        from aurex.local_inference import run_local_inference
        runner = run_local_inference
    try:
        result = runner(
            prompt="Synthetic AUREX local test. Reply with one short word: READY.",
            model=model, base_url=f"http://127.0.0.1:{port}", backend=backend,
            approved=True, timeout_seconds=45.0,
        )
        if not isinstance(result.text, str) or not result.text.strip():
            raise ValueError("empty model response")
        return {
            **readiness,
            "status": "LOCAL_INFERENCE_OBSERVED_UNVERIFIED",
            "inference": "OBSERVED_UNVERIFIED",
            "answer_sha256": result.sha256,
            "answer_characters": len(result.text),
        }
    except Exception:  # noqa: BLE001 - intentionally sanitize local server errors
        return {**readiness, "status": "LOCAL_INFERENCE_FAILED", "inference": "FAILED"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX local-only Qwen model readiness")
    parser.add_argument("--backend", choices=tuple(_BACKEND_PATH), default="llama.cpp")
    parser.add_argument("--model", required=True, help="exact identifier from local model server")
    parser.add_argument("--port", type=int, default=None)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="GET local model list only")
    mode.add_argument("--infer", action="store_true", help="run one synthetic local inference")
    parser.add_argument("--approve-local", action="store_true", help="required for --infer")
    args = parser.parse_args(argv)
    if args.infer and not args.approve_local:
        parser.error("--infer also requires --approve-local")
    port = args.port if args.port is not None else (11434 if args.backend == "ollama" else 8080)
    try:
        if args.infer:
            report = synthetic_smoke(backend=args.backend, model=args.model, port=port,
                                     approved=args.approve_local)
        else:
            report = check_local_qwen(backend=args.backend, model=args.model, port=port)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] in ("MODEL_ADVERTISED_UNVERIFIED",
                                      "LOCAL_INFERENCE_OBSERVED_UNVERIFIED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
