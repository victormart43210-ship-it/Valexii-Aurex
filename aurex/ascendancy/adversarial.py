"""M5. Challenges against a stated conclusion.

A conclusion that needs more independent roots than the graph can supply does
not survive. A one-cent change is a different Decimal value. These checks do
not repair the input.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from aurex.evidence_kernel import EvidenceGraph


@dataclass(frozen=True, slots=True)
class Challenge:
    name: str
    survived: bool
    authority: str = "ADVISORY_ONLY"


def independence_challenge(graph: EvidenceGraph, evidence_ids: tuple[str, ...], required_roots: int) -> Challenge:
    if required_roots < 1:
        raise ValueError("a challenge must require at least one root")
    survived = graph.independent_root_count(evidence_ids) >= required_roots
    return Challenge("independent-roots", survived)


def corrupt_decimal(amount: Decimal, cents: Decimal = Decimal("0.01")) -> Decimal:
    """Return a different amount. The caller decides whether the old conclusion still holds."""
    if cents == 0:
        raise ValueError("corruption must change the value")
    return amount + cents
