"""Reproducible selective-risk, calibration, and group-leakage QA.

Educational techniques from University of Helsinki / MinnaLearn Building AI:
classification, Bayesian reasoning, cross-validation and empirical evaluation.
All metrics are descriptive ONLY. Artificial samples are not external proof.
"""
from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from typing import Any

LABELS = {"CLEAR", "REVIEW", "HOLD"}


def wilson_interval(errors: int, trials: int, z: float = 1.95996398454) -> tuple[float, float] | None:
    """95% Wilson score interval; robust for zero observed errors."""
    if not isinstance(errors, int) or not isinstance(trials, int) or trials < 0 or not 0 <= errors <= trials:
        raise ValueError("invalid counts")
    if trials == 0:
        return None
    p = errors / trials
    denom = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * trials)) / trials) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def evaluate_rows(truth: list[dict[str, Any]], predicted: list[dict[str, Any]]) -> dict[str, Any]:
    if not truth or len(truth) > 100_000:
        raise ValueError("bounded nonempty truth required")
    def unique_map(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
        out = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or len(row["id"]) > 96:
                raise ValueError("invalid row id")
            if row["id"] in out:
                raise ValueError("duplicate row id")
            if row.get(key) not in LABELS:
                raise ValueError("invalid label")
            out[row["id"]] = row
        return out
    t = unique_map(truth, "expected")
    p = unique_map(predicted, "prediction")
    if set(t) != set(p):
        raise ValueError("exact ID join required; missing data fails closed")
    covered = wrong = false_clear = false_review = review_tp = review_total = 0
    brier_sum = 0.0
    brier_n = 0
    bins: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for key in sorted(t):
        expected, row = t[key]["expected"], p[key]
        pred = row["prediction"]
        if expected == "REVIEW":
            review_total += 1
        if pred != "HOLD":
            covered += 1
            wrong += int(pred != expected)
        false_clear += int(pred == "CLEAR" and expected == "REVIEW")
        false_review += int(pred == "REVIEW" and expected == "CLEAR")
        review_tp += int(pred == "REVIEW" and expected == "REVIEW")
        if "pReview" in row:
            probability = row["pReview"]
            if not isinstance(probability, (int, float)) or not math.isfinite(probability) or not 0 <= probability <= 1:
                raise ValueError("bad pReview; probability must be finite [0,1]")
            if pred != "HOLD" and expected in ("REVIEW", "CLEAR"):
                y = int(expected == "REVIEW")
                brier_sum += (probability - y)**2
                brier_n += 1
                bin_id = min(9, int(probability * 10))
                bins[bin_id].append((float(probability), y))
    total = len(t)
    ece = None
    if brier_n:
        ece = sum(len(vals) / brier_n * abs(sum(x for x, _ in vals) / len(vals) - sum(y for _, y in vals) / len(vals)) for vals in bins.values())
    ci = wilson_interval(false_clear, review_total)
    return {
        "total": total,
        "coverage": round(covered / total, 6),
        "selectiveRisk": round(wrong / covered, 6) if covered else None,
        "unsafeClearAgainstReview": false_clear,
        "unsafeClearRateAmongReview": round(false_clear / review_total, 6) if review_total else None,
        "unsafeClearWilson95": [round(z, 6) for z in ci] if ci else None,
        "falseReviewAgainstClear": false_review,
        "reviewRecall": round(review_tp / review_total, 6) if review_total else None,
        "brierScore": round(brier_sum / brier_n, 6) if brier_n else None,
        "expectedCalibrationError": round(ece, 6) if ece is not None else None,
        "probabilitySampleCount": brier_n,
        "blindExternalLabels": "NOT_VERIFIED",
        "modelImprovement": "NOT_VERIFIED",
        "authority": "NONE",
        "release": "HOLD",
    }


def deterministic_group_folds(rows: list[dict[str, str]], k: int = 5) -> dict[str, int]:
    """Whole groups stay in one fold; prevents entity-level train/test leakage.

    No optimizer/model training occurs here. This is an assignment helper, not
    evidence that cross-validation was performed or models generalize.
    """
    if not isinstance(k, int) or not 2 <= k <= 10:
        raise ValueError("fold count 2-10")
    groups: dict[str, list[str]] = defaultdict(list)
    ids: set[str] = set()
    if len(rows) > 100_000:
        raise ValueError("too many rows")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not isinstance(row.get("group"), str):
            raise ValueError("id/group strings required")
        i, group = row["id"], row["group"]
        if not i or len(i) > 96 or not group or len(group) > 96 or i in ids:
            raise ValueError("missing or duplicate id/group")
        ids.add(i)
        groups[group].append(i)
    if len(groups) < k:
        raise ValueError("not enough distinct groups")
    assigned: dict[str, int] = {}
    counts = [0] * k
    for group in sorted(groups, key=lambda g: (-len(groups[g]), hashlib.sha256(g.encode()).hexdigest())):
        fold = min(range(k), key=lambda f: (counts[f], f))
        for i in groups[group]:
            assigned[i] = fold
        counts[fold] += len(groups[group])
    return assigned


def cusum_shift(values: list[float], *, reference_mean: float, slack: float = 0.05, threshold: float = 5.0) -> list[int]:
    """Two-sided CUSUM drift *candidates*, not validated change points.

    Data must be chronologically ordered and normalized to [0,1]. Baseline
    must come from independent historical data; thresholds are NOT calibrated.
    No training or authority decisions happen here.
    """
    if len(values) > 100_000 or not 0 <= reference_mean <= 1 or not 0 <= slack <= 1 or not 0 < threshold <= 100:
        raise ValueError("invalid drift configuration")
    upper = lower = 0.0
    indices = []
    for i, value in enumerate(values):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("nonfinite or out-of-range observation")
        upper = max(0.0, upper + value - reference_mean - slack)
        lower = max(0.0, lower + reference_mean - value - slack)
        if max(upper, lower) >= threshold:
            indices.append(i)
            upper = lower = 0.0
    return indices
