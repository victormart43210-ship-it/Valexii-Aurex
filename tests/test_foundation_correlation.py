"""Regression tests for AUREX request correlation."""

from fastapi.testclient import TestClient

from aurex.api import app


def test_health_generates_request_id():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_valid_request_id_preserved():
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "AUREX-TEST-12345678"},
        )

    assert response.headers["x-request-id"] == "AUREX-TEST-12345678"


def test_invalid_request_id_replaced():
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "invalid id"},
        )

    assert response.headers["x-request-id"] != "invalid id"


def test_unauthenticated_request_remains_protected():
    with TestClient(app) as client:
        response = client.get("/v1/jobs")

    assert response.status_code in (401, 500)
    assert response.headers.get("x-request-id")
