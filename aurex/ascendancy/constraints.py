"""M3. Exact constraints and contradiction detection.

Decimal sums use exact equality. Two different totals for one subject contradict
each other. Nothing in this module posts a financial result.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class SumConstraint:
    constraint_id: str
    parts: tuple[Decimal, ...]
    total: Decimal


@dataclass(frozen=True, slots=True)
class IdentityConstraint:
    constraint_id: str
    left: str
    right: str


@dataclass(frozen=True, slots=True)
class ClaimedTotal:
    subject: str
    total: Decimal


@dataclass(frozen=True, slots=True)
class ConstraintReport:
    violations: tuple[str, ...]
    contradictions: tuple[str, ...]
    authority: str = "ADVISORY_ONLY"

    @property
    def satisfied(self) -> bool:
        return not self.violations and not self.contradictions


def evaluate_constraints(
    sums: Sequence[SumConstraint] = (),
    identities: Sequence[IdentityConstraint] = (),
    claims: Sequence[ClaimedTotal] = (),
) -> ConstraintReport:
    violations: list[str] = []
    for sum_rule in sums:
        if sum(sum_rule.parts, Decimal("0")) != sum_rule.total:
            violations.append(sum_rule.constraint_id)
    for identity in identities:
        if identity.left != identity.right:
            violations.append(identity.constraint_id)
    seen: dict[str, Decimal] = {}
    contradictions: list[str] = []
    for claim in claims:
        prior = seen.get(claim.subject)
        if prior is not None and prior != claim.total and claim.subject not in contradictions:
            contradictions.append(claim.subject)
        seen[claim.subject] = claim.total
    return ConstraintReport(tuple(violations), tuple(contradictions))
