"""Research templates. Each one states what is not established."""

from __future__ import annotations

from typing import Any

_TEMPLATES: dict[str, dict[str, Any]] = {
    "voynich": {
        "subject": "Voynich manuscript",
        "scholarly_status": "NOT_ESTABLISHED",
        "can_examine": ["glyph crops", "repeated pixel groups", "page comparison", "faded-stroke contrast"],
        "must_not_claim": ["a decipherment", "a language identification", "recovered text"],
    },
    "rongorongo": {
        "subject": "Rongorongo",
        "scholarly_status": "NOT_ESTABLISHED",
        "can_examine": ["incision contrast on a supplied photograph", "symbol crops", "line orientation"],
        "must_not_claim": ["a reading", "depth from a single photograph", "a decipherment"],
    },
    "linear-a": {
        "subject": "Linear A",
        "scholarly_status": "NOT_ESTABLISHED",
        "can_examine": ["inscription crops", "damage versus mark contrast", "sign-frequency counts of human labels"],
        "must_not_claim": ["a translation", "that a crack is a sign", "a decipherment"],
    },
    "palimpsest": {
        "subject": "Palimpsest",
        "scholarly_status": "NOT_ESTABLISHED",
        "can_examine": ["supplied spectral bands", "band differences", "region review"],
        "must_not_claim": ["undertext from an ordinary RGB photograph", "a reconstruction as fact"],
    },
    "artwork": {
        "subject": "Painting or other artwork",
        "scholarly_status": "NOT_ESTABLISHED",
        "can_examine": ["a supplied infrared, ultraviolet, X-ray, or XRF image as an ordinary registered image"],
        "must_not_claim": ["what lies under paint from an RGB photograph", "an elemental identification without the instrument file"],
    },
}


def research_template(name: str) -> dict[str, Any]:
    template = _TEMPLATES.get(name)
    if template is None:
        return {
            "decision": "REFUSED",
            "effect": "NONE",
            "authority": "NONE",
            "problems": ["UNKNOWN_TEMPLATE"],
        }
    return {
        "schema": "aurex.manuscript_forensics.template.v1",
        "decision": "RECORDED",
        "effect": "NONE",
        "authority": "NONE",
        "financial_authority": "NONE",
        "production": "HOLD",
        "launch": "NOT_STARTED",
        **template,
    }


def template_names() -> list[str]:
    return sorted(_TEMPLATES)
