"""M1. Evidence dependency over the existing evidence graph.

The authoritative count is the number of disjoint source roots. Counting records
is retained only as a weak baseline.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from aurex.evidence_kernel import EvidenceGraph


@dataclass(frozen=True, slots=True)
class Corroboration:
    independent_roots: int
    record_count: int
    baseline_record_count: int
    shared_ancestry: bool
    authority: str = "ADVISORY_ONLY"

    @property
    def baseline_overcount(self) -> int:
        return self.baseline_record_count - self.independent_roots


def corroboration(graph: EvidenceGraph, evidence_ids: Sequence[str]) -> Corroboration:
    """Compare root independence with a record-count baseline on the same ids."""
    ids = tuple(evidence_ids)
    if not ids:
        raise ValueError("at least one evidence id is required")
    root_sets = [graph.roots(eid) for eid in ids]
    shared = any(root_sets[i] & root_sets[j] for i in range(len(root_sets)) for j in range(i + 1, len(root_sets)))
    return Corroboration(
        independent_roots=graph.independent_root_count(ids),
        record_count=len(ids),
        baseline_record_count=len(set(ids)),
        shared_ancestry=shared,
    )
