"""Independent verifier for AUREX GET /v1/jobs/{job_id}/receipt payloads (CXXXI).

Pure, offline, stdlib-only. Recomputes the digest with the same canonical
serialization used by aurex/pipeline_receipts.py:
    sha256(json.dumps(observation, sort_keys=True).encode())
A matching digest proves consistency with the stored observation ONLY. It is not
proof of invoice accuracy. Authority stays NONE; release stays HOLD.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any

_JOB_ID = re.compile(r"job-[0-9a-f]{24}\Z")
_EVIDENCE_ID = re.compile(r"ev-[0-9a-f]{24}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

RECEIPT_FIELDS = frozenset({
    "jobId", "state", "evidenceId", "sha256", "observation",
    "integrity", "verification", "authority", "release",
})


class ReceiptError(ValueError):
    """Raised when a receipt fails independent verification (fail closed)."""


def canonical_digest(observation: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()


def verify_receipt(
    receipt: object,
    *,
    expected_job_id: str,
    expected_evidence_id: str | None = None,
) -> dict[str, str]:
    """Return a small verified summary or raise ReceiptError. Never returns authority."""
    if not _JOB_ID.fullmatch(expected_job_id):
        raise ReceiptError("expected job id malformed")
    if not isinstance(receipt, dict):
        raise ReceiptError("receipt is not an object")
    if set(receipt) != RECEIPT_FIELDS:
        raise ReceiptError("unexpected or missing receipt fields")
    if receipt["jobId"] != expected_job_id:
        raise ReceiptError("job id mismatch")
    if receipt["state"] != "succeeded":
        raise ReceiptError("receipt state is not succeeded")
    evidence_id = receipt["evidenceId"]
    if not isinstance(evidence_id, str) or not _EVIDENCE_ID.fullmatch(evidence_id):
        raise ReceiptError("evidence id missing or malformed")
    if expected_evidence_id is not None and evidence_id != expected_evidence_id:
        raise ReceiptError("evidence id mismatch")
    stored = receipt["sha256"]
    if not isinstance(stored, str) or not _SHA256.fullmatch(stored):
        raise ReceiptError("digest malformed")
    observation = receipt["observation"]
    if not isinstance(observation, dict) or not observation:
        raise ReceiptError("observation missing")
    try:
        recomputed = canonical_digest(observation)
    except (TypeError, ValueError):
        raise ReceiptError("observation not canonically serializable") from None
    if not hmac.compare_digest(stored, recomputed):
        raise ReceiptError("digest does not match observation")
    if receipt["integrity"] != "RECORDED":
        raise ReceiptError("integrity status unexpected")
    if receipt["verification"] != "NOT VERIFIED":
        raise ReceiptError("verification must remain NOT VERIFIED")
    if receipt["authority"] != "NONE":
        raise ReceiptError("authority must be NONE")
    if receipt["release"] != "HOLD":
        raise ReceiptError("release must be HOLD")
    return {
        "jobId": expected_job_id,
        "evidenceId": evidence_id,
        "sha256": recomputed,
        "digest_consistency": "PASS",
        "independent_verification": "NOT VERIFIED",
        "authority": "NONE",
        "release": "HOLD",
    }
