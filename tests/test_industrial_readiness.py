"""Synthetic-only negative and boundary tests for industrial readiness."""
from datetime import date

import pytest

from aurex.governance_math.industrial_readiness import (
    EvidenceRecord,
    FindingStatus,
    assess_readiness,
)

TODAY = date(2026, 10, 24)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def test_missing_is_not_pass() -> None:
    findings = assess_readiness((), ("driver_file",), as_of=TODAY)
    assert findings[0].status is FindingStatus.MISSING
    assert findings[0].authority == "ADVISORY_ONLY_NO_CERTIFICATION"


def test_expired_is_flagged() -> None:
    record = EvidenceRecord("one", "inspection", DIGEST_A, date(2026, 10, 23))
    assert assess_readiness((record,), ("inspection",), as_of=TODAY)[0].status is FindingStatus.EXPIRED


def test_present_never_claims_verified() -> None:
    record = EvidenceRecord("one", "inspection", DIGEST_A, TODAY)
    assert assess_readiness((record,), ("inspection",), as_of=TODAY)[0].status is FindingStatus.PRESENT


def test_invalid_digest_demotes() -> None:
    record = EvidenceRecord("one", "inspection", "unknown")
    assert assess_readiness((record,), ("inspection",), as_of=TODAY)[0].status is FindingStatus.NOT_VERIFIED


def test_conflicting_active_sources() -> None:
    records = (EvidenceRecord("one", "inspection", DIGEST_A),
               EvidenceRecord("two", "inspection", DIGEST_B))
    assert assess_readiness(records, ("inspection",), as_of=TODAY)[0].status is FindingStatus.CONFLICTING


def test_duplicate_record_ids_rejected() -> None:
    records = (EvidenceRecord("same", "a", DIGEST_A),
               EvidenceRecord("same", "b", DIGEST_B))
    with pytest.raises(ValueError):
        assess_readiness(records, ("a",), as_of=TODAY)


def test_duplicate_required_categories_rejected() -> None:
    with pytest.raises(ValueError):
        assess_readiness((), ("a", "a"), as_of=TODAY)


def test_bounded_input() -> None:
    with pytest.raises(ValueError):
        assess_readiness((), tuple(str(i) for i in range(101)), as_of=TODAY)
