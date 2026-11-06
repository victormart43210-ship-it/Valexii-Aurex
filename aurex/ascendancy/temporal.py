"""M4. Versioned intervals and named supersession.

A successor whose start is on or before the query date retires only the named
predecessor. Retired records remain in the supplied history.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class IntervalRecord:
    record_id: str
    start: date
    end: date
    supersedes: str = ""


def covering(records: Sequence[IntervalRecord], on: date) -> tuple[str, ...]:
    """Ids in force on `on`, after named supersession. History is not rewritten."""
    if on.__class__ is not date:
        raise ValueError("query date must be datetime.date")
    active = [row for row in records if row.start <= on <= row.end]
    retired = {row.supersedes for row in active if row.supersedes and row.start <= on}
    return tuple(sorted(row.record_id for row in active if row.record_id not in retired))
