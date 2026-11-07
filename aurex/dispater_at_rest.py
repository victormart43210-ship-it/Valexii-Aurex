"""Optional AES-GCM envelope for a stored DISPATER report blob.

The key is a server secret. Whoever can read that secret can decrypt the blob.
This is not customer-exclusive encryption and it is not zero-knowledge.
Finding columns and monitor rows are not covered.

Configuration, never committed:
- AUREX_DISPATER_DATA_KEYS: JSON object {key_id: hex key, 32 bytes}
- AUREX_DISPATER_DATA_ACTIVE_KID: key id for new envelopes
"""

from __future__ import annotations

import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AtRestError(RuntimeError):
    """The report envelope cannot be opened. Callers fail closed."""


def encryption_status() -> str:
    """NOT_CONFIGURED unless an active 32-byte key is present. An empty object is not configured."""
    try:
        keys = _keys()
    except AtRestError:
        return "NOT_CONFIGURED"
    kid = os.environ.get("AUREX_DISPATER_DATA_ACTIVE_KID", "")
    if kid not in keys:
        return "NOT_CONFIGURED"
    return "SERVER_KEY_AESGCM"


def _keys() -> dict[str, bytes]:
    raw = os.environ.get("AUREX_DISPATER_DATA_KEYS")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        keys = {str(key): bytes.fromhex(str(value)) for key, value in parsed.items()}
    except (ValueError, AttributeError, TypeError) as exc:
        raise AtRestError("at-rest keys are malformed") from exc
    if any(len(value) != 32 for value in keys.values()):
        raise AtRestError("at-rest keys must be 32 bytes")
    return keys


def protect_text(plain: str) -> str:
    """Return plaintext when no data key is configured. Never logs the key."""
    keys = _keys()
    if not keys:
        return plain
    kid = os.environ.get("AUREX_DISPATER_DATA_ACTIVE_KID", "")
    key = keys.get(kid)
    if key is None:
        raise AtRestError("active at-rest key id is not configured")
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, plain.encode("utf-8"), kid.encode("utf-8"))
    return json.dumps(
        {
            "ct": base64.b64encode(ciphertext).decode("ascii"),
            "enc": "AES-GCM",
            "kid": kid,
            "nonce": base64.b64encode(nonce).decode("ascii"),
        },
        sort_keys=True,
    )


def reveal_text(stored: str) -> str:
    """Open an envelope. A plaintext report without an envelope is returned as stored."""
    try:
        parsed = json.loads(stored)
    except json.JSONDecodeError as exc:
        raise AtRestError("stored report is not JSON") from exc
    if not isinstance(parsed, dict) or "enc" not in parsed:
        return stored
    if parsed.get("enc") != "AES-GCM":
        raise AtRestError("unknown at-rest envelope")
    kid = str(parsed.get("kid", ""))
    key = _keys().get(kid)
    if key is None:
        raise AtRestError("at-rest key is unavailable")
    try:
        raw = AESGCM(key).decrypt(
            base64.b64decode(str(parsed.get("nonce", ""))),
            base64.b64decode(str(parsed.get("ct", ""))),
            kid.encode("utf-8"),
        )
    except Exception as exc:
        raise AtRestError("at-rest payload failed") from exc
    return raw.decode("utf-8")
