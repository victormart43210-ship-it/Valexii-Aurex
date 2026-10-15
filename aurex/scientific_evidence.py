"""Bounded, reproducible, offline evaluation primitives inspired by REANA and Inspect AI.

This module does not execute arbitrary code, call models, or grant job authority.
Unsigned statements are NOT cryptographic attestations.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    """Stable serialization; reject NaN and non-JSON objects."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    request: str
    expected: str


def evaluate_exact(cases: list[EvaluationCase], outputs: dict[str, str]) -> dict[str, Any]:
    """Inspect-inspired independent, deterministic scorer. Missing output is UNKNOWN, never PASS."""
    if not cases or len(cases) > 1000:
        raise ValueError("Evaluation requires 1..1000 cases")
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids) or any(not case_id for case_id in ids):
        raise ValueError("Case IDs must be nonempty and unique")
    if set(outputs) - set(ids):
        raise ValueError("Unexpected output case IDs")
    results: list[dict[str, str]] = []
    for case in cases:
        actual = outputs.get(case.case_id)
        outcome = "UNKNOWN" if actual is None else ("PASS" if actual == case.expected else "FAIL")
        results.append({"case_id": case.case_id, "outcome": outcome})
    counts = {state: sum(r["outcome"] == state for r in results) for state in ("PASS", "FAIL", "UNKNOWN")}
    return {"results": results, "counts": counts, "complete": counts["UNKNOWN"] == 0,
            "passed": counts["PASS"] == len(cases), "digest_sha256": digest(results)}


def execution_manifest(*, source_sha: str, environment_digest: str,
                       inputs: dict[str, Any], outputs: dict[str, Any],
                       evaluation: dict[str, Any]) -> dict[str, Any]:
    """REANA-inspired reproducibility manifest; does not claim execution verification."""
    if len(source_sha) != 40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("Full lowercase git commit SHA required")
    if len(environment_digest) != 64 or any(c not in "0123456789abcdef" for c in environment_digest):
        raise ValueError("SHA-256 environment digest required")
    if not isinstance(evaluation.get("passed"), bool):
        raise ValueError("Explicit evaluation result required")
    return {"schema": "aurex.reproducibility.v1", "source_sha": source_sha,
            "environment_sha256": environment_digest,
            "inputs_sha256": digest(inputs), "outputs_sha256": digest(outputs),
            "evaluation_sha256": digest(evaluation),
            "qualification": "UNVERIFIED", "authority": "NONE"}


def unsigned_statement(manifest: dict[str, Any]) -> dict[str, Any]:
    """in-toto Statement-shaped export. Explicitly UNSIGNED, never evidence of independent trust."""
    return {"_type": "https://in-toto.io/Statement/v1",
            "subject": [{"name": "aurex-execution-manifest",
                         "digest": {"sha256": digest(manifest)}}],
            "predicateType": "https://valexii.ai/attestations/reproducibility/v1",
            "predicate": manifest}


def verify_manifest(manifest: dict[str, Any], *, source_sha: str,
                    environment_digest: str, inputs: dict[str, Any],
                    outputs: dict[str, Any], evaluation: dict[str, Any]) -> bool:
    """Independent recomputation of content bindings; no trust or signature assertion."""
    try:
        expected = execution_manifest(source_sha=source_sha,
                                      environment_digest=environment_digest,
                                      inputs=inputs, outputs=outputs, evaluation=evaluation)
        return manifest == expected
    except (TypeError, ValueError):
        return False
