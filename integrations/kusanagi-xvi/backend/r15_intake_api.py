"""R15-A candidate: disabled-by-default tenant-scoped metadata API.

Requires existing service bearer on router mount, and separate tenant token.
No upload, model call, or authority elevation.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from r14.identity import IntakeAuthorizationError, resolve_principal
from r14 import service

try:
    from . import intake_adapter, store
except ImportError:
    import intake_adapter  # type: ignore[no-redef]
    import store  # type: ignore[no-redef]

router = APIRouter(prefix="/v1/intake", tags=["intake"])


class MetadataRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_label: str = Field(min_length=1, max_length=256)
    content_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    size_bytes: int = Field(ge=0, le=20 * 1024 * 1024)


def _principal(tenant_authorization: str):
    if os.getenv("AUREX_R15_INTAKE_ENABLED", "").lower() != "true":
        raise HTTPException(503, "intake disabled; HOLD")
    if not tenant_authorization.startswith("Bearer "):
        raise HTTPException(401, "unauthorized")
    token = tenant_authorization[7:]
    try:
        # Offline staging only: configuration is server-controlled; no tenant IDs
        # or credential mappings are accepted from client request data.
        raw = os.environ.get("AUREX_R15_TENANT_TOKEN_MAP", "")
        mapping = json.loads(raw) if raw else {}
        if not isinstance(mapping, dict):
            raise ValueError("invalid mapping")
        return resolve_principal(presented_token=token, token_hash_to_tenant=mapping)
    except (ValueError, TypeError, IntakeAuthorizationError):
        raise HTTPException(401, "unauthorized") from None


@router.post("/metadata", status_code=201)
def register_metadata(body: MetadataRequest,
                      tenant_authorization: Annotated[str, Header()] = "",
                      idempotency_key: Annotated[str, Header()] = ""):
    principal = _principal(tenant_authorization)
    try:
        return service.register_metadata(
            intake_adapter, store.path_from_env(), principal=principal,
            source_label=body.source_label, content_sha256=body.content_sha256,
            size_bytes=body.size_bytes, idempotency_key=idempotency_key,
        )
    except ValueError:
        raise HTTPException(422, "invalid intake metadata") from None


@router.get("/metadata/{record_id}")
def get_metadata(record_id: str, tenant_authorization: Annotated[str, Header()] = ""):
    principal = _principal(tenant_authorization)
    if not (1 <= len(record_id) <= 128 and all(c.isalnum() or c in "-_" for c in record_id)):
        raise HTTPException(422, "invalid record id")
    result = service.retrieve_metadata(intake_adapter, store.path_from_env(), principal=principal, record_id=record_id)
    if result is None:
        raise HTTPException(404, "record not found")
    return result
