"""Second-key checkpoint for the DISPATER monitor chain.

The receipt key MACs each event. This file MACs the tenant head with a different
server key. A holder of only the receipt key cannot forge the checkpoint.

This is not an external witness. The same operating-system user who can edit the
database, this file, and both environment variables can still roll both back.
``EXTERNAL_ANCHOR`` therefore stays ``NOT_VERIFIED``.

Configuration, never committed:
- AUREX_DISPATER_ANCHOR_KEYS: JSON object {key_id: hex key, at least 32 bytes}
- AUREX_DISPATER_ANCHOR_ACTIVE_KID: key id for new checkpoints
- AUREX_DISPATER_ANCHOR_REVOKED_KIDS: optional comma-separated key ids that must fail
"""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import threading
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

EXTERNAL_ANCHOR = "NOT_VERIFIED"
_LOCK = threading.Lock()


class AnchorKeyError(RuntimeError):
    """Anchor keys are missing or invalid. Verification fails closed."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _keys() -> dict[str, bytes]:
    raw = os.environ.get("AUREX_DISPATER_ANCHOR_KEYS")
    if not raw:
        raise AnchorKeyError("anchor keys are not configured")
    try:
        parsed = json.loads(raw)
        keys = {str(key): bytes.fromhex(str(value)) for key, value in parsed.items()}
    except (ValueError, AttributeError, TypeError) as exc:
        raise AnchorKeyError("anchor keys are malformed") from exc
    if not keys or any(len(value) < 32 for value in keys.values()):
        raise AnchorKeyError("anchor keys are missing or too short")
    return keys


def _active() -> tuple[str, bytes]:
    keys = _keys()
    kid = os.environ.get("AUREX_DISPATER_ANCHOR_ACTIVE_KID", "")
    if kid not in keys:
        raise AnchorKeyError("active anchor key id is not configured")
    key = keys[kid]
    raw = os.environ.get("AUREX_DISPATER_RECEIPT_KEYS", "")
    if raw:
        try:
            receipt_keys = json.loads(raw)
        except ValueError:
            receipt_keys = {}
        if isinstance(receipt_keys, dict):
            for value in receipt_keys.values():
                try:
                    other = bytes.fromhex(str(value))
                except ValueError:
                    continue
                if len(other) == len(key) and hmac.compare_digest(other, key):
                    raise AnchorKeyError("anchor key must not reuse the receipt key")
    return kid, key


def require_configured() -> None:
    """Fail before a monitor row is written when the checkpoint key is unusable."""
    _active()


def _revoked() -> set[str]:
    raw = os.environ.get("AUREX_DISPATER_ANCHOR_REVOKED_KIDS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _path() -> Path:
    from aurex.dispater_store import db_path

    return Path(str(db_path()) + ".anchor.json")


def _read(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text())
    if not isinstance(loaded, dict):
        raise AnchorKeyError("anchor file is not an object")
    return loaded


def _write(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True))
    temporary.replace(path)


def _exclusive(path: Path, action: Callable[[], None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            action()
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def note_head(tenant_id: str, head: str, count: int) -> None:
    """Record the current head. The generation id is kept from the first note."""
    kid, key = _active()
    if kid in _revoked():
        raise AnchorKeyError("active anchor key is revoked")
    path = _path()

    def _record() -> None:
        current = _read(path) if path.exists() else {}
        previous = current.get(tenant_id)
        generation = previous.get("generation") if isinstance(previous, dict) else None
        if not isinstance(generation, str) or len(generation) < 8:
            generation = uuid.uuid4().hex
        body = {
            "count": count,
            "generation": generation,
            "head": head,
            "seq": count,
            "tenant_id": tenant_id,
        }
        mac = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
        current[tenant_id] = {**body, "kid": kid, "mac": mac}
        _write(path, current)

    with _LOCK:
        _exclusive(path, _record)


def clear_tenant(tenant_id: str) -> None:
    """Drop one tenant after an authorized full purge. This does not delete other tenants."""
    path = _path()

    def _drop() -> None:
        if not path.exists():
            return
        current = _read(path)
        current.pop(tenant_id, None)
        _write(path, current)

    with _LOCK:
        _exclusive(path, _drop)


def anchor_agrees(tenant_id: str, events: list[dict[str, Any]]) -> bool:
    """True when the checkpoint matches the stored events, or neither exists yet.

    An empty event list with a surviving checkpoint is erasure and returns False.
    Deleting the checkpoint and the events together is not detectable here.
    """
    path = _path()
    try:
        stored = _read(path).get(tenant_id) if path.exists() else None
    except (OSError, ValueError, AnchorKeyError):
        return False
    if not events:
        return stored is None
    if not isinstance(stored, dict):
        return False
    kid = str(stored.get("kid", ""))
    if kid in _revoked():
        return False
    try:
        key = _keys().get(kid)
    except AnchorKeyError:
        return False
    if key is None:
        return False
    body = {
        "count": stored.get("count"),
        "generation": stored.get("generation"),
        "head": stored.get("head"),
        "seq": stored.get("seq"),
        "tenant_id": tenant_id,
    }
    expected = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(stored.get("mac", ""))):
        return False
    return (
        stored.get("head") == events[-1]["entry_sha256"]
        and stored.get("count") == len(events)
        and stored.get("seq") == len(events)
    )
