"""Customer lifecycle requests that do not delete or export beyond the tenant grant.

Deletion and retention changes are recorded as HOLD. Nothing is purged, no backup
is touched, and no legal hold is created. A passing request does not grant authority.
"""

from __future__ import annotations

import uuid
from typing import Any

from aurex.customer_sovereignty import assert_no_effect


def deletion_request(tenant_id: str) -> dict[str, Any]:
    assert_no_effect()
    return {
        "request_id": f"del-{uuid.uuid4().hex}",
        "tenant_id": tenant_id,
        "status": "HOLD",
        "effect": "NONE",
        "deletion": "NOT_EXECUTED",
        "reason": "DELETION_REQUIRES_SEPARATE_AUTHORIZATION",
        "backup_deletion": "NOT_IMPLEMENTED",
        "legal_hold": "NOT_IMPLEMENTED",
        "audit_record_retention": "NOT_IMPLEMENTED",
        "confirmed_recovery_usd": "0.00",
    }


def retention_request(tenant_id: str, *, retain_days: int) -> dict[str, Any]:
    assert_no_effect()
    if retain_days < 1 or retain_days > 3650:
        raise ValueError("retain_days is outside the accepted range")
    return {
        "request_id": f"ret-{uuid.uuid4().hex}",
        "tenant_id": tenant_id,
        "status": "HOLD",
        "effect": "NONE",
        "retain_days": retain_days,
        "enforcement": "NOT_IMPLEMENTED",
        "reason": "RETENTION_POLICY_NOT_ENFORCED",
        "backup_deletion": "NOT_IMPLEMENTED",
        "confirmed_recovery_usd": "0.00",
    }


def authorization_decision(authorization: dict[str, Any]) -> dict[str, Any]:
    """Describe an approval claim. The result is never a verified financial action."""
    assert_no_effect()
    required = ("actor_id", "action", "scope", "expires_at", "tenant_id")
    missing = [key for key in required if not str(authorization.get(key, "")).strip()]
    return {
        "verification": "UNVERIFIED",
        "effect": "NONE",
        "financial_action": "NONE",
        "third_party_contact": "NONE",
        "reason": "MISSING_AUTHORIZATION_FIELDS" if missing else "NO_IDENTITY_PROVIDER",
        "missing": missing,
    }
