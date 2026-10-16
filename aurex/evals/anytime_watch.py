"""Anytime-valid e-process *diagnostic* for sequential false-pass monitoring.

Adapted independently from the elementary betting-supermartingale idea
studied by Aaditya Ramdas/CMU. This e-process is only statistically valid
when the pre-specified null E[error_t | history] <= p0 holds and the stake is
predictable. No assumptions can be verified from caller-provided rows alone.
Never maps a statistical signal to authorization, punishment, or deployment.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

_SHA = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ReviewedOutcome:
    item_id: str
    lineage_group: str
    observed_at: datetime
    false_pass: bool
    evidence_sha256: str


@dataclass(frozen=True, slots=True)
class AnytimeReport:
    observed: int
    errors: int
    baseline_error_ceiling: float
    stake: float
    log_e_final: float
    log_e_max: float
    first_crossing_index: int | None
    alpha: float
    gate: str
    assumption: str = "CONDITIONAL_ERROR_CEILING_NOT_ESTABLISHED"
    authority: str = "ADVISORY_ONLY_NO_PASS"


def _p(value: float) -> float:
    if (
        not isinstance(value, (float, int)) or isinstance(value, bool)
        or not math.isfinite(value) or not 0 < value < 1
    ):
        raise ValueError("expected a finite probability strictly between 0 and 1")
    return float(value)


def watch_false_passes(
    records: Sequence[ReviewedOutcome],
    *,
    allowed_error: float = 0.05,
    alpha: float = 0.05,
    stake: float = 1.0,
) -> AnytimeReport:
    """Pre-chosen nonnegative stake yields e_t=Π[1+stake*(x_t-p0)].

    Under the conditional-null bound E[x_t|past]<=p0, factors have expectation
    <=1, and remain nonnegative when stake<=1/p0. A crossing of 1/alpha
    indicates evidence against the null subject to these assumptions. Calling
    this repeatedly on overlapping datasets does not create new independent
    tests; no claims of formal coverage without independently proved premises.
    """
    p0 = _p(allowed_error)
    significance = _p(alpha)
    if (
        not isinstance(stake, (float, int)) or isinstance(stake, bool)
        or not math.isfinite(stake) or not 0 < stake <= 1 / p0
    ):
        raise ValueError("stake must be fixed in (0, 1/allowed_error]")
    if len(records) > 10_000:
        raise ValueError("record limit exceeded")
    seen_ids: set[str] = set()
    seen_groups: set[str] = set()
    previous: datetime | None = None
    logwealth = 0.0
    peak = 0.0
    crossing: int | None = None
    errors = 0
    threshold = -math.log(significance)
    for i, row in enumerate(records, 1):
        if not isinstance(row, ReviewedOutcome):
            raise ValueError("expected ReviewedOutcome")
        if (
            not row.item_id or row.item_id in seen_ids
            or not row.lineage_group or row.lineage_group in seen_groups
            or not isinstance(row.false_pass, bool)
            or not _SHA.fullmatch(row.evidence_sha256)
            or not isinstance(row.observed_at, datetime)
            or row.observed_at.tzinfo is None
            or row.observed_at.utcoffset() is None
            or (previous is not None and row.observed_at <= previous)
        ):
            raise ValueError("invalid, correlated, duplicate or out-of-order observation")
        previous = row.observed_at
        seen_ids.add(row.item_id)
        seen_groups.add(row.lineage_group)
        x = int(row.false_pass)
        errors += x
        factor = 1 + float(stake) * (x - p0)
        logwealth += math.log(factor) if factor > 0 else -math.inf
        peak = max(peak, logwealth)
        if crossing is None and logwealth >= threshold:
            crossing = i
    return AnytimeReport(
        observed=len(records), errors=errors, baseline_error_ceiling=p0,
        stake=float(stake), log_e_final=logwealth, log_e_max=peak,
        first_crossing_index=crossing, alpha=significance,
        gate="REVIEW_EXCESS_FALSE_PASSES" if crossing is not None else "NO_SIGNAL_NOT_PROOF",
    )
