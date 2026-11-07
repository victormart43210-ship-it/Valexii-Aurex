#!/usr/bin/env python3
"""Offline aggregate-only financial pilot scorecard; no uploads or API calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aurex.commercial.pilot_gate import evaluate_financial_pilots

MAX_INPUT_BYTES = 256 * 1024


def _dedupe(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local de-identified aggregate JSON")
    args = parser.parse_args()
    try:
        if args.input.is_symlink() or args.input.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("unsafe input path or oversized input")
        raw = args.input.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("oversized input")
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_dedupe,
            parse_constant=lambda _x: (_ for _ in ()).throw(ValueError("non-finite number")),
        )
        report = evaluate_financial_pilots(payload)
    except (OSError, ValueError, UnicodeError):
        report = evaluate_financial_pilots(None)
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    # This tool NEVER exits with production/release admission based on supplied input.
    raise SystemExit(2)


if __name__ == "__main__":
    main()
