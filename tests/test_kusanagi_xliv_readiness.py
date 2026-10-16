"""Regression tests for AUREX fail-closed execution readiness.

These checks prevent a UI or integration client from mistaking HTTP health
for an available execution worker.
"""

from fastapi.testclient import TestClient

from aurex.api import app

client = TestClient(app)
TOKEN = "x" * 40


def test_health_does_not_assert_execution_readiness(monkeypatch, tmp_path):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    import aurex.api as api

    monkeypatch.setattr(api, "DEFAULT_DB_PATH", str(tmp_path / "jobs.db"))
    assert client.get("/health").status_code == 200
    headers = {"Authorization": f"Bearer {TOKEN}"}
    capabilities = client.get("/v1/capabilities", headers=headers)
    assert capabilities.status_code == 200
    assert all(not item["available"] for item in capabilities.json()["capabilities"])
    job = client.post(
        "/v1/jobs",
        headers=headers,
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0},
    )
    assert job.status_code == 503
    assert client.get("/v1/jobs", headers=headers).json()["jobs"] == []
    assert client.get("/v1/evidence", headers=headers).json()["evidence"] == []


def test_execution_is_not_public(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    assert client.get("/v1/capabilities").status_code == 401
    assert client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0},
    ).status_code == 401


def test_paid_execution_is_rejected_before_worker(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    response = client.post(
        "/v1/jobs",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0.01},
    )
    assert response.status_code == 402
