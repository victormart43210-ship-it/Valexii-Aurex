"""KUSANAGI XCV: offline Finland/India research smoke and optional local Qwen.

No downloads, weights, paid provider calls, public routes, or model authority.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from aurex.research_alignment import (
    filter_parallel_pairs,
    synthetic_baseline,
    synthetic_corpus,
    validate_synthetic_plan,
)
from workstation.qwen_readiness import check_local_qwen

OFFICIAL_OPUSFILTER_VERSION = "3.3.1"


def official_opusfilter_demo(*, executable: str | None = None) -> dict[str, object]:
    """Optional real OpusFilter 3.3.1 run on an *invented* four-pair dataset.

    Independently compare its output with the deterministic local filters.
    No model or data downloads; pip installs must be done separately by owner.
    """
    try:
        observed_version = version("opusfilter")
    except PackageNotFoundError:
        observed_version = None
    executable = executable if executable is not None else shutil.which("opusfilter")
    if observed_version != OFFICIAL_OPUSFILTER_VERSION or not executable:
        return {"status": "OPUSFILTER_NOT_INSTALLED_OR_VERSION_MISMATCH",
                "independent_verification": "NOT_VERIFIED", "authority": "NONE"}
    corpus = synthetic_corpus()[:4]
    expected, receipt = filter_parallel_pairs(corpus)
    with tempfile.TemporaryDirectory(prefix="aurex-xcv-") as directory:
        root = Path(directory)
        (root / "source.txt").write_text(
            "".join(source + "\n" for source, _ in corpus), encoding="utf-8"
        )
        (root / "target.txt").write_text(
            "".join(target + "\n" for _, target in corpus), encoding="utf-8"
        )
        # OpusFilter documentation supports YAML 'filter' steps with LengthFilter
        # and LengthRatioFilter; all paths are private temporary local files.
        config = (
            "common:\n"
            f"  workdir: {json.dumps(str(root))}\n"
            "steps:\n"
            "  - type: filter\n"
            "    parameters:\n"
            "      inputs: [source.txt, target.txt]\n"
            "      outputs: [source.filtered.txt, target.filtered.txt]\n"
            "      filters:\n"
            "        - LengthFilter:\n"
            "            unit: word\n"
            "            min_length: 1\n"
            "            max_length: 100\n"
            "        - LengthRatioFilter:\n"
            "            unit: word\n"
            "            threshold: 3\n"
        )
        (root / "config.yaml").write_text(config, encoding="utf-8")
        env = {k: v for k, v in os.environ.items()
               if k.lower() not in {"http_proxy", "https_proxy", "all_proxy"}}
        try:
            finished = subprocess.run(
                [executable, str(root / "config.yaml")],
                cwd=root, env=env, timeout=60, check=False,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if finished.returncode != 0:
                raise ValueError("OpusFilter failed")
            files = (root / "source.filtered.txt", root / "target.filtered.txt")
            if not all(f.is_file() and f.stat().st_size <= 16_384 for f in files):
                raise ValueError("filtered files missing or oversized")
            rows = [f.read_text(encoding="utf-8").splitlines() for f in files]
            actual = tuple(zip(rows[0], rows[1], strict=True))
            if actual != expected:
                raise ValueError("output does not match deterministic expectations")
        except (OSError, ValueError, subprocess.TimeoutExpired, UnicodeError):
            return {"status": "OPUSFILTER_DEMO_HOLD",
                    "independent_verification": "NOT_VERIFIED", "authority": "NONE"}
    return {
        "status": "SYNTHETIC_OPUSFILTER_3_3_1_OBSERVED_UNVERIFIED",
        "accepted_pairs": len(expected),
        "filtered_sha256": receipt.filtered_sha256,
        "independent_verification": "NOT_VERIFIED",
        "authority": "NONE",
    }


def evaluate_local_qwen(*, backend: str, model: str, port: int,
                        approved: bool, checker: Any = check_local_qwen,
                        runner: Any = None) -> dict[str, object]:
    """One explicit local-only synthetic planning observation, never a task."""
    if approved is not True:
        raise PermissionError("operator --approve-local required")
    _, corpus = filter_parallel_pairs(synthetic_corpus())
    ready = checker(backend=backend, model=model, port=port)
    if ready["status"] != "MODEL_ADVERTISED_UNVERIFIED":
        return {"status": "HOLD_MODEL_NOT_READY", "readiness": ready["status"],
                "authority": "NONE", "independent_verification": "NOT_VERIFIED"}
    if runner is None:
        from aurex.local_inference import run_local_inference
        runner = run_local_inference
    prompt = (
        "This is a synthetic, non-executable structure-only test. "
        "Return exactly one JSON object with key 'steps' and exactly three "
        "string values: inspect, test, review, in that order. No prose."
    )
    try:
        model_result = runner(
            prompt=prompt, model=model, base_url=f"http://127.0.0.1:{port}",
            backend=backend, approved=True, timeout_seconds=45.0,
        )
        plan = validate_synthetic_plan(model_result.text)
        status = "LOCAL_SYNTHETIC_PLAN_OBSERVED_UNVERIFIED" if plan.status == "STRUCTURE_MATCH_ONLY" else "HOLD_PLAN_REJECTED"
    except Exception:  # noqa: BLE001 - never expose raw model errors or private paths
        return {"status": "HOLD_LOCAL_INFERENCE_FAILED",
                "authority": "NONE", "independent_verification": "NOT_VERIFIED"}
    return {
        "status": status,
        "corpus_sha256": corpus.filtered_sha256,
        "plan_status": plan.status,
        "plan_reason": plan.reason,
        "response_sha256": plan.response_sha256,
        "model_output_chars": len(model_result.text),
        "independent_verification": "NOT_VERIFIED",
        "authority": "NONE",
        "external_spend_usd": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUREX XCV Finland/India synthetic Qwen study")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="offline deterministic baseline")
    action.add_argument("--opusfilter-demo", action="store_true", help="run installed pinned OpusFilter on synthetic data")
    action.add_argument("--infer", action="store_true", help="one explicitly approved local inference")
    parser.add_argument("--approve-local", action="store_true", help="required with --infer")
    parser.add_argument("--model")
    parser.add_argument("--backend", choices=("llama.cpp", "ollama"), default="llama.cpp")
    parser.add_argument("--port", type=int)
    args = parser.parse_args(argv)
    if args.infer:
        if not args.approve_local or not args.model:
            parser.error("--infer requires --approve-local and --model")
        port = args.port if args.port is not None else (11434 if args.backend == "ollama" else 8080)
        if not 1 <= port <= 65535:
            parser.error("invalid numeric localhost port")
        result = evaluate_local_qwen(backend=args.backend, model=args.model, port=port, approved=True)
    elif args.opusfilter_demo:
        result = official_opusfilter_demo()
    else:
        result = synthetic_baseline()
    print(json.dumps(result, sort_keys=True))
    if args.check:
        return 0
    return 0 if str(result["status"]).startswith(("SYNTHETIC_OPUSFILTER_", "LOCAL_SYNTHETIC_PLAN_")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
