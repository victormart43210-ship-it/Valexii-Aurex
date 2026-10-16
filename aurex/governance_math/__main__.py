"""Read-only command-line entry point for Helsinki-inspired AUREX reasoning.

    python -m aurex.governance_math --input local-candidates.json

This NEVER runs a job, modifies a repository, spends money or talks to the
website. It does not validate caller-provided independent-witness assertions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from .calibration import Prediction, temporal_holdout
from .information_gain import Probe
from .optimization import FixStep
from .retrieval import Incident
from .spine import advise

MAX_INPUT_BYTES = 128 * 1024


def _objects(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("expected a list")
    if any(not isinstance(v, dict) for v in value):
        raise ValueError("each entry must be an object")
    return value


def _decimal(value: Any) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("monetary amounts must be decimal strings")
    return Decimal(value)


def _interpret(body: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(body, dict) or not isinstance(body.get("problem_code"), str):
        raise ValueError("problem_code required")
    if not isinstance(body.get("description"), str):
        raise ValueError("description required")
    incidents = [
        Incident(
            r["case_id"], r["description"], r["remedy_id"],
            r["evidence_sha256"], r["lineage_group"],
        )
        for r in _objects(body.get("incidents", []))
    ]
    fixes = [
        FixStep(
            r["key"], r["problem_code"], r["lineage_group"],
            tuple(r["fix"]), tuple(r["verify"]), tuple(r["rollback"]),
            r["minutes"], r["risk"], _decimal(r["cost_usd"]), r["impact"],
            tuple(r.get("requires", [])), tuple(r.get("conflicts", [])),
            r.get("reversible", True), r.get("historical_successes", 0),
            r.get("historical_failures", 0), r.get("independently_admitted_history", False),
        )
        for r in _objects(body.get("fixes", []))
    ]
    probes = [
        Probe(
            r["probe_id"], r["sensitivity"], r["specificity"],
            r["duration_seconds"], r["risk"], _decimal(r["cost_usd"]),
            r.get("calibration_reviewed", False),
        )
        for r in _objects(body.get("probes", []))
    ]
    result = advise(
        body["problem_code"], body["description"],
        incidents=incidents, fixes=fixes, probes=probes,
        prior=body.get("prior"),
    )
    response: dict[str, Any] = {
        "schema_version": 1, "kind": "AUREX_ADVISORY_NOT_EXECUTION",
        "advice": asdict(result),
        "independent_verification": "NOT VERIFIED",
        "effect_authority": "NONE",
    }
    # Optional retrospective evaluation; external signed qualification of
    # training/test labels is required before interpreting these diagnostics.
    if "predictions" in body:
        from datetime import datetime

        samples = [
            Prediction(
                row["case_id"], row["lineage_group"],
                datetime.fromisoformat(row["predicted_at"].replace("Z", "+00:00")),
                row["probability"], row["actual"],
            )
            for row in _objects(body["predictions"])
        ]
        cutoff_raw = body.get("holdout_cutoff")
        if not isinstance(cutoff_raw, str):
            raise ValueError("holdout_cutoff required when predictions supplied")
        cutoff = datetime.fromisoformat(cutoff_raw.replace("Z", "+00:00"))
        response["temporal_evaluation"] = asdict(temporal_holdout(samples, cutoff))
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="local bounded JSON evidence candidates")
    args = parser.parse_args()
    try:
        if not args.input.is_file() or args.input.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("missing or oversized local input")
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        result = _interpret(raw)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        # Do not echo untrusted input contents or disclose secrets.
        parser.error(f"invalid or unsafe input ({type(exc).__name__})")
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
