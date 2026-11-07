"""Separate what was seen, calculated, inferred, withheld, and confirmed.

An inferred statement cannot be relabeled as confirmed. Confirmed recovery is
outside this classifier: callers keep that amount at 0.00 unless a separate
human authority record exists.
"""

from __future__ import annotations

EVIDENCE_CLASSES = (
    "OBSERVED",
    "CALCULATED",
    "INFERRED",
    "UNVERIFIED",
    "WITHHELD",
    "CONFIRMED",
)

_BY_CLAIM = {
    "CALCULATED_DISCREPANCY": "CALCULATED",
    "SUSPECTED_EXPOSURE": "INFERRED",
    "UNVERIFIED_INTERPRETATION": "UNVERIFIED",
}


def evidence_class_for_claim(claim: str, *, withheld: bool) -> str:
    """Map a frozen DISPATER claim onto one evidence class.

    Withheld wins over a calculated or inferred label because the amount is
    not being advanced. Nothing here returns CONFIRMED.
    """
    if withheld:
        return "WITHHELD"
    mapped = _BY_CLAIM.get(claim)
    if mapped is None:
        raise ValueError(f"claim is outside the evidence map: {claim!r}")
    if mapped == "CONFIRMED":
        raise ValueError("inferred or calculated output cannot confirm itself")
    return mapped
