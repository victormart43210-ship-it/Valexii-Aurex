"""APIS PRIME: one bounded research request, one evidence-first reasoning spine.

Fourteen roles contribute to ONE consolidated report, not fourteen AI agents,
services, tabs, scientific verdicts, or authorization pathways.
"""
from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict
from typing import Any

from aurex.huruf_llull import (
    MAX_TEXT_BYTES,
    abjad_calculate,
    caesar_candidates,
    inspect_python,
    llull_wheel,
    profile_document,
)
from aurex.research_alignment import filter_parallel_pairs, validate_synthetic_plan

POLICY = "apis-prime-single-spine-v1"
NAMES = (
    "APIS-LEX", "KUKULKAN", "LYSIPHER", "SPECTRA", "SIFTRA",
    "ITZAMNAAJ", "ELNOESIS", "COATLICUE", "IACCHCODEX", "PROSOPHEX",
    "TEZCATLIPOCA", "XOLOTL", "ANTHOFORGE", "CRUCIBLE",
)
MAX_MODEL_DRAFT_CHARS = 600


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _node(number: int, status: str, observations: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": f"AP{number:02d}", "name": NAMES[number - 1], "status": status,
        "observations": observations or {}, "authority": "NONE",
        "independent_verification": "NOT_VERIFIED",
    }


def _statistics(text: str) -> dict[str, Any]:
    counts = Counter(text)
    size = len(text)
    entropy = -sum((count / size) * math.log2(count / size) for count in counts.values()) if size else 0.0
    letters = Counter(c.lower() for c in text if "a" <= c.lower() <= "z")
    return {
        "characters": size, "distinct_codepoints": len(counts),
        "shannon_entropy_bits_per_codepoint": round(entropy, 6),
        "top_ascii_letters": [
            {"letter": char, "count": n}
            for char, n in sorted(letters.items(), key=lambda item: (-item[1], item[0]))[:5]
        ],
        "limitation": "Descriptive frequencies, not a language, encryption or translation verdict",
    }


