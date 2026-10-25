"""Offline R13 intake adapter. No HTTP route or deployment authority."""

from __future__ import annotations

from . import store


def register_intake(
    db_path: str,
    *,
    tenant_id: str,
    source_label: str,
    content_sha256: str,
    size_bytes: int,
    idempotency_key: str,
) -> dict:
    from sovereign_intake import storage

    with store.connect(db_path) as connection:
        return storage.register(
            connection,
            tenant_id=tenant_id,
            source_label=source_label,
            content_sha256=content_sha256,
            size_bytes=size_bytes,
            idempotency_key=idempotency_key,
        )


def get_intake(
    db_path: str,
    *,
    tenant_id: str,
    record_id: str,
) -> dict | None:
    from sovereign_intake import storage

    with store.connect(db_path) as connection:
        return storage.get_for_tenant(connection, tenant_id, record_id)
