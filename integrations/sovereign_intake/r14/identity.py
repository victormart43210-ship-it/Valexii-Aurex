"""Fail-closed tenant identity mapping for R14 intake.

This module intentionally does not interpret the existing AUREX service token as
an end-user/tenant identity. The caller must supply a trusted server-side
mapping, never a tenant ID taken from an HTTP request.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Mapping
from dataclasses import dataclass

_TENANT_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}\Z")


class IntakeAuthorizationError(PermissionError):
    pass


@dataclass(frozen=True)
class TenantPrincipal:
    tenant_id: str
    subject: str


def resolve_principal(*, presented_token: str | None,
                      token_hash_to_tenant: Mapping[str, tuple[str, str]]) -> TenantPrincipal:
    """Resolve a trusted tenant from a server-owned SHA256(token) mapping.

    This is an offline boundary primitive, NOT a complete credential lifecycle.
    No raw token, hash, or principal is logged. Caller must provide TLS, secret
    storage, token rotation/revocation, throttling, and request authentication.
    """
    if not isinstance(presented_token, str) or not (16 <= len(presented_token) <= 4096):
        raise IntakeAuthorizationError("unauthorized")
    if not token_hash_to_tenant:
        raise IntakeAuthorizationError("unauthorized")
    digest = hashlib.sha256(presented_token.encode("utf-8")).hexdigest()
    matched = None
    for key, principal in token_hash_to_tenant.items():
        if isinstance(key, str) and len(key) == 64 and hmac.compare_digest(digest, key):
            matched = principal
    if not isinstance(matched, tuple) or len(matched) != 2:
        raise IntakeAuthorizationError("unauthorized")
    tenant_id, subject = matched
    if not isinstance(tenant_id, str) or not _TENANT_RE.fullmatch(tenant_id):
        raise IntakeAuthorizationError("unauthorized")
    if not isinstance(subject, str) or not (1 <= len(subject) <= 128):
        raise IntakeAuthorizationError("unauthorized")
    return TenantPrincipal(tenant_id=tenant_id, subject=subject)


def require_tenant(principal: TenantPrincipal, requested_tenant: str | None = None) -> str:
    """Enforce trusted tenant scope; never default to a request's tenant ID."""
    if not isinstance(principal, TenantPrincipal) or not _TENANT_RE.fullmatch(principal.tenant_id):
        raise IntakeAuthorizationError("unauthorized")
    if requested_tenant is not None and not hmac.compare_digest(principal.tenant_id, requested_tenant):
        raise IntakeAuthorizationError("unauthorized")
    return principal.tenant_id
