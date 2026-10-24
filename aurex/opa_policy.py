"""Open Policy Agent (OPA) feature-gated authorization evaluator for AUREX/OX.

Provides declarative policy evaluation for API routes, tenant scopes, and lease status,
strictly enforcing AI self-authorization prohibitions and $0 financial authority.

Feature-gated behind AUREX_ENABLE_OPA environment variable (default: 0 / disabled).
"""

from __future__ import annotations

import os
from typing import Any

OPA_ENABLED_ENV = "AUREX_ENABLE_OPA"


def is_opa_enabled() -> bool:
    """Return True if OPA policy evaluation is enabled via environment variable."""
    return os.environ.get(OPA_ENABLED_ENV) == "1"


def evaluate_authorization_policy(
    subject: dict[str, Any],
    action: str,
    resource: dict[str, Any],
    environment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate an authorization request against AUREX Rego-equivalent governance rules.

    Denies unconditionally if:
      - Subject claims model/AI identity self-grant (is_ai_self_grant=True or subject_type='model')
      - Request attempts financial execution or budget increase > $0
      - Cross-tenant or unauthorized scope access is attempted
      - Lease or token is expired
    """

    # Invariant 1: AI models cannot grant themselves execution or release authority
    sub_type = str(subject.get("type", "")).lower()
    if sub_type in ("model", "agent", "llm") or subject.get("is_ai_self_grant") is True:
        return {
            "allowed": False,
            "decision": "DENY",
            "reason": "AI model self-authorization prohibited",
            "authority": "NONE",
        }

    # Invariant 2: Financial spend or release authority above $0 is forbidden
    financial_usd = float(resource.get("max_cost_usd", 0.0) or resource.get("reservation_usd", 0.0))
    if financial_usd > 0.0 or resource.get("financial_release") is True:
        return {
            "allowed": False,
            "decision": "DENY",
            "reason": "Financial spend or release authority above $0 is forbidden",
            "authority": "NONE",
        }

    # Rule 1: Public read-only endpoints (e.g. /v1/health)
    if action == "GET" and resource.get("path") in ("/v1/health", "/health"):
        return {
            "allowed": True,
            "decision": "ALLOW_PUBLIC_READ",
            "reason": "Public health endpoint accessible",
            "authority": "NONE",
        }

    # Rule 2: Authenticated owner actions
    is_authenticated = subject.get("authenticated") is True
    role = subject.get("role", "anonymous")

    if not is_authenticated:
        return {
            "allowed": False,
            "decision": "DENY_UNAUTHENTICATED",
            "reason": "Authentication required for requested resource",
            "authority": "NONE",
        }

    # Check tenant isolation
    tenant_id = subject.get("tenant_id")
    resource_tenant = resource.get("tenant_id")
    if resource_tenant and tenant_id != resource_tenant and role != "owner":
        return {
            "allowed": False,
            "decision": "DENY_CROSS_TENANT",
            "reason": "Cross-tenant resource access denied",
            "authority": "NONE",
        }

    # Check lease expiry if resource is a leased job
    if resource.get("lease_expired") is True:
        return {
            "allowed": False,
            "decision": "DENY_EXPIRED_LEASE",
            "reason": "Worker lease expired or superseded",
            "authority": "NONE",
        }

    # Scope verification for DISPATER vs Admin actions
    required_scope = resource.get("required_scope")
    user_scopes = set(subject.get("scopes", []))

    if required_scope and required_scope not in user_scopes and role != "owner":
        return {
            "allowed": False,
            "decision": "DENY_INSUFFICIENT_SCOPE",
            "reason": f"Required scope '{required_scope}' missing",
            "authority": "NONE",
        }

    return {
        "allowed": True,
        "decision": "ALLOW_AUTHORIZED",
        "reason": "Authorization cleared by policy",
        "authority": "NONE",
    }
