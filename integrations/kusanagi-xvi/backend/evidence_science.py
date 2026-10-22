"""Bounded, deterministic AUREX discrepancy triage. NOT a security verdict.

Concepts: hypothesis testing, source independence, provenance fingerprints,
freshness, and conservative abstention. Source metadata is operator-supplied
and is NOT independently attested here: no positive security authority ever.
No API/model calls, filesystem access, network calls, or mutable global state.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime, timedelta
from typing import Any

HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
STANCES = frozenset({"SUPPORT", "CONTRADICT"})
MAX_EVIDENCE = 16
MAX_AGE_DAYS = 30


def _stamp(raw: Any) -> datetime:
    if not isinstance(raw, str) or len(raw) > 40:
        raise ValueError("timestamp required")
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timezone required")
    return dt.astimezone(UTC)


def assess_claim(payload: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Deduplicate correlated witnesses, detect contradictions and HOLD.

    Families are unverified claims of organizational independence. sha256 is
    a claimed document fingerprint, not proof that content was inspected.
    Never emits CLEAR/PASS or proof of independent verification.
    """
    if not isinstance(payload, dict) or set(payload) != {"claimId", "evidence"}:
        raise ValueError("claimId and evidence only")
    claim_id = payload["claimId"]
    items = payload["evidence"]
    if not isinstance(claim_id, str) or not ID.fullmatch(claim_id):
        raise ValueError("invalid claimId")
    if not isinstance(items, list) or len(items) > MAX_EVIDENCE:
        raise ValueError("evidence must be a list of at most 16 items")
    when = now or datetime.now(UTC)
    if when.tzinfo is None:
        raise ValueError("aware now required")
    when = when.astimezone(UTC)

    # A group is at most one unverified organizational witness. Conflicting
    # assertions *within* one family trigger conflict but not corroboration.
    families: dict[str, set[str]] = {}
    fingerprints: dict[str, str] = {}
    seen_ids: set[str] = set()
    excluded = {"stale": 0, "future": 0, "malformed": 0, "duplicateDigest": 0}
    for e in items:
        if not isinstance(e, dict) or set(e) != {"sourceId", "family", "stance", "capturedAt", "sha256"}:
            raise ValueError("invalid evidence shape")
        sid, family, stance, digest = (e[x] for x in ("sourceId", "family", "stance", "sha256"))
        if not all(isinstance(v, str) for v in (sid, family, stance, digest)):
            raise ValueError("invalid evidence type")
        if not ID.fullmatch(sid) or not ID.fullmatch(family) or stance not in STANCES:
            raise ValueError("invalid evidence identifiers or stance")
        if not HEX.fullmatch(digest):
            raise ValueError("invalid document fingerprint")
        if sid in seen_ids:
            raise ValueError("duplicate sourceId")
        seen_ids.add(sid)
        captured = _stamp(e["capturedAt"])
        if captured > when + timedelta(minutes=5):
            excluded["future"] += 1
            continue
        if captured > when:  # small clock skew: don't count as fresh evidence
            excluded["future"] += 1
            continue
        if when - captured > timedelta(days=MAX_AGE_DAYS):
            excluded["stale"] += 1
            continue
        prior_family = fingerprints.get(digest)
        if prior_family is not None and prior_family != family:
            # Copy of exactly the same content cannot count as a new witness.
            excluded["duplicateDigest"] += 1
            continue
        fingerprints[digest] = family
        families.setdefault(family, set()).add(stance)

    conflicting_families = sorted(f for f, sides in families.items() if len(sides) > 1)
    support_families = sorted(f for f, sides in families.items() if "SUPPORT" in sides)
    contradict_families = sorted(f for f, sides in families.items() if "CONTRADICT" in sides)
    conflict = bool(conflicting_families or (support_families and contradict_families))
    if conflict:
        priority = "REVIEW_CANDIDATE"
        reason = "CONFLICTING_UNVERIFIED_SOURCE_STATEMENTS"
    elif len(families) < 2:
        priority = "HOLD"
        reason = "INSUFFICIENT_DISTINCT_SOURCE_FAMILIES"
    elif contradict_families:
        priority = "REVIEW_CANDIDATE"
        reason = "UNVERIFIED_CONTRADICTORY_STATEMENTS"
    else:
        priority = "HOLD"
        reason = "CORROBORATION_REQUIRES_EXTERNAL_ATTESTATION"
    summary = {
        "claimId": claim_id,
        "sourceFamilyCount": len(families),
        "supportFamilies": len(support_families),
        "contradictFamilies": len(contradict_families),
        "conflictingFamilies": len(conflicting_families),
        "excluded": excluded,
        "conflictDetected": conflict,
    }
    # Aggregate only (no claim text, evidence content, or raw sensitive IDs).
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    return {
        "status": priority,
        "reason": reason,
        "summary": summary,
        "assessmentSha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "sourceIndependence": "CLAIMED_NOT_VERIFIED",
        "independentVerification": "NOT_VERIFIED",
        "modelWasCalled": False,
        "authority": "NONE",
        "release": "HOLD",
    }


def bayesian_example(prior: float, likelihood_ratios: list[float]) -> float:
    """Demonstrate Bayes odds math only; NEVER a truth or authority metric.

    Caller is responsible for validating genuinely independent and calibrated
    likelihood ratios. Correlated evidence must not be fed to this function.
    """
    if not math.isfinite(prior) or not 0 < prior < 1:
        raise ValueError("prior must be between 0 and 1")
    if not isinstance(likelihood_ratios, list) or len(likelihood_ratios) > 16:
        raise ValueError("at most 16 independent ratios")
    logit = math.log(prior) - math.log1p(-prior)
    for ratio in likelihood_ratios:
        if not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or not 0 < ratio <= 1e9:
            raise ValueError("invalid likelihood ratio")
        logit += math.log(ratio)
    # Stable sigmoid; no external dependencies.
    if logit >= 0:
        return 1 / (1 + math.exp(-logit))
    z = math.exp(logit)
    return z / (1 + z)
