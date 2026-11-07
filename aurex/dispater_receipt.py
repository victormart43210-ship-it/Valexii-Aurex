"""Keyed (HMAC-SHA256) authenticity for stored DISPATER receipts.

The unkeyed ``receipt_sha256`` only detects accidental corruption: anyone with database
write access can edit a report and recompute it. ``receipt_auth``/``receipt_mac`` add a
MAC under a server-side key that the database does not hold.

Scope: this proves the stored report was produced by a holder of the key and not altered
since. It does NOT prove the underlying evidence was truthful, and it cannot protect against
an attacker who also holds the key (symmetric). Stronger audit guarantees need asymmetric
signatures or an independently anchored checkpoint.

Configuration (never commit key material):
- AUREX_DISPATER_RECEIPT_KEYS: JSON object {key_id: hex-encoded key, >= 32 bytes}
- AUREX_DISPATER_RECEIPT_ACTIVE_KID: key_id used for new receipts
Rotation: add the new key, switch the active kid; keep old keys until their receipts expire.
Missing/invalid configuration fails closed: nothing is signed and nothing verifies.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

ALGORITHM = "HMAC-SHA256"
MIN_KEY_BYTES = 32


class ReceiptKeyError(RuntimeError):
    """Receipt signing keys are missing or invalid."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _load_keys() -> dict[str, bytes]:
    raw = os.environ.get("AUREX_DISPATER_RECEIPT_KEYS")
    if not raw:
        raise ReceiptKeyError("receipt signing keys are not configured")
    try:
        parsed = json.loads(raw)
        keys = {str(k): bytes.fromhex(str(v)) for k, v in parsed.items()}
    except (ValueError, AttributeError) as exc:
        raise ReceiptKeyError("receipt signing keys are malformed") from exc
    if not keys or any(len(v) < MIN_KEY_BYTES for v in keys.values()):
        raise ReceiptKeyError("receipt signing keys are missing or too short")
    return keys


def _mac(key: bytes, report: dict[str, Any]) -> str:
    body = {k: v for k, v in report.items() if k != "receipt_mac"}
    return hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()


def _active_key() -> tuple[str, bytes]:
    keys = _load_keys()
    kid = os.environ.get("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "")
    if kid not in keys:
        raise ReceiptKeyError("active receipt key id is not configured")
    return kid, keys[kid]


def _content_digest(body: dict[str, Any]) -> str:
    raw = _canonical({k: v for k, v in body.items() if k not in ("receipt_sha256", "receipt_auth", "receipt_mac")})
    return hashlib.sha256(raw).hexdigest()


def sign_report(report: dict[str, Any]) -> dict[str, Any]:
    """Legacy receipt. Identity fields are not covered. Persistence uses :func:`seal_run`."""
    kid, key = _active_key()
    signed = {k: v for k, v in report.items() if k not in ("receipt_auth", "receipt_mac")}
    signed["receipt_auth"] = {"alg": ALGORITHM, "kid": kid}
    signed["receipt_mac"] = _mac(key, signed)
    return signed


def seal_run(report: dict[str, Any], *, run_id: str, created_at: str) -> dict[str, Any]:
    """Version 2 receipt. ``run_id`` and ``created_at`` are inside both the hash and the MAC.

    A stored v2 receipt is not rewritten into a legacy receipt. Removing ``v``, the identity
    fields, or ``receipt_binding`` changes the MAC and will not verify.
    """
    if not isinstance(run_id, str) or len(run_id) != 36 or not run_id.startswith("run-"):
        raise ValueError("run_id is not a canonical run identifier")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at is required")
    kid, key = _active_key()
    body = {
        k: v
        for k, v in report.items()
        if k not in ("receipt_sha256", "receipt_auth", "receipt_mac", "run_id", "created_at", "receipt_binding")
    }
    body["run_id"] = run_id
    body["created_at"] = created_at
    body["receipt_binding"] = "BOUND_V2"
    body["receipt_class"] = "SEALED_V2"
    body["receipt_sha256"] = _content_digest(body)
    body["receipt_auth"] = {"alg": ALGORITHM, "kid": kid, "v": 2}
    body["receipt_mac"] = _mac(key, body)
    return body


def receipt_version(report: dict[str, Any]) -> int | None:
    """1 legacy, 2 identity-bound. None is an unknown version and must be rejected."""
    auth = report.get("receipt_auth")
    if not isinstance(auth, dict) or "v" not in auth:
        return 1
    if auth.get("v") == 2:
        return 2
    return None


def mac_mapping(body: dict[str, Any]) -> tuple[str, str]:
    """MAC a canonical mapping with the active receipt key. This is not a human signature."""
    kid, key = _active_key()
    digest = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    return kid, digest


def verify_mapping_mac(body: dict[str, Any], *, kid: str, mac: str) -> bool:
    """True when ``mac`` matches ``body`` under a configured key. Never raises."""
    try:
        key = _load_keys().get(kid)
        if key is None or not isinstance(mac, str):
            return False
        expected = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, mac)
    except (ReceiptKeyError, TypeError, ValueError):
        return False


def verify_mac(report: dict[str, Any]) -> bool:
    """True only for a well-formed receipt whose MAC verifies under a known key. Never raises."""
    try:
        auth = report.get("receipt_auth")
        mac = report.get("receipt_mac")
        if not isinstance(auth, dict) or auth.get("alg") != ALGORITHM or not isinstance(mac, str):
            return False
        key = _load_keys().get(str(auth.get("kid")))
        if key is None:
            return False
        return hmac.compare_digest(_mac(key, report), mac)
    except (ReceiptKeyError, TypeError, ValueError):
        return False
