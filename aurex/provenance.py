"""Deterministic provenance utilities for public evidence artifacts."""

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fingerprint(value: Any) -> str:
    return sha256_hex(canonical_json(value))
