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


def sign_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the report with receipt_auth and receipt_mac attached."""
    keys = _load_keys()
    kid = os.environ.get("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "")
    if kid not in keys:
        raise ReceiptKeyError("active receipt key id is not configured")
    signed = {k: v for k, v in report.items() if k not in ("receipt_auth", "receipt_mac")}
    signed["receipt_auth"] = {"alg": ALGORITHM, "kid": kid}
    signed["receipt_mac"] = _mac(keys[kid], signed)
    return signed


def sign_report_v2(report: dict[str, Any], *, run_id: str, created_at: str) -> dict[str, Any]:
    """Versioned receipt: run_id and created_at are inside the signed body.

    ``receipt_auth.v == 2`` is itself covered by the MAC, so a v2 receipt cannot be downgraded
    to look like a legacy one, and a receipt cannot be moved to another run or timestamp.
    """
    keys = _load_keys()
    kid = os.environ.get("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "")
    if kid not in keys:
        raise ReceiptKeyError("active receipt key id is not configured")
    signed = {k: v for k, v in report.items() if k not in ("receipt_auth", "receipt_mac")}
    signed["run_id"] = run_id
    signed["created_at"] = created_at
    signed["receipt_auth"] = {"alg": ALGORITHM, "kid": kid, "v": 2}
    signed["receipt_mac"] = _mac(keys[kid], signed)
    return signed


def receipt_version(report: dict[str, Any]) -> int:
    """1 for legacy receipts, 2 for versioned. Only meaningful after verify_mac() is True."""
    auth = report.get("receipt_auth")
    return 2 if isinstance(auth, dict) and auth.get("v") == 2 else 1


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
