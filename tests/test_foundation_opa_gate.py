"""OPA policy review must fail closed before job creation."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from aurex.api import app
from aurex_foundation.opa import PolicyResult


def test_opa_denial_blocks_job_creation(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "x" * 40)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    monkeypatch.setenv("AUREX_OPA_PILOT_ENABLED", "1")
    monkeypatch.setenv("AUREX_OPA_OPERATOR_APPROVED", "1")
    monkeypatch.setenv("AUREX_OPA_SYNTHETIC_ONLY", "1")

    with (
        patch("aurex.api.evaluate_policy", return_value=PolicyResult("HOLD", "denied")),
        patch("aurex.api.create_job") as create,
        TestClient(app) as client,
    ):
        response = client.post(
            "/v1/jobs",
            headers={
                "Authorization": "Bearer " + "x" * 40,
                "Idempotency-Key": "synthetic-policy-test-001",
            },
            json={
                "kind": "regression_scan",
                "params": {"probe": "sqlite_roundtrip_v1"},
                "maxCostUsd": 0,
            },
        )

    assert response.status_code == 503
    create.assert_not_called()


def test_opa_missing_approval_blocks_execution(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "x" * 40)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    monkeypatch.setenv("AUREX_OPA_PILOT_ENABLED", "1")
    monkeypatch.delenv("AUREX_OPA_OPERATOR_APPROVED", raising=False)
    monkeypatch.setenv("AUREX_OPA_SYNTHETIC_ONLY", "1")

    with (
        patch("aurex.api.evaluate_policy") as evaluate,
        patch("aurex.api.create_job") as create,
        TestClient(app) as client,
    ):
        response = client.post(
            "/v1/jobs",
            headers={
                "Authorization": "Bearer " + "x" * 40,
                "Idempotency-Key": "synthetic-policy-test-002",
            },
            json={
                "kind": "regression_scan",
                "params": {"probe": "sqlite_roundtrip_v1"},
                "maxCostUsd": 0,
            },
        )

    assert response.status_code == 503
    evaluate.assert_not_called()
    create.assert_not_called()


def test_opa_unavailable_blocks_execution(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "x" * 40)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    monkeypatch.setenv("AUREX_OPA_PILOT_ENABLED", "1")
    monkeypatch.setenv("AUREX_OPA_OPERATOR_APPROVED", "1")
    monkeypatch.setenv("AUREX_OPA_SYNTHETIC_ONLY", "1")

    with (
        patch(
            "aurex.api.evaluate_policy",
            return_value=PolicyResult("HOLD", "opa_unavailable_or_invalid"),
        ),
        patch("aurex.api.create_job") as create,
        TestClient(app) as client,
    ):
        response = client.post(
            "/v1/jobs",
            headers={
                "Authorization": "Bearer " + "x" * 40,
                "Idempotency-Key": "synthetic-policy-test-003",
            },
            json={
                "kind": "regression_scan",
                "params": {"probe": "sqlite_roundtrip_v1"},
                "maxCostUsd": 0,
            },
        )

    assert response.status_code == 503
    create.assert_not_called()
