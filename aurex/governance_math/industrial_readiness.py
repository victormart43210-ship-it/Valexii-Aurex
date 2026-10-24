"""Synthetic-only industrial document readiness checks.

Read-only advisory classification. No DOT certification, no customer ingestion,
no tenant authentication, no authority or effect path. The caller must enforce
tenant access before supplying records; this module never fetches records.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class FindingStatus(StrEnum):
    PRESENT = "PRESENT_NOT_VERIFIED"
    MISSING = "MISSING"
    EXPIRED = "EXPIRED"
    CONFLICTING = "CONFLICTING"
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    record_id: str
    category: str
    source_sha256: str
    expires_on: date | None = None


@dataclass(frozen=True, slots=True)
class ReadinessFinding:
    category: str
    status: FindingStatus
    record_ids: tuple[str, ...]
    authority: str = "ADVISORY_ONLY_NO_CERTIFICATION"


def assess_readiness(
    records: tuple[EvidenceRecord, ...],
    required_categories: tuple[str, ...],
    *,
    as_of: date,
) -> tuple[ReadinessFinding, ...]:
    """Deterministic inventory findings, never compliance PASS.

    Categories are supplied by an authorized caller, not inferred from DOT law.
    Conflicting active digests are flagged for human review. Identical content
    is not independent corroboration. Missing digest is never verified.
    """
    if type(as_of) is not date:
        raise ValueError("as_of must be a date")
    if len(records) > 1000 or len(required_categories) > 100:
        raise ValueError("input exceeds bounded limits")
    if any(not isinstance(c, str) or not c or len(c) > 128 for c in required_categories):
        raise ValueError("invalid required category")
    if len(set(required_categories)) != len(required_categories):
        raise ValueError("duplicate required category")
    ids: set[str] = set()
    by_category: dict[str, list[EvidenceRecord]] = {}
    for record in records:
        if not isinstance(record, EvidenceRecord):
            raise ValueError("invalid evidence record")
        if (not isinstance(record.record_id, str) or not isinstance(record.category, str)
            or not isinstance(record.source_sha256, str)
            or (record.expires_on is not None and type(record.expires_on) is not date)):
            raise ValueError("invalid evidence field type")
        if (not record.record_id or len(record.record_id) > 128 or record.record_id in ids
            or not record.category or len(record.category) > 128):
            raise ValueError("invalid or duplicate evidence identity")
        ids.add(record.record_id)
        by_category.setdefault(record.category, []).append(record)
    results: list[ReadinessFinding] = []
    for category in required_categories:
        group = by_category.get(category, [])
        active = [r for r in group if r.expires_on is None or r.expires_on >= as_of]
        valid = [r for r in active if len(r.source_sha256) == 64
                 and all(ch in "0123456789abcdef" for ch in r.source_sha256)]
        if not group:
            status = FindingStatus.MISSING
        elif not active:
            status = FindingStatus.EXPIRED
        elif len(valid) != len(active):
            status = FindingStatus.NOT_VERIFIED
        elif len({r.source_sha256 for r in valid}) > 1:
            status = FindingStatus.CONFLICTING
        else:
            status = FindingStatus.PRESENT
        results.append(ReadinessFinding(category, status, tuple(sorted(r.record_id for r in group))))
    return tuple(results)
