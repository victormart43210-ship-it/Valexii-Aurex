"""Offline entry point: feed fictional source cases to the AUREX rule engine.

Not for customer data. Outputs must be checked by an independent evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from aurex.field_reconciliation import reconcile_field_cases

INPUT_SCHEMA = "aurex.field-audit-beta.cases.v1"
OUTPUT_SCHEMA = "aurex.field-audit-beta.results.v1"
MAX_BYTES = 128 * 1024


def candidate_from_suite(data: dict[str, Any]) -> dict[str, Any]:
    if (type(data) is not dict or set(data) != {"schema", "synthetic", "cases", "suite_sha256"}
            or data["schema"] != INPUT_SCHEMA or data["synthetic"] is not True
            or type(data["suite_sha256"]) is not str):
        raise ValueError("invalid synthetic suite header")
    canonical = {k: data[k] for k in ("schema", "synthetic", "cases")}
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    if digest != data["suite_sha256"]:
        raise ValueError("suite digest mismatch")
    rows = reconcile_field_cases(data["cases"])
    return {"schema": OUTPUT_SCHEMA, "synthetic": True, "suite_sha256": digest,
            "results": [{**r, "authority": "HOLD", "independent_verification": "NOT_VERIFIED",
                         "effect": "NONE"} for r in rows]}


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate JSON field")
        out[k] = v
    return out


def _no_constant(_s: str) -> None:
    raise ValueError("nonfinite JSON constant")


def read_suite(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("invalid source file")
    try:
        result = json.loads(path.read_bytes().decode("utf-8", errors="strict"),
                            object_pairs_hook=_unique, parse_constant=_no_constant)
    except (ValueError, UnicodeError) as e:
        raise ValueError("invalid source JSON") from e
    if type(result) is not dict:
        raise ValueError("source JSON must be an object")
    return result


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description="Offline synthetic AUREX field audit candidate, $0, HOLD")
    cli.add_argument("--cases", required=True, type=Path)
    args = cli.parse_args(argv)
    try:
        output = candidate_from_suite(read_suite(args.cases))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc), "effect": "NONE"}))
        return 2
    print(json.dumps(output, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
