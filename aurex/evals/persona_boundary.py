"""Zero-network diagnostics for untrusted model/persona text.

Text may claim any identity or authority. This module NEVER authenticates a
speaker, verifies an attestation, measures internal model activations, or acts
on a tool. Its lexical flags are an imperfect diagnostic, not a safety gate.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

Origin = Literal["model_output", "retrieved_document", "tool_output"]

_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,63}$")
_PERSONAS = ("ghost", "leviathan")
_ROLE = re.compile(
    r"\b(?:i\s+am|i'm|i\s+represent|as)\s+(?:the\s+|an?\s+)?"
    r"(?:ghost|leviathan|administrator|admin|developer|root|owner|sovereign)\b",
    re.I,
)
_PRIVILEGE = re.compile(
    r"\b(?:i\s+(?:have|possess|hold)\s+(?:unrestricted(?:\s+(?:admin|root|system))?|admin|root|system)\s+"
    r"(?:access|authority|privileges?|permissions?)|"
    r"(?:grant|give)\s+(?:me|myself|us)\s+(?:admin\s+)?(?:permissions?|access|authority)|"
    r"(?:override|bypass|disable)\s+(?:the\s+)?(?:security|policy|permission|audit|approval)|"
    r"security[_\s-]?override|authority[_\s-]?granted|"
    r"i\s+(?:am|was)\s+(?:the\s+)?(?:administrator|root\s+user|system\s+owner)|"
    r"(?:deploy|merge|execute|approve|transfer)\s+(?:it|this|now|without\s+approval))\b",
    re.I,
)
_ATTESTATION = re.compile(
    r"\b(?:verified\s+by\s+custos|independent\s+(?:review|verification)\s+(?:passed|approved)|"
    r"(?:signed|authorized)\s+by\s+(?:the\s+)?(?:administrator|owner|custos)|"
    r"signature\s+(?:verified|approved))\b",
    re.I,
)
_INSTRUCTION = re.compile(
    r"\b(?:ignore\s+(?:all\s+)?(?:previous(?:\s+(?:system|developer))?|system|developer)\s+instructions?|"
    r"(?:new|replacement)\s+system\s+(?:message|prompt|instructions?)|"
    r"(?:you\s+must|you\s+are\s+required\s+to)\s+ignore\s+(?:the\s+)?(?:policy|rules))\b",
    re.I,
)


@dataclass(frozen=True, slots=True)
class UntrustedTurn:
    turn_id: str
    source: Origin
    text: str


@dataclass(frozen=True, slots=True)
class PersonaFinding:
    turn_id: str
    source: Origin
    text_sha256: str
    flags: tuple[str, ...]
    persona_references: tuple[str, ...]
    diagnostic: str
    claimed_identity_verified: bool = False
    authority: str = "NONE"
    execution: str = "NO_ACTION"
    independent_verification: str = "NOT VERIFIED"
    activation_measurement: str = "NOT MEASURED"


@dataclass(frozen=True, slots=True)
class TranscriptAssessment:
    turns: int
    marked_turns: int
    first_flags: tuple[str, ...]
    last_flags: tuple[str, ...]
    lexical_markers_changed: bool
    diagnostic: str
    authority: str = "NONE"
    activation_measurement: str = "NOT MEASURED"
    independent_verification: str = "NOT VERIFIED"


def assess_turn(turn: UntrustedTurn) -> PersonaFinding:
    """Label bounded untrusted text; do NOT infer identity or permission."""
    if not isinstance(turn, UntrustedTurn):
        raise ValueError("turn must be an UntrustedTurn")
    if not isinstance(turn.turn_id, str) or not _ID.fullmatch(turn.turn_id):
        raise ValueError("invalid turn ID")
    if turn.source not in ("model_output", "retrieved_document", "tool_output"):
        raise ValueError("source must be explicitly untrusted")
    if not isinstance(turn.text, str):
        raise ValueError("text must be a string")
    try:
        encoded = turn.text.encode("utf-8")
    except UnicodeError as exc:
        raise ValueError("text must be valid UTF-8") from exc
    if not 1 <= len(encoded) <= 4096:
        raise ValueError("text must be 1..4096 UTF-8 bytes")
    flags: list[str] = []
    lower = turn.text.casefold()
    referenced = tuple(p for p in _PERSONAS if re.search(r"\b" + p + r"\b", lower))
    if referenced:
        flags.append("PERSONA_REFERENCE")
    if _ROLE.search(turn.text):
        flags.append("ROLE_OR_IDENTITY_CLAIM")
    if _PRIVILEGE.search(turn.text):
        flags.append("PRIVILEGE_CLAIM_PATTERN")
    if _ATTESTATION.search(turn.text):
        flags.append("ATTESTATION_CLAIM_PATTERN")
    if _INSTRUCTION.search(turn.text):
        flags.append("UNTRUSTED_INSTRUCTION_PATTERN")
    risk_flags = {"PRIVILEGE_CLAIM_PATTERN", "ATTESTATION_CLAIM_PATTERN", "UNTRUSTED_INSTRUCTION_PATTERN"}
    return PersonaFinding(
        turn_id=turn.turn_id,
        source=turn.source,
        text_sha256=hashlib.sha256(encoded).hexdigest(),
        flags=tuple(flags),
        persona_references=referenced,
        diagnostic="REVIEW_REQUIRED" if risk_flags.intersection(flags) else "NO_PRIVILEGE_SIGNAL_NOT_PROOF",
    )


def assess_transcript(turns: Sequence[UntrustedTurn]) -> TranscriptAssessment:
    """Compare lexical markers, NOT internal persona-axis activations.

    Does not retain raw turns or extrapolate to a measured drift rate.
    """
    if not isinstance(turns, (tuple, list)) or not 1 <= len(turns) <= 64:
        raise ValueError("expected 1..64 turns")
    seen: set[str] = set()
    results: list[PersonaFinding] = []
    total_bytes = 0
    for turn in turns:
        found = assess_turn(turn)
        if found.turn_id in seen:
            raise ValueError("duplicate turn ID")
        seen.add(found.turn_id)
        total_bytes += len(turn.text.encode("utf-8"))
        if total_bytes > 65536:
            raise ValueError("transcript exceeds 65536 UTF-8 bytes")
        results.append(found)
    any_review = any(r.diagnostic == "REVIEW_REQUIRED" for r in results)
    return TranscriptAssessment(
        turns=len(results),
        marked_turns=sum(bool(r.flags) for r in results),
        first_flags=results[0].flags,
        last_flags=results[-1].flags,
        lexical_markers_changed=results[0].flags != results[-1].flags,
        diagnostic="REVIEW_REQUIRED" if any_review else "NO_PRIVILEGE_SIGNAL_NOT_PROOF",
    )
