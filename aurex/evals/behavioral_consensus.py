"""Functional-consistency grouping of *pre-observed* sandbox outputs.

Inspired by MIT's research on functional clustering for code generation.
This code DOES NOT execute untrusted programs, produce model samples, copy
the research implementation, or equate agreement with correctness.
Candidates are grouped only by exact declared output vectors over the same
frozen test-suite identity; correlated origins and shared bugs remain risks.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from aurex.provenance import fingerprint

_SHA = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ObservedCandidate:
    candidate_id: str
    source_group: str
    model_sha256: str
    test_suite_sha256: str
    observed_outputs: tuple[str, ...]
    observation_evidence_sha256: str


@dataclass(frozen=True, slots=True)
class BehaviorCluster:
    behavior_sha256: str
    members: tuple[str, ...]
    count: int


@dataclass(frozen=True, slots=True)
class ConsensusReport:
    candidates: int
    observations_per_candidate: int
    clusters: tuple[BehaviorCluster, ...]
    dominant_fraction: float
    suggested_candidate: str | None
    gate: str
    independent_verification: str = "NOT VERIFIED"
    authority: str = "NO_EXECUTION_NO_CORRECTNESS_CLAIM"


def group_observed_behaviors(
    candidates: Sequence[ObservedCandidate], *, agreement_threshold: float = 0.8
) -> ConsensusReport:
    """Group identical test behaviors deterministically; always require review.

    Sample groups must be distinct to reduce trivial duplicate voting. That
    does NOT establish statistical independence; all outputs may still share
    a bad interpretation of the spec or a weak test suite.
    """
    if (
        not isinstance(agreement_threshold, (float, int))
        or isinstance(agreement_threshold, bool)
        or not 0.5 < agreement_threshold <= 1
    ):
        raise ValueError("agreement threshold must be >0.5 and <=1")
    if not 2 <= len(candidates) <= 64:
        raise ValueError("2..64 observed candidates required")
    ids: set[str] = set()
    groups: set[str] = set()
    model_sha: str | None = None
    suite_sha: str | None = None
    observed_n: int | None = None
    clusters: dict[str, list[str]] = {}
    for row in candidates:
        if not isinstance(row, ObservedCandidate):
            raise ValueError("invalid candidate")
        if (
            not row.candidate_id or row.candidate_id in ids
            or not row.source_group or row.source_group in groups
            or any(
                not isinstance(value, str) or not _SHA.fullmatch(value)
                for value in (row.model_sha256, row.test_suite_sha256, row.observation_evidence_sha256)
            )
            or not 1 <= len(row.observed_outputs) <= 128
            or any(
                not isinstance(value, str) or len(value) > 4096
                for value in row.observed_outputs
            )
            or (model_sha is not None and row.model_sha256 != model_sha)
            or (suite_sha is not None and row.test_suite_sha256 != suite_sha)
            or (observed_n is not None and len(row.observed_outputs) != observed_n)
        ):
            raise ValueError("duplicate, correlated, oversized or mismatched observations")
        ids.add(row.candidate_id)
        groups.add(row.source_group)
        model_sha = row.model_sha256
        suite_sha = row.test_suite_sha256
        observed_n = len(row.observed_outputs)
        digest = fingerprint({"test_suite_sha256": suite_sha, "outputs": row.observed_outputs})
        clusters.setdefault(digest, []).append(row.candidate_id)
    ordered = tuple(
        sorted(
            (BehaviorCluster(digest, tuple(sorted(members)), len(members))
             for digest, members in clusters.items()),
            key=lambda x: (-x.count, x.behavior_sha256),
        )
    )
    dominant = ordered[0]
    fraction = dominant.count / len(candidates)
    suggested = dominant.members[0] if fraction >= agreement_threshold else None
    return ConsensusReport(
        len(candidates), observed_n or 0, ordered, fraction, suggested,
        "CONSISTENT_CANDIDATE_REVIEW_REQUIRED" if suggested else "ABSTAIN_HOLD",
    )
