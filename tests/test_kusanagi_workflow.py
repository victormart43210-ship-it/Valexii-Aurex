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
    res = client.get("/v1/health")
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


def test_durable_job_submission_executes_and_records_evidence():
    from aurex.api import app
    client = TestClient(app)
    auth_header = {"Authorization": f"Bearer {VALID_TOKEN}"}

    # Submit job
    res = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {"suite": "quick"}, "maxCostUsd": 0.0},
        headers=auth_header,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["kind"] == "regression_scan"
    assert data["state"] == "succeeded"
    job_id = data["id"]

    # Query job
    res_get = client.get(f"/v1/jobs/{job_id}", headers=auth_header)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == job_id

    # Query evidence
    res_ev = client.get("/v1/evidence", headers=auth_header)
    assert res_ev.status_code == 200
    ev_list = res_ev.json()["evidence"]
    assert len(ev_list) >= 1
    assert ev_list[0]["capabilityId"] == "regression_scan"


def test_idempotency_key_deduplication():
    from aurex.api import app
    client = TestClient(app)
    auth_header = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Idempotency-Key": "idem-key-101",
    }

    res1 = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {"suite": "quick"}, "maxCostUsd": 0.0},
        headers=auth_header,
    )
    assert res1.status_code == 200
    job1 = res1.json()

    res2 = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {"suite": "quick"}, "maxCostUsd": 0.0},
        headers=auth_header,
    )
    assert res2.status_code == 200
    assert res2.json()["id"] == job1["id"]


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

    res = client.post(
        "/v1/jobs",
        json={"kind": "regression_scan", "params": {}, "maxCostUsd": 0.0},
        headers=auth_header,
    )
    job_id = res.json()["id"]

    res_cancel = client.post(f"/v1/jobs/{job_id}/cancel", headers=auth_header)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["state"] == "cancelled"
