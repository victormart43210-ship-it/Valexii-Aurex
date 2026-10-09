"""Authorized benchmark outcomes gate. This does not download or grade HLE."""

import hashlib
import json
from pathlib import Path
from typing import Any


class BenchmarkHold(ValueError):
    """Insufficient evidence for benchmark reporting."""


def assess_pair(manifest_file: Path, outcomes_file: Path) -> dict[str, Any]:
    raw = manifest_file.read_bytes()
    manifest = json.loads(raw)
    required = (
        "dataset_sha256",
        "dataset_revision",
        "item_ids",
        "baseline_model",
        "aurex_model",
        "judge_id",
        "evaluation_protocol_sha256",
    )
    if any(not manifest.get(k) for k in required):
        raise BenchmarkHold("Incomplete manifest")
    for flag in ("judge_independent", "contamination_checked", "dataset_authorized"):
        if manifest.get(flag) is not True:
            raise BenchmarkHold("Missing independent authorization or contamination control")
    for key in ("dataset_sha256", "evaluation_protocol_sha256"):
        value = manifest[key]
        if not isinstance(value, str) or len(value) != 64:
            raise BenchmarkHold("Missing SHA-256")
        try:
            bytes.fromhex(value)
        except ValueError as exc:
            raise BenchmarkHold("Invalid SHA-256") from exc
    ids = manifest["item_ids"]
    if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids):
        raise BenchmarkHold("Invalid or duplicate items")
    results = {}
    content = outcomes_file.read_bytes()
    for line in content.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = row["item_id"]
        if key in results or key not in ids:
            raise BenchmarkHold("Duplicate or unknown outcome")
        if (
            type(row.get("base_correct")) is not bool
            or type(row.get("governed_correct")) is not bool
        ):
            raise BenchmarkHold("Scores must be independently graded booleans")
        results[key] = row
    if set(results) != set(ids):
        raise BenchmarkHold("Incomplete paired outcomes")
    base = sum(r["base_correct"] for r in results.values())
    governed = sum(r["governed_correct"] for r in results.values())
    improved = sum(not r["base_correct"] and r["governed_correct"] for r in results.values())
    regressed = sum(r["base_correct"] and not r["governed_correct"] for r in results.values())
    n = len(ids)
    return {
        "status": "PAIRED_COUNTS_VALIDATED_NOT_HLE_CERTIFIED",
        "n": n,
        "base_correct": base,
        "governed_correct": governed,
        "percentage_point_delta": 100 * (governed - base) / n,
        "relative_uplift": (governed - base) / base if base else None,
        "improved_pairs": improved,
        "regressed_pairs": regressed,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "outcomes_sha256": hashlib.sha256(content).hexdigest(),
    }
