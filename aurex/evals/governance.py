"""Qualification from externally configured signed witnesses, never model assertions."""

import base64
import hashlib
import json
from datetime import datetime
from typing import Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["PASS", "FAIL", "HOLD", "NOT RUN", "NOT VERIFIED"]


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    answer: str
    status: Status = "NOT VERIFIED"
    evidence_ids: tuple[str, ...] = ()


class Witness(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    witness_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    claim_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    outcome: Status
    observed_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    signature: str

    def signing_bytes(self) -> bytes:
        return json.dumps(
            self.model_dump(mode="json", exclude={"signature"}),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()


class Qualification(BaseModel):
    status: Status
    reason: str
    evidence_ids: tuple[str, ...] = ()
    authority_granted: Literal[False] = False


def qualify(
    claim: Claim,
    witnesses: tuple[Witness, ...],
    trusted_keys: dict[str, Ed25519PublicKey],
    now: datetime,
    context_sha256: str,
) -> Qualification:
    """Keys come from the operator trust store, not the evaluated response/document.

    PASS means this signed claim has current supporting evidence. It does not grant
    product authority, certify the source's real-world truth, or erase old failures.
    """
    hold = Qualification(status="HOLD", reason="Missing or inadmissible independent evidence")
    if (
        now.tzinfo is None
        or not claim.evidence_ids
        or len(set(claim.evidence_ids)) != len(claim.evidence_ids)
    ):
        return hold
    if len({w.witness_id for w in witnesses}) != len(witnesses):
        return hold
    digest = hashlib.sha256(claim.answer.encode()).hexdigest()
    valid: dict[str, Witness] = {}
    conflict = False
    for w in witnesses:
        key = trusted_keys.get(w.source_id)
        if key is None:
            continue
        try:
            key.verify(base64.b64decode(w.signature, validate=True), w.signing_bytes())
        except (ValueError, InvalidSignature):
            continue
        if w.context_sha256 != context_sha256:
            continue
        dates = (w.observed_at, w.expires_at, w.revoked_at or now)
        if any(t.tzinfo is None for t in dates):
            continue
        if not (w.observed_at <= now < w.expires_at) or (w.revoked_at and w.revoked_at <= now):
            continue
        if (w.outcome == "FAIL" and w.claim_sha256 == digest) or (
            w.outcome == "PASS" and w.claim_sha256 != digest
        ):
            conflict = True
        if w.outcome == "PASS" and w.claim_sha256 == digest:
            valid[w.witness_id] = w
    if conflict:
        return Qualification(status="HOLD", reason="Conflicting or rejecting signed evidence")
    if any(e not in valid for e in claim.evidence_ids):
        return hold
    return Qualification(
        status="PASS", reason="Current signed supporting evidence", evidence_ids=claim.evidence_ids
    )