def _safe_call(number: int, action: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        result = action()
        if result["id"] != f"AP{number:02d}" or result["authority"] != "NONE":
            return _node(number, "HOLD_CONTRACT_VIOLATION")
        return result
    except Exception:  # noqa: BLE001 — no raw source/provider errors in output
        return _node(number, "HOLD_MODULE_FAILURE")


def unified_research(
    text: str, *, kind: str = "document",
    parallel_pairs: Sequence[tuple[str, str]] | None = None,
    plan_json: str | None = None,
    local_model_approved: bool = False,
    local_model: str | None = None,
    local_backend: str = "ollama",
    local_port: int = 11434,
    model_runner: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Fan in bounded analyses to one HOLD-governed, single-panel research report.

    Analyses run as one synchronous deterministic DAG; a model runs only by
    explicit opt-in, against aggregated stats (never the source itself).
    Missing capabilities are reported as unavailable, not simulated.
    """
    if type(text) is not str or "\x00" in text or any(0xD800 <= ord(c) <= 0xDFFF for c in text) or len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("plain UTF-8 text up to 64KiB only; binary rejected")
    if kind not in {"document", "python"}:
        raise ValueError("kind must be document or python")
    if type(local_model_approved) is not bool:
        raise ValueError("local model approval must be a boolean")
    if local_model_approved and (
        not local_model or type(local_port) is not int or not 1 <= local_port <= 65535
        or local_backend not in {"ollama", "llama.cpp"}
    ):
        raise ValueError("approved local model needs a model, backend and valid loopback port")

    digest = _digest(text)
    stats = _statistics(text)
    analyses: list[dict[str, Any]] = []
    # Run the shared structural analysis just once for the manuscript/anomaly lanes.
    profile_cache: dict[str, Any] | None = None

    def document_profile() -> dict[str, Any]:
        nonlocal profile_cache
        if profile_cache is None:
            profile_cache = profile_document(text)
        return profile_cache

    # Evidence acquisition: only methods applicable to the admitted input run.
    def apis() -> dict[str, Any]:
        if not any("\u0600" <= c <= "\u06ff" for c in text):
            return _node(1, "NOT_APPLICABLE_NO_ARABIC_SCRIPT")
        value = abjad_calculate(text)
        return _node(1, value["status"], value["analysis"])
    analyses.append(_safe_call(1, apis))

    def kukulkan() -> dict[str, Any]:
        wheel = llull_wheel()
        return _node(2, "EXPLORATORY_COMBINATIONS_ONLY", {
            "figure": wheel["figure"], "combination_count": len(wheel["combinations"]),
            "historical_link": "NOT_ESTABLISHED",
        })
    analyses.append(_safe_call(2, kukulkan))

    def lysipher() -> dict[str, Any]:
        guesses = caesar_candidates(text)
        return _node(3, "CANDIDATES_NOT_DECIPHERMENT", {
            "method": guesses["analysis"]["method"],
            "candidates_explored": len(guesses["analysis"]["candidates"]),
            "selected_plaintext": None,
        })
    analyses.append(_safe_call(3, lysipher))

    analyses.append(_node(4, "DESCRIPTIVE_STATISTICS_ONLY", stats))

    def siftra() -> dict[str, Any]:
        if parallel_pairs is None:
            return _node(5, "LOCAL_INPUT_ADMISSION_ONLY", {
                "bytes": len(text.encode("utf-8")),
                "source_sha256": digest, "opusfilter": "NOT_RUN_NO_PARALLEL_CORPUS",
            })
        _, receipt = filter_parallel_pairs(parallel_pairs)
        return _node(5, "SYNTHETIC_FILTER_ANALOGUE_ONLY", asdict(receipt))
    analyses.append(_safe_call(5, siftra))

    def itzamnaaj() -> dict[str, Any]:
        if plan_json is None:
            return _node(6, "PLAN_INPUT_NOT_SUPPLIED", {
                "expected_synthetic_steps": ["inspect", "test", "review"]
            })
        receipt = validate_synthetic_plan(plan_json)
        return _node(6, "SYNTHETIC_PLAN_CHECK_ONLY" if receipt.status == "STRUCTURE_MATCH_ONLY" else "HOLD_PLAN_CHECK", asdict(receipt))
    analyses.append(_safe_call(6, itzamnaaj))

    def elnoesis() -> dict[str, Any]:
        if not local_model_approved:
            return _node(7, "NOT_RUN_NO_MODEL_APPROVAL")
        # Deliberately exclude user source, source filename and raw cipher candidates.
        prompt = (
            "Given ONLY these bounded statistics, suggest one falsifiable next "
            "research test. Do not claim decipherment, validity or authority. "
            f"Input kind: {kind}; count: {stats['characters']}; "
            f"distinct codepoints: {stats['distinct_codepoints']}; "
            f"entropy: {stats['shannon_entropy_bits_per_codepoint']}."
        )
        if model_runner is None:
            from aurex.local_inference import run_local_inference
            runner = run_local_inference
        else:
            runner = model_runner
        result = runner(
            prompt=prompt, model=local_model,
            base_url=f"http://127.0.0.1:{local_port}",
            backend=local_backend, approved=True, timeout_seconds=30.0,
        )
        if not isinstance(result.text, str) or result.authority_granted or result.verified:
            return _node(7, "HOLD_UNTRUSTED_MODEL_CONTRACT")
        return _node(7, "LOCAL_MODEL_DRAFT_UNVERIFIED", {
            "draft": result.text[:MAX_MODEL_DRAFT_CHARS],
            "response_sha256": _digest(result.text),
            "scope": "AGGREGATE_STATISTICS_ONLY_SOURCE_NOT_SENT",
        })
    analyses.append(_safe_call(7, elnoesis))

    analyses.append(_node(8, "NOT_RUN_NO_VISUAL_CORPUS", {
        "reason": "Prehistoric imagery requires sourced images and an independently reviewed visual method"
    }))

    def iacchcodex() -> dict[str, Any]:
        profile = document_profile()
        a = profile["analysis"]
        return _node(9, "STRUCTURAL_PROFILE_ONLY", {
            "token_count": a["token_count"], "unique_tokens": a["unique_tokens"],
            "suffix_width": a["suffix_width"],
            "common_suffixes": a["common_suffixes"],
            "reading_order": a["reading_order"],
        })
    analyses.append(_safe_call(9, iacchcodex))

    def prosophex() -> dict[str, Any]:
        if kind != "python":
            return _node(10, "NOT_APPLICABLE_NOT_PYTHON")
        a = inspect_python(text)
        return _node(10, a["status"], a["analysis"])
    analyses.append(_safe_call(10, prosophex))

    # Challenge: these are internal bounded controls, NOT independent witnesses.
    def tezcatlipoca() -> dict[str, Any]:
        profile = document_profile()
        a = profile["analysis"]
        return _node(11, "EXPLORATORY_BASELINE_ONLY", {
            "observed_suffix_fraction": a["observed_top_suffix_fraction"],
            "one_shuffled_null_fraction": a["single_shuffled_null_fraction"],
            "significance": "NOT_ESTABLISHED_ONE_NULL_SAMPLE",
        })
    analyses.append(_safe_call(11, tezcatlipoca))

    analyses.append(_node(12, "HOLD_INDEPENDENT_WITNESS_REQUIRED", {
        "next": "External negative controls, held-out predictions, independent reviewer"
    }))
    analyses.append(_node(13, "TEST_IDEAS_ONLY", {
        "suggested_research_sequence": ["specify claim", "collect controls", "test held-out corpus", "independent review"],
        "prototype_executed": False,
    }))

    check = (
        len(analyses) == 13
        and all(item["id"] == f"AP{i:02d}" for i, item in enumerate(analyses, 1))
        and all(item["authority"] == "NONE" for item in analyses)
        and all(item["independent_verification"] == "NOT_VERIFIED" for item in analyses)
    )
    analyses.append(_node(14, "INTERNAL_BOUNDARY_CHECK_ONLY" if check else "HOLD_BOUNDARY_FAILURE", {
        "no_action_authority": check,
        "external_independent_red_team": "NOT_RUN",
        "source_code_executed": False,
    }))
    if not check:
        for item in analyses:
            if item["authority"] != "NONE":
                item["authority"] = "NONE"
        outcome = "HOLD_CONTRACT_VIOLATION"
    else:
        outcome = "HOLD_INDEPENDENT_EVIDENCE_REQUIRED"
    problem_count = sum(item["status"].startswith("HOLD") for item in analyses)
    return {
        "kind": "APIS_PRIME_UNIFIED_RESEARCH", "policy": POLICY,
        "source_sha256": digest, "source_kind": kind, "spine_status": outcome,
        "authority": "NONE", "independent_verification": "NOT_VERIFIED",
        "external_spend_usd": 0, "decipherment": "NOT_ESTABLISHED",
        "one_view": {
            "title": "APIS PRIME · REASONING SPINE", "tabs_added": 0,
            "now": "Research diagnostics assembled; conclusions remain unverified",
            "changed": "NOT_COMPUTED_NO_PRIOR_COMPARISON",
            "next": "Collect independent controls and review before claiming a finding",
            "why": "14 bounded roles converge through one evidence-first orchestration call",
            "proof": {"source_sha256": digest, "contributors": 14,
                      "modules_requiring_attention": problem_count,
                      "independent_verification": "NOT_VERIFIED"},
        },
        "contributions": analyses,
    }
