"""APIS PRIME Folio Index: provenance-first, tenant-scoped research catalog.

A *metadata-only* library/relationship/time index. No raw customer document
storage, parsing, LLM inference, code execution, financial verdict, or authority.
Inspired by historical cataloguing and scientific methods, not an attempt to
recreate any institution's original archival software.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Visibility = Literal["public", "private"]
Kind = Literal[
    "original", "scan", "transcription", "extraction", "normalization",
    "hypothesis", "experiment", "challenge", "review",
]
Domain = Literal["manuscript", "finance", "compliance", "code", "model", "research"]
Relation = Literal[
    "derived_from", "interprets", "supports", "contradicts", "tests",
    "alternative_to", "equivalent_edition", "chronological_to",
]
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,95}\Z")
_KINDS: set[str] = {
    "original", "scan", "transcription", "extraction", "normalization",
    "hypothesis", "experiment", "challenge", "review",
}


def digest_of(data: bytes) -> str:
    """Integrity fingerprint only; not a signature or proof of authenticity."""
    if type(data) is not bytes:
        raise TypeError("bytes required")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True, slots=True)
class Folio:
    accession: str
    tenant: str
    collection: str
    kind: Kind
    domain: Domain
    sha256: str
    captured_at: str
    visibility: Visibility = "private"
    parent: str | None = None
    shelfmark: str | None = None
    source_date: str | None = None
    source_calendar: str | None = None
    # Pure subject facets, NOT raw content, raw prompts, OCR or filenames.
    facets: tuple[str, ...] = ()
    llm_training_consent: bool = False

    def __post_init__(self) -> None:
        for key in ("accession", "tenant", "collection"):
            value = getattr(self, key)
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise ValueError(f"invalid {key}")
        if self.kind not in _KINDS:
            raise ValueError("unsupported folio kind")
        if self.domain not in {"manuscript", "finance", "compliance", "code", "model", "research"}:
            raise ValueError("unsupported domain")
        if self.visibility not in {"public", "private"}:
            raise ValueError("invalid visibility")
        if not isinstance(self.sha256, str) or not _HEX.fullmatch(self.sha256):
            raise ValueError("sha256 must be lowercase 64-hex characters")
        if self.parent is not None and (
            not isinstance(self.parent, str) or not _ID.fullmatch(self.parent)
            or self.parent == self.accession
        ):
            raise ValueError("invalid parent reference")
        if self.shelfmark is not None and (
            not isinstance(self.shelfmark, str) or len(self.shelfmark) > 160
            or any(ord(ch) < 32 for ch in self.shelfmark)
        ):
            raise ValueError("invalid external shelfmark")
        if self.source_calendar is not None and (
            not isinstance(self.source_calendar, str)
            or self.source_calendar not in {"gregorian", "julian", "maya_long_count", "unknown"}
        ):
            raise ValueError("unsupported calendar or correlation")
        if self.source_date is not None and (
            not isinstance(self.source_date, str) or len(self.source_date) > 60
            or any(ord(ch) < 32 for ch in self.source_date)
        ):
            raise ValueError("invalid source date")
        if type(self.facets) is not tuple or len(self.facets) > 24 or any(
            not isinstance(f, str) or not _ID.fullmatch(f) for f in self.facets
        ):
            raise ValueError("invalid bounded subject facets")
        if self.llm_training_consent is not False:
            # Training consent is deliberately NOT an index-level permission.
            raise ValueError("training permission needs a separate consent workflow")
        try:
            moment = datetime.fromisoformat(self.captured_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ValueError("captured_at must be ISO-8601") from exc
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("captured_at requires an explicit timezone")


@dataclass(frozen=True, slots=True)
class FolioLink:
    source: str
    target: str
    relation: Relation
    rationale_sha256: str

    def __post_init__(self) -> None:
        if (not _ID.fullmatch(self.source) or not _ID.fullmatch(self.target)
                or self.source == self.target):
            raise ValueError("invalid folio link endpoints")
        if self.relation not in {
            "derived_from", "interprets", "supports", "contradicts", "tests",
            "alternative_to", "equivalent_edition", "chronological_to",
        }:
            raise ValueError("unknown relationship")
        if not _HEX.fullmatch(self.rationale_sha256):
            raise ValueError("rationale fingerprint required")


class FolioIndex:
    """Append-only in-process registry prototype, NOT durable event storage."""

    def __init__(self) -> None:
        self._folio: dict[tuple[str, str], Folio] = {}
        self._links: list[tuple[str, FolioLink]] = []

    def admit(self, folio: Folio) -> None:
        key = (folio.tenant, folio.accession)
        if key in self._folio:
            raise ValueError("folio ID already admitted; sources are immutable")
        if folio.parent is not None:
            parent = self._folio.get((folio.tenant, folio.parent))
            if parent is None:
                raise ValueError("parent must exist in same tenant")
            if folio.visibility == "public" and parent.visibility == "private":
                raise ValueError("cannot publish derivatives of private sources")
        self._folio[key] = folio

    def relate(self, tenant: str, link: FolioLink) -> None:
        a = self._folio.get((tenant, link.source))
        b = self._folio.get((tenant, link.target))
        if a is None or b is None:
            raise ValueError("relationship cannot cross tenants or cite missing folios")
        if a.visibility == "public" and b.visibility == "private":
            raise ValueError("public artifact cannot link to private evidence")
        if link.relation == "derived_from" and a.parent != b.accession:
            raise ValueError("derivation must match frozen lineage")
        self._links.append((tenant, link))

    def list_receipts(self, *, tenant: str) -> list[dict[str, str]]:
        """Only PUBLIC receipts; authenticated private views need a separate API gate."""
        out: list[dict[str, str]] = []
        for (owner, _), folio in self._folio.items():
            if owner != tenant or folio.visibility != "public":
                continue
            out.append({
                "accession": folio.accession, "collection": folio.collection,
                "kind": folio.kind, "domain": folio.domain,
                "sha256": folio.sha256,
                "status": "CATALOGUED_NOT_VERIFIED",
                "authority": "NONE",
            })
        return sorted(out, key=lambda item: (item["collection"], item["accession"]))

    def relation_counts(self, *, tenant: str) -> dict[str, int]:
        """No cross-tenant relationship observations leak into public listings."""
        counts: dict[str, int] = {}
        for owner, link in self._links:
            if owner != tenant:
                continue
            source = self._folio.get((tenant, link.source))
            target = self._folio.get((tenant, link.target))
            if (source is not None and target is not None
                    and source.visibility == "public" and target.visibility == "public"):
                counts[link.relation] = counts.get(link.relation, 0) + 1
        return dict(sorted(counts.items()))


def maya_long_count_days(
    baktun: int, katun: int, tun: int, winal: int, kin: int
) -> int:
    """Relative day index only. NO Gregorian conversion or unique inscription reading."""
    vals = (baktun, katun, tun, winal, kin)
    if any(type(v) is not int for v in vals):
        raise ValueError("Maya components must be integers")
    if not (0 <= baktun <= 99 and 0 <= katun < 20 and 0 <= tun < 20
            and 0 <= winal < 18 and 0 <= kin < 20):
        raise ValueError("Maya long-count components out of bounds")
    return baktun * 144000 + katun * 7200 + tun * 360 + winal * 20 + kin


def compare_maya_candidates(candidates: tuple[tuple[int, int, int, int, int], ...]) -> dict[str, object]:
    """Show why equal 260-day phases cannot resolve damaged 2026 Maya glyphs."""
    if not candidates or len(candidates) > 16:
        raise ValueError("provide 1 to 16 proposed candidate readings")
    days = [maya_long_count_days(*candidate) for candidate in candidates]
    phases = [day % 260 for day in days]
    return {
        "day_indices": days,
        "tzolkin_260_phases": phases,
        "identical_260_phase": len(set(phases)) == 1,
        "unique_long_count": len(set(days)) == 1,
        "finding": "AMBIGUOUS_READING_HOLD" if len(set(days)) > 1 else "ARITHMETIC_ONLY",
        "gregorian_conversion": "NOT_ATTEMPTED_REQUIRES_DECLARED_CORRELATION",
        "glyph_interpretation": "NOT_VERIFIED",
        "authority": "NONE",
    }
