"""Offline R14-to-R13 bridge; never grants financial or audit authority."""
from __future__ import annotations

from .identity import TenantPrincipal, require_tenant

MAX_METADATA_BYTES = 20 * 1024 * 1024


def register_metadata(adapter, db_path: str, *, principal: TenantPrincipal,
                      source_label: str, content_sha256: str,
                      size_bytes: int, idempotency_key: str) -> dict:
    tenant_id = require_tenant(principal)
    if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or not (0 <= size_bytes <= MAX_METADATA_BYTES):
        raise ValueError("invalid size_bytes")
    record = adapter.register_intake(db_path, tenant_id=tenant_id,
                                     source_label=source_label,
                                     content_sha256=content_sha256,
                                     size_bytes=size_bytes,
                                     idempotency_key=idempotency_key)
    if record.get("tenant_id") != tenant_id or record.get("status") != "QUARANTINED" or record.get("authority") != "NONE":
        raise RuntimeError("intake invariant violation")
    return record


def retrieve_metadata(adapter, db_path: str, *, principal: TenantPrincipal,
                      record_id: str) -> dict | None:
    return adapter.get_intake(db_path, tenant_id=require_tenant(principal), record_id=record_id)
