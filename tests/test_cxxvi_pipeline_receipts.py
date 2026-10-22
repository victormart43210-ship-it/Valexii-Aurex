"""End-to-end, zero-cost contract test for HTTP -> lease -> SQLite -> evidence -> receipt.

Fictional fixed SQLite probe only. Not a production audit accuracy test.
"""
from __future__ import annotations

import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

import aurex.api as api
from aurex.database import get_job

TOKEN = "r" * 40
AUTH = {"Authorization": f"Bearer {TOKEN}"}
BODY = {"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"}, "maxCostUsd": 0}


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    db_path = str(tmp_path / "receipt_test.sqlite3")
    monkeypatch.setattr(api, "DEFAULT_DB_PATH", db_path)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    with TestClient(api.app) as client:
        yield client, db_path


def _execute(client: TestClient) -> str:
    response = client.post(
        "/v1/jobs", json=BODY, headers={**AUTH, "Idempotency-Key": "receipt-probe-v1-00001"},
    )
    assert response.status_code == 200
    assert response.json()["state"] == "succeeded"
    return str(response.json()["id"])


def test_authenticated_end_to_end_receipt_and_safe_replay(pipeline) -> None:
    client, db_path = pipeline
    job_id = _execute(client)
    result = client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH)
    assert result.status_code == 200
    data = result.json()
    assert data["jobId"] == job_id
    assert data["state"] == "succeeded"
    assert data["integrity"] == "RECORDED"
    assert (data["verification"], data["authority"], data["release"]) == (
        "NOT VERIFIED", "NONE", "HOLD",
    )
    assert data["observation"]["probe"] == "sqlite_roundtrip_v1"
    assert data["observation"]["passed"] is True
    assert get_job(db_path, job_id)["evidence_id"] == data["evidenceId"]
    assert client.get("/v1/evidence", headers=AUTH).json()["evidence"][0]["sha256"] == data["sha256"]
    replay = client.post("/v1/jobs", json=BODY, headers={
        **AUTH, "Idempotency-Key": "receipt-probe-v1-00001",
    })
    assert replay.status_code == 200 and replay.json()["id"] == job_id
    assert client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH).json() == data
    assert len(client.get("/v1/jobs", headers=AUTH).json()["jobs"]) == 1


def test_receipt_requires_valid_bearer_and_existing_id(pipeline) -> None:
    client, _ = pipeline
    job_id = _execute(client)
    for headers in ({}, {"Authorization": "Bearer invalid"}, {"Authorization": "Basic " + TOKEN}):
        assert client.get(f"/v1/jobs/{job_id}/receipt", headers=headers).status_code == 401
    assert client.get("/v1/jobs/job-abcdef012345abcdef012345/receipt", headers=AUTH).status_code == 404
    assert client.get("/v1/jobs/../../health/receipt", headers=AUTH).status_code in (404, 409)
    assert client.get("/v1/jobs/not-an-id/receipt", headers=AUTH).status_code == 409


def test_sqlite_evidence_tamper_fails_closed(pipeline) -> None:
    client, db_path = pipeline
    job_id = _execute(client)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE evidence_records SET sha256=? WHERE id=?",
            ("0" * 64, get_job(db_path, job_id)["evidence_id"]),
        )
    response = client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH)
    assert response.status_code == 409
    assert "observation" not in response.text.lower()
    assert "0" * 64 not in response.text


def test_spurious_observation_fields_are_not_leaked(pipeline) -> None:
    client, db_path = pipeline
    job_id = _execute(client)
    job = get_job(db_path, job_id)
    payload = job["result"]
    payload["observation"]["customer_account_number"] = "DO_NOT_EXPOSE"
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE jobs SET result_json=? WHERE id=?", (json.dumps(payload), job_id))
    response = client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH)
    assert response.status_code == 409
    assert "DO_NOT_EXPOSE" not in response.text


def test_disabled_lab_does_not_create_receipt(pipeline, monkeypatch) -> None:
    client, db_path = pipeline
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "0")
    response = client.post("/v1/jobs", json=BODY, headers={
        **AUTH, "Idempotency-Key": "receipt-disabled-v1-001",
    })
    assert response.status_code == 503
    assert client.get("/v1/jobs", headers=AUTH).json()["jobs"] == []
    with sqlite3.connect(db_path) as conn:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='evidence_records'",
        ).fetchone()
        if exists:
            assert conn.execute("SELECT count(*) FROM evidence_records").fetchone()[0] == 0
