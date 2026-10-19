"""KUSANAGI II Website Contract & Durable Job Workflow Tests."""

import pytest
from fastapi.testclient import TestClient

VALID_TOKEN = "a" * 32


@pytest.fixture(autouse=True)
def setup_env(monkeypatch, tmp_path):
    db_file = str(tmp_path / "test_jobs.db")
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", VALID_TOKEN)
    monkeypatch.setenv("AUREX_DB_PATH", db_file)
    import aurex.api
    aurex.api.DEFAULT_DB_PATH = db_file


def test_health_public():
    from aurex.api import app
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_v1_health_requires_service_authentication():
    from aurex.api import app
    client = TestClient(app)
    assert client.get("/v1/health").status_code == 401
    assert client.get("/v1/health", headers={"Authorization": "Bearer wrong"}).status_code == 401
    result = client.get("/v1/health", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert result.status_code == 200
    assert result.json()["status"] == "ok"


def test_unauthenticated_request_denied(monkeypatch):
    from aurex.api import app
    client = TestClient(app)
    res = client.get("/v1/capabilities")
    assert res.status_code == 401


def test_invalid_token_denied():
    from aurex.api import app
    client = TestClient(app)
    res = client.get("/v1/capabilities", headers={"Authorization": "Bearer wrong_token_that_is_long_enough_32chars"})
    assert res.status_code == 401


def test_valid_token_allows_access():
    from aurex.api import app
    client = TestClient(app)
    res = client.get("/v1/capabilities", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert res.status_code == 200
    assert "capabilities" in res.json()


def test_unavailable_worker_creates_no_job_or_evidence():
    from aurex.api import app

    client = TestClient(app)
    auth = {"Authorization": f"Bearer {VALID_TOKEN}"}

    response = client.post(
        "/v1/jobs",
        json={
            "kind": "regression_scan",
            "params": {"suite": "quick"},
            "maxCostUsd": 0.0,
        },
        headers=auth,
    )

    assert response.status_code == 503
    assert "worker unavailable" in response.json()["detail"].lower()

    jobs = client.get("/v1/jobs", headers=auth)
    evidence = client.get("/v1/evidence", headers=auth)

    assert jobs.status_code == 200
    assert evidence.status_code == 200
    assert jobs.json()["jobs"] == []
    assert evidence.json()["evidence"] == []



def test_unavailable_worker_does_not_create_idempotent_jobs():
    from aurex.api import app

    client = TestClient(app)
    auth = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Idempotency-Key": "idem-key-101",
    }

    payload = {
        "kind": "regression_scan",
        "params": {"suite": "quick"},
        "maxCostUsd": 0.0,
    }

    first = client.post("/v1/jobs", json=payload, headers=auth)
    second = client.post("/v1/jobs", json=payload, headers=auth)

    assert first.status_code == 503
    assert second.status_code == 503

    jobs = client.get("/v1/jobs", headers=auth)

    assert jobs.status_code == 200
    assert jobs.json()["jobs"] == []



def test_paid_job_rejected():
    from aurex.api import app
    client = TestClient(app)
    auth_header = {"Authorization": f"Bearer {VALID_TOKEN}"}
    res = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 5.0},
        headers=auth_header,
    )
    assert res.status_code == 402


def test_nonexistent_job_cannot_be_cancelled():
    from aurex.api import app

    client = TestClient(app)
    auth = {"Authorization": f"Bearer {VALID_TOKEN}"}

    response = client.post(
        "/v1/jobs/nonexistent-job/cancel",
        headers=auth,
    )

    assert response.status_code == 404

    jobs = client.get("/v1/jobs", headers=auth)

    assert jobs.status_code == 200
    assert jobs.json()["jobs"] == []
