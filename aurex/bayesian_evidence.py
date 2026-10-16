"""AUREX Bayesian evidence-fusion *analysis* (never an authority source).

Savant-like pattern discovery is represented as a hypothesis generator only.
Bayesian updates quantify uncertainty, not truth or authorization. Inputs must be
externally qualified; correlated witnesses share a cluster and count at most once.
No dependencies beyond the standard library.

CLI: python -m aurex.bayesian_evidence evidence.json
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FusionResult:
    hypothesis: str
    prior: float
    posterior: float
    log_odds: float
    qualified_witnesses: int
    independent_clusters: int
    rejected: tuple[str, ...]
    status: str = "ANALYSIS_ONLY_NOT_AUTHORITY"


def _probability(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} outside numeric limits") from exc
    if not math.isfinite(result) or not 0 < result < 1:
        raise ValueError(f"{name} must be strictly between 0 and 1")
    return result


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("observed_at must be an ISO timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid observed_at") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("observed_at requires timezone")
    return result.astimezone(UTC)


def fuse(payload: dict[str, Any], *, now: datetime | None = None) -> FusionResult:
    """Conservative, bounded Bayesian updates with explicit dependence control.

    Each accepted cluster contributes the *least favorable* qualified log LR,
    so adding correlated witnesses cannot amplify confidence. Calibration of
    likelihood ratios is external and must be independently reviewed.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    hypothesis = payload.get("hypothesis")
    if not isinstance(hypothesis, str) or not hypothesis.strip() or len(hypothesis) > 256:
        raise ValueError("hypothesis required")
    prior = _probability(payload.get("prior"), "prior")
    observations = payload.get("observations")
    if not isinstance(observations, list) or len(observations) > 1000:
        raise ValueError("observations must be a list of at most 1000")
    resolved_now = datetime.now(UTC) if now is None else now
    if (
        not isinstance(resolved_now, datetime) or resolved_now.tzinfo is None
        or resolved_now.utcoffset() is None
    ):
        raise ValueError("now must be a timezone-aware datetime")
    now = resolved_now.astimezone(UTC)
    clusters: dict[str, list[float]] = {}
    rejected: list[str] = []
    qualified = 0
    ids: set[str] = set()
    for i, item in enumerate(observations):
        if not isinstance(item, dict):
            raise ValueError("observation must be an object")
        identity = item.get("id")
        if (
            not isinstance(identity, str) or not identity.strip()
            or len(identity) > 128 or identity in ids
        ):
            raise ValueError("observation IDs must be unique nonempty strings")
        ids.add(identity)
        if item.get("qualification") != "PASS" or item.get("independent") is not True:
            rejected.append(f"{identity}:unqualified_or_self_witness")
            continue
        if item.get("status") != "OBSERVED":
            rejected.append(f"{identity}:not_observed")
            continue
        cluster = item.get("cluster")
        if not isinstance(cluster, str) or not cluster.strip() or len(cluster) > 128:
            rejected.append(f"{identity}:missing_independence_cluster")
            continue
        observed = _timestamp(item.get("observed_at"))
        age = (now - observed).total_seconds()
        if not 0 <= age <= 7 * 86400:
            rejected.append(f"{identity}:stale_or_future")
            continue
        # LR=P(observation|H)/P(observation|not H). Only externally
        # calibrated likelihoods qualify; cap effect of one cluster.
        if item.get("calibration") != "INDEPENDENTLY_VALIDATED":
            rejected.append(f"{identity}:uncalibrated")
            continue
        p_h = _probability(item.get("p_given_h"), "p_given_h")
        p_not_h = _probability(item.get("p_given_not_h"), "p_given_not_h")
        # Log differences remain finite for extreme positive subnormal inputs.
        log_lr = max(-math.log(10), min(math.log(10), math.log(p_h) - math.log(p_not_h)))
        clusters.setdefault(cluster, []).append(log_lr)
        qualified += 1
    log_odds = math.log(prior / (1 - prior))
    for values in clusters.values():
        # A cluster is one witness. Choose weakest support (or strongest
        # contradiction) to prevent evidence multiplication.
        log_odds += min(values)
    posterior = 1 / (1 + math.exp(-max(-700, min(700, log_odds))))
    return FusionResult(
        hypothesis=hypothesis,
        prior=prior,
        posterior=posterior,
        log_odds=log_odds,
        qualified_witnesses=qualified,
        independent_clusters=len(clusters),
        rejected=tuple(rejected),
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m aurex.bayesian_evidence evidence.json")
    source = Path(sys.argv[1])
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 512 * 1024:
        raise SystemExit("missing, linked or oversized input file")
    result = fuse(json.loads(source.read_text(encoding="utf-8")))
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
