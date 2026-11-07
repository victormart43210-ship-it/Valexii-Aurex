"""Local audit-replay manifest. Created-at is metadata and is outside the digest.

This is the REANA-style reproducibility contract from PR #179, without deploying
REANA. HMAC receipts stay in the DISPATER receipt module.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def audit_replay_manifest(
    *,
    tenant_pseudonym: str,
    audit_run_id: str,
    source_digests: list[str],
    rule_pack_digest: str,
    code_commit: str,
    output_digest: str,
    created_at: str,
) -> dict[str, Any]:
    """Same inputs produce the same manifest digest. ``created_at`` is excluded."""
    payload = {
        "schema_version": "aurex.ox.replay.v1",
        "tenant_pseudonym": tenant_pseudonym,
        "audit_run_id": audit_run_id,
        "source_digest_set": sorted(source_digests),
        "rule_pack_digest": rule_pack_digest,
        "code_commit": code_commit,
        "output_digest": output_digest,
        "financial_authority": "NONE",
        "model_id": None,
    }
    return {**payload, "created_at": created_at, "manifest_digest": _sha(payload)}
