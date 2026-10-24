"""Unit tests for Open Policy Agent (OPA) feature-gated authorization evaluator."""

from __future__ import annotations

import pytest

from aurex.opa_policy import evaluate_authorization_policy, is_opa_enabled


def test_opa_feature_flag_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUREX_ENABLE_OPA", raising=False)
    assert not is_opa_enabled()

    monkeypatch.setenv("AUREX_ENABLE_OPA", "1")
    assert is_opa_enabled()


def test_public_health_endpoint_allowed() -> None:
    res = evaluate_authorization_policy(
        subject={"authenticated": False, "role": "anonymous"},
        action="GET",
        resource={"path": "/v1/health"},
    )
    assert res["allowed"] is True
    assert res["decision"] == "ALLOW_PUBLIC_READ"


def test_ai_model_self_authorization_denied() -> None:
    res = evaluate_authorization_policy(
        subject={"type": "model", "is_ai_self_grant": True, "authenticated": True},
        action="POST",
        resource={"path": "/v1/jobs"},
    )
    assert res["allowed"] is False
    assert res["decision"] == "DENY"
    assert "self-authorization" in res["reason"]


def test_financial_spend_above_zero_denied() -> None:
    res = evaluate_authorization_policy(
        subject={"authenticated": True, "role": "owner"},
        action="POST",
        resource={"path": "/v1/jobs", "max_cost_usd": 5.00},
    )
    assert res["allowed"] is False
    assert res["decision"] == "DENY"
    assert "above $0 is forbidden" in res["reason"]


def test_cross_tenant_access_denied() -> None:
    res = evaluate_authorization_policy(
        subject={"authenticated": True, "role": "user", "tenant_id": "tenant_a"},
        action="GET",
        resource={"path": "/v1/jobs/123", "tenant_id": "tenant_b"},
    )
    assert res["allowed"] is False
    assert res["decision"] == "DENY_CROSS_TENANT"


def test_expired_lease_denied() -> None:
    res = evaluate_authorization_policy(
        subject={"authenticated": True, "role": "owner"},
        action="POST",
        resource={"path": "/v1/jobs/123", "lease_expired": True},
    )
    assert res["allowed"] is False
    assert res["decision"] == "DENY_EXPIRED_LEASE"


def test_scope_authorization_cleared() -> None:
    res = evaluate_authorization_policy(
        subject={
            "authenticated": True,
            "role": "user",
            "tenant_id": "dispater_tenant",
            "scopes": ["dispater:audit"],
        },
        action="GET",
        resource={"path": "/v1/dispater/records", "tenant_id": "dispater_tenant", "required_scope": "dispater:audit"},
    )
    assert res["allowed"] is True
    assert res["decision"] == "ALLOW_AUTHORIZED"
