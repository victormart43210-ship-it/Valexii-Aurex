"""R13 tenant-scoped intake metadata. Offline staging only."""

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


def initialize(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS intake_records (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            source_label TEXT NOT NULL,
            content_sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status = 'QUARANTINED'),
            authority TEXT NOT NULL CHECK(authority = 'NONE'),
            idempotency_key TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(tenant_id, idempotency_key)
        )
    """)


def register(
    connection,
    *,
    tenant_id,
    source_label,
    content_sha256,
    size_bytes,
    idempotency_key,
):
    if not all((tenant_id, source_label, content_sha256, idempotency_key)):
        raise ValueError("required intake fields missing")

    if (
        len(content_sha256) != 64
        or any(c not in "0123456789abcdef" for c in content_sha256)
    ):
        raise ValueError("invalid SHA-256")

    if not isinstance(size_bytes, int) or not 0 <= size_bytes <= 20 * 1024 * 1024:
        raise ValueError("invalid file size")


    # The caller must supply a dedicated connection with no active transaction.
    # BEGIN IMMEDIATE serializes writers before checking idempotency.
    if connection.in_transaction:
        raise ValueError("registration requires a fresh transaction")

    connection.execute("BEGIN IMMEDIATE")
    try:
        existing = connection.execute(
            """
            SELECT * FROM intake_records
            WHERE tenant_id = ? AND idempotency_key = ?
            """,
            (tenant_id, idempotency_key),
        ).fetchone()

        if existing:
            if (
                existing["source_label"] != source_label
                or existing["content_sha256"] != content_sha256
                or existing["size_bytes"] != size_bytes
            ):
                raise ValueError("idempotency conflict")

            result = dict(existing)
        else:
            record_id = uuid4().hex

            connection.execute(
                """
                INSERT INTO intake_records
                (id, tenant_id, source_label, content_sha256,
                 size_bytes, status, authority, idempotency_key, created_at)
                VALUES (?, ?, ?, ?, ?, 'QUARANTINED', 'NONE', ?, ?)
                """,
                (
                    record_id,
                    tenant_id,
                    source_label,
                    content_sha256,
                    size_bytes,
                    idempotency_key,
                    now(),
                ),
            )

            result = dict(
                connection.execute(
                    "SELECT * FROM intake_records WHERE id = ?",
                    (record_id,),
                ).fetchone()
            )

        connection.commit()
        return result

    except BaseException:
        connection.rollback()
        raise


def get_for_tenant(connection, tenant_id, record_id):
    row = connection.execute(
        """
        SELECT * FROM intake_records
        WHERE tenant_id = ? AND id = ?
        """,
        (tenant_id, record_id),
    ).fetchone()
    return dict(row) if row else None
