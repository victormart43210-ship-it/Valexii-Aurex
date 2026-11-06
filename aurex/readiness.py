"""Evidence-weighted AUREX/OX readiness calculator; no self-attestation.

Input is independent review data, not runtime self-reported metrics. Unknown never scores.
Run: python -m aurex.readiness evidence.json
JSON schema: {"checks":[{"id":"...","status":"PASS","source":"independent reviewer / exact SHA","observed_at":"2026-10-16T00:00:00+00:00"}]}
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Frozen acceptance criteria: changing weights requires independent review.
WEIGHTS: dict[str, int] = {
    "canonical_source": 10,
    "exact_sha_ci": 10,
    "api_contract": 12,
    "backend_auth": 10,
    "worker_fencing": 10,
    "durable_storage": 10,
    "frontend_proxy": 10,
    "end_to_end_proof": 14,
    "recovery_rollback": 8,
    "observability": 6,
}
CRITICAL = frozenset({"canonical_source", "backend_auth", "durable_storage", "end_to_end_proof"})
assert sum(WEIGHTS.values()) == 100


@dataclass(frozen=True)
class Result:
    score: int
    maximum_possible: int
    verified_checks: int
    total_checks: int
    eligible_for_90: bool
    authority: str
    missing: tuple[str, ...]


def evaluate(data: dict[str, Any], *, now: datetime | None = None) -> Result:
    """Independent evidence required; malformed, stale or conflicting evidence fails closed."""
    now = now or datetime.now(timezone.utc)
    entries = data.get("checks")
    if not isinstance(entries, list):
        raise ValueError("checks must be a list")
    seen: dict[str, bool] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("check must be an object")
        key = item.get("id")
        if key not in WEIGHTS or key in seen:
            raise ValueError("unknown or duplicate check")
        status = item.get("status")
        if status not in ("PASS", "FAIL", "NOT RUN", "NOT VERIFIED"):
            raise ValueError("invalid check status")
        valid = False
        if status == "PASS":
            source = item.get("source")
            stamp = item.get("observed_at")
            if not isinstance(source, str) or not source.strip() or not isinstance(stamp, str):
                raise ValueError("PASS requires independent source and observed_at")
            try:
                observed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("invalid observed_at") from exc
            if observed.tzinfo is None:
                raise ValueError("observed_at requires timezone")
            age = (now - observed).total_seconds()
            valid = 0 <= age <= 7 * 86400 and item.get("independent") is True
        seen[key] = valid
    score = sum(weight for key, weight in WEIGHTS.items() if seen.get(key, False))
    missing = tuple(key for key in WEIGHTS if not seen.get(key, False))
    critical_ok = all(seen.get(key, False) for key in CRITICAL)
    # Score is a *verified acceptance coverage* metric, NOT a delivery-performance benchmark.
    eligible = score >= 90 and critical_ok
    return Result(score, 100, sum(seen.values()), len(WEIGHTS), eligible,
                  "CANDIDATE_REVIEW_ONLY" if eligible else "HOLD", missing)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m aurex.readiness evidence.json")
    result = evaluate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
