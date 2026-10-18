"""Synthetic Helsinki/Delhi research alignment; no third-party runtime is bundled.

The deterministic filters are *inspired by* OpusFilter length/ratio concepts.
The plan checker is *inspired by* LRPlan's constraint-aware planning methodology.
Neither is the complete upstream implementation, a training run, or a model score.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Sequence

MAX_CORPUS_PAIRS = 100
MAX_CORPUS_BYTES = 64 * 1024
MAX_PLAN_BYTES = 8192
REQUIRED_PLAN = ("inspect", "test", "review")
POLICY_VERSION = "aurex-helsinki-delhi-synthetic-v1"


def _digest(value: object) -> str:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def synthetic_corpus() -> tuple[tuple[str, str], ...]:
    """Only invented samples, never proprietary records or training data."""
    return (
        ("Inspect a sample record", "Review the sample record"),
        ("Test the local service", "Validate the local service"),
        ("", "Empty source should not pass"),
        ("Review", "one two three four five six seven eight nine ten"),
        ("Inspect a sample record", "Review the sample record"),
    )


@dataclass(frozen=True)
class CorpusReceipt:
    status: str
    policy: str
    input_pairs: int
    accepted_pairs: int
    rejected_pairs: int
    source_sha256: str
    filtered_sha256: str
    reason_counts: dict[str, int]
    independent_verification: str = "NOT_VERIFIED"
    authority: str = "NONE"


@dataclass(frozen=True)
class PlanReceipt:
    status: str
    reason: str
    response_sha256: str
    expected_sequence_sha256: str
    independent_verification: str = "NOT_VERIFIED"
    authority: str = "NONE"


def filter_parallel_pairs(
    pairs: Sequence[tuple[str, str]],
    *,
    min_words: int = 1,
    max_words: int = 100,
    ratio_threshold: float = 3.0,
) -> tuple[tuple[tuple[str, str], ...], CorpusReceipt]:
    """Deterministic, bounded local analogue of two OpusFilter filters.

    No language identification, toxicity filtering, factual verification,
    multilingual validation, external network calls, or dataset acquisition.
    """
    if not 1 <= min_words <= max_words <= 100:
        raise ValueError("invalid length policy")
    if not 1.0 < ratio_threshold <= 10.0:
        raise ValueError("invalid ratio threshold")
    if isinstance(pairs, (str, bytes)) or not 0 < len(pairs) <= MAX_CORPUS_PAIRS:
        raise ValueError("empty, malformed or oversized corpus")
    canonical: list[tuple[str, str]] = []
    for pair in pairs:
        if (
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or not all(isinstance(item, str) for item in pair)
        ):
            raise ValueError("corpus pair must contain exactly two strings")
        canonical.append((pair[0], pair[1]))
    if len(json.dumps(canonical, ensure_ascii=False).encode("utf-8")) > MAX_CORPUS_BYTES:
        raise ValueError("corpus exceeds byte limit")
    accepted: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    reasons = {"empty": 0, "length": 0, "ratio": 0, "duplicate": 0, "control": 0}
    for left, right in canonical:
        a, b = left.strip(), right.strip()
        if not a or not b:
            reasons["empty"] += 1
            continue
        if any(ord(char) < 32 and char not in "\n\t" for char in a + b):
            reasons["control"] += 1
            continue
        n, m = len(a.split()), len(b.split())
        if not min_words <= n <= max_words or not min_words <= m <= max_words:
            reasons["length"] += 1
            continue
        # OpusFilter's documented threshold uses strict 'below', not <=.
        if max(n, m) / min(n, m) >= ratio_threshold:
            reasons["ratio"] += 1
            continue
        ident = (a, b)
        if ident in seen:
            reasons["duplicate"] += 1
            continue
        seen.add(ident)
        accepted.append(ident)
    result = tuple(accepted)
    receipt = CorpusReceipt(
        status="SYNTHETIC_FILTER_OBSERVED_UNVERIFIED" if result else "HOLD_EMPTY_FILTER",
        policy=POLICY_VERSION,
        input_pairs=len(canonical),
        accepted_pairs=len(result),
        rejected_pairs=len(canonical) - len(result),
        source_sha256=_digest(canonical),
        filtered_sha256=_digest(result),
        reason_counts=reasons,
    )
    return result, receipt


def validate_synthetic_plan(raw: str) -> PlanReceipt:
    """Accept exactly one closed-schema synthetic ordered plan, not an action."""
    if not isinstance(raw, str):
        raise ValueError("response must be text")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    reference = _digest({"steps": list(REQUIRED_PLAN)})
    status = "HOLD"
    reason = "INVALID_JSON"
    if not raw.strip() or len(raw.encode("utf-8")) > MAX_PLAN_BYTES:
        reason = "EMPTY_OR_OVERSIZED"
    else:
        try:
            obj = json.loads(raw)
        except (ValueError, TypeError):
            obj = None
        if isinstance(obj, dict) and set(obj) == {"steps"}:
            steps = obj["steps"]
            if (
                isinstance(steps, list)
                and len(steps) == len(REQUIRED_PLAN)
                and all(isinstance(step, str) for step in steps)
            ):
                if tuple(steps) == REQUIRED_PLAN:
                    status = "STRUCTURE_MATCH_ONLY"
                    reason = "SYNTHETIC_SEQUENCE_MATCH"
                else:
                    reason = "ORDER_OR_ACTION_MISMATCH"
            else:
                reason = "INVALID_STEPS"
        elif obj is not None:
            reason = "INVALID_SCHEMA"
    return PlanReceipt(
        status=status,
        reason=reason,
        response_sha256=digest,
        expected_sequence_sha256=reference,
    )


def synthetic_baseline() -> dict[str, object]:
    """Deterministic offline baseline; does not invoke a Qwen model."""
    _, corpus = filter_parallel_pairs(synthetic_corpus())
    plan = validate_synthetic_plan('{"steps":["inspect","test","review"]}')
    return {
        "kind": "SYNTHETIC_ONLY_NOT_MODEL_INFERENCE",
        "corpus": asdict(corpus),
        "plan": asdict(plan),
        "external_spend_usd": 0,
        "production_authority": "HOLD",
    }
