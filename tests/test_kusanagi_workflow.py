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


def test_health_authenticated():
    from aurex.api import app
    client = TestClient(app)
    res = client.get("/v1/health", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


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


def test_unavailable_worker_has_no_side_effects():
    from aurex.api import app
    client = TestClient(app)
    auth = {"Authorization": f"Bearer {VALID_TOKEN}", "Idempotency-Key": "repeated-request-101"}
    for _ in range(2):
        res = client.post("/v1/jobs", headers=auth, json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0})
        assert res.status_code == 503
    assert client.get("/v1/jobs", headers=auth).json()["jobs"] == []
    assert client.get("/v1/evidence", headers=auth).json()["evidence"] == []


def test_database_idempotency_preserves_single_job(tmp_path):
    from aurex.database import create_job, list_jobs
    db = str(tmp_path / "dedup.db")
    first = create_job(db, "one", "regression_scan", {}, "same-key")
    second = create_job(db, "two", "regression_scan", {}, "same-key")
    assert first["id"] == second["id"]
    assert len(list_jobs(db)) == 1


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


def test_job_cancellation():
    from aurex.api import app
    client = TestClient(app)
    auth_header = {"Authorization": f"Bearer {VALID_TOKEN}"}

    from aurex.api import DEFAULT_DB_PATH
    from aurex.database import create_job
    create_job(DEFAULT_DB_PATH, "queued-test", "regression_scan", {})
    job_id = "queued-test"

    res_cancel = client.post(f"/v1/jobs/{job_id}/cancel", headers=auth_header)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["state"] == "cancelled"
