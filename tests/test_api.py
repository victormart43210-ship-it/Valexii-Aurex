"""API endpoint integration tests."""

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

client = TestClient(app)
VALID_TOKEN = "a" * 32


@pytest.fixture(autouse=True)
def setup_token(monkeypatch, tmp_path):
    db_file = str(tmp_path / "test_api_jobs.db")
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", VALID_TOKEN)
    monkeypatch.setenv("AUREX_DB_PATH", db_file)
    import aurex.api
    aurex.api.DEFAULT_DB_PATH = db_file


def test_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_capabilities_endpoint() -> None:
    res = client.get("/v1/capabilities", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert res.status_code == 200
    data = res.json()
    assert "capabilities" in data


def test_jobs_submission_endpoint() -> None:
    res = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0.0},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )
    assert res.status_code == 503
    assert "worker unavailable" in res.json()["detail"].lower()
    jobs = client.get("/v1/jobs", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert jobs.status_code == 200
    assert jobs.json()["jobs"] == []
    evidence = client.get("/v1/evidence", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert evidence.status_code == 200
    assert evidence.json()["evidence"] == []


def test_evidence_summary_endpoint() -> None:
    res = client.get("/v1/evidence", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert res.status_code == 200
    assert "evidence" in res.json()
