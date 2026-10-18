"""Offline tests for immutable provenance and interdisciplinary ordering safeguards."""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from aurex.folio_index import (
    Folio,
    FolioIndex,
    FolioLink,
    compare_maya_candidates,
    digest_of,
    maya_long_count_days,
)

NOW = datetime(2026, 10, 18, tzinfo=UTC).isoformat()


def source(
    accession: str = "ms-01",
    *,
    tenant: str = "tenant-a",
    kind: str = "original",
    parent: str | None = None,
    visibility: str = "public",
    **other: object,
) -> Folio:
    fields: dict[str, object] = dict(
        accession=accession,
        tenant=tenant,
        collection="primary.maya",
        kind=kind,
        domain="manuscript",
        sha256=digest_of(accession.encode()),
        captured_at=NOW,
        visibility=visibility,
        parent=parent,
        shelfmark="Pal.lat.2028",
        facets=("calendar", "epigraphy"),
    )
    fields.update(other)
    return Folio(**fields)  # type: ignore[arg-type]


def test_source_and_derivation_append_only_and_content_addressed() -> None:
    index = FolioIndex()
    original = source()
    derived = source("scan-01", kind="scan", parent=original.accession)
    index.admit(original)
    index.admit(derived)
    with pytest.raises(ValueError, match="already admitted"):
        index.admit(original)
    index.relate(
        "tenant-a",
        FolioLink("scan-01", "ms-01", "derived_from", digest_of(b"photo evidence")),
    )
    entries = index.list_receipts(tenant="tenant-a")
    assert len(entries) == 2
    assert entries[0]["authority"] == "NONE"
    assert all(item["status"] == "CATALOGUED_NOT_VERIFIED" for item in entries)
    assert index.relation_counts(tenant="tenant-a") == {"derived_from": 1}


def test_cross_tenant_derivation_fails_closed() -> None:
    index = FolioIndex()
    index.admit(source("a", visibility="private"))
    with pytest.raises(ValueError, match="parent must exist"):
        index.admit(source("child", tenant="tenant-b", parent="a", kind="extraction"))
    index.admit(source("b", tenant="tenant-b"))
    with pytest.raises(ValueError, match="cannot cross"):
        index.relate("tenant-a", FolioLink("a", "b", "interprets", digest_of(b"why")))
    assert index.relation_counts(tenant="tenant-a") == {}


def test_no_automatic_private_to_public_declassification() -> None:
    index = FolioIndex()
    index.admit(source("private", visibility="private"))
    with pytest.raises(ValueError, match="cannot publish"):
        index.admit(
            source("public-child", kind="extraction", parent="private", visibility="public")
        )


def test_public_listing_does_not_expose_private_receipts() -> None:
    index = FolioIndex()
    index.admit(source("private", visibility="private"))
    index.admit(source("public", visibility="public"))
    assert [entry["accession"] for entry in index.list_receipts(tenant="tenant-a")] == [
        "public"
    ]
    assert index.list_receipts(tenant="tenant-b") == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"sha256": "no-hash"},
        {"captured_at": "2026-10-18T12:00:00"},
        {"llm_training_consent": True},
        {"visibility": "external"},
        {"source_calendar": "unapproved-conversion"},
        {"facets": ("* wildcard",)},
        {"collection": "../../etc"},
    ],
)
def test_malformed_or_permission_expanding_metadata_rejected(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        source(**overrides)


def test_maya_2026_el_palmar_260_day_ambiguity_survives_controls() -> None:
    # Three alternative proposed inscriptions are separated by 260 days,
    # so matching Tzolk'in phases alone cannot resolve damaged glyphs.
    candidates = (
        (8, 7, 0, 5, 0),
        (8, 7, 1, 0, 0),
        (8, 7, 1, 13, 0),
    )
    result = compare_maya_candidates(candidates)
    assert result["identical_260_phase"] is True
    assert result["unique_long_count"] is False
    assert result["finding"] == "AMBIGUOUS_READING_HOLD"
    assert result["day_indices"][1] - result["day_indices"][0] == 260
    assert result["day_indices"][2] - result["day_indices"][1] == 260
    assert result["gregorian_conversion"].startswith("NOT_ATTEMPTED")
    assert result["glyph_interpretation"] == "NOT_VERIFIED"


def test_maya_long_count_components_have_correct_mixed_radices() -> None:
    assert maya_long_count_days(0, 0, 1, 0, 0) == 360
    assert maya_long_count_days(0, 1, 0, 0, 0) == 7200
    assert maya_long_count_days(1, 0, 0, 0, 0) == 144000


@pytest.mark.parametrize(
    "tuple_of_counts",
    [
        (0, 0, 0, 18, 0),
        (0, 0, 0, 0, 20),
        (-1, 0, 0, 0, 0),
        (0, 20, 0, 0, 0),
        (True, 0, 0, 0, 0),
    ],
)
def test_maya_invalid_dates_refused(tuple_of_counts: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        maya_long_count_days(*tuple_of_counts)  # type: ignore[arg-type]


def test_no_absolute_calendar_conversion_claim() -> None:
    result = compare_maya_candidates(((8, 7, 1, 0, 0),))
    assert result["finding"] == "ARITHMETIC_ONLY"
    assert result["authority"] == "NONE"
