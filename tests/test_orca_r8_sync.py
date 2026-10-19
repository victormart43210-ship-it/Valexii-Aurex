"""Synthetic, exact-shape tests for the ORCA R8 owner telemetry boundary."""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

SERVICE = "s" * 40
PUSH = "p" * 40
PATH = "/v1/orca/r8/status"


@pytest.fixture()
def env(monkeypatch: pytest.MonkeyPatch, tmp_path):
    db_path = tmp_path / "private.sqlite3"
    monkeypatch.setenv("AUREX_DB_PATH", str(db_path))
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", SERVICE)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ORCA_PUSH_TOKEN", PUSH)
    monkeypatch.setenv("AUREX_ORCA_SYNC_ENABLED", "1")
    return db_path


def sample(seq: int = 1, run: str = "r8_run_20261018") -> dict[str, object]:
    return {
        "sourceId": "orca-r8",
        "runId": run,
        "sequence": seq,
        "observedAt": datetime.now(UTC).isoformat(),
        "status": "RUNNING",
        "completedBatches": 38,
        "totalBatches": 84,
        "rowsRemaining": 1088,
        "etaSeconds": 6180,
        "checkpointAgeSeconds": 83,
    }


def test_requires_explicit_opt_in(env, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AUREX_ORCA_SYNC_ENABLED")
    client = TestClient(app)
    assert client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + PUSH}).status_code == 503
    assert client.get(PATH, headers={"Authorization": "Bearer " + SERVICE}).status_code == 503


def test_auth_is_scoped_and_fail_closed(env):
    client = TestClient(app)
    assert client.post(PATH, json=sample()).status_code == 401
    assert client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + SERVICE}).status_code == 401
    assert client.get(PATH).status_code == 401
    assert client.get(PATH, headers={"Authorization": "Bearer " + PUSH}).status_code == 401
    r = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE})
    assert r.status_code == 200
    assert r.json()["state"] == "NO_DATA"


def test_ingest_and_read_only_safe_fields(env):
    client = TestClient(app)
    r = client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + PUSH})
    assert r.status_code == 200, r.text
    assert r.json()["result"] == "STORED_UNVERIFIED"
    data = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE}).json()
    assert data["state"] == "OBSERVED"
    assert data["snapshot"]["completedBatches"] == 38
    assert data["snapshot"]["totalBatches"] == 84
    assert data["snapshot"]["rowsRemaining"] == 1088
    assert data["authority"] == "NONE"
    assert data["evidenceStatus"] == "NOT VERIFIED"
    assert len(data["sha256"]) == 64


def test_replay_denied_and_latest_preserved(env):
    client = TestClient(app)
    auth = {"Authorization": "Bearer " + PUSH}
    assert client.post(PATH, json=sample(), headers=auth).status_code == 200
    assert client.post(PATH, json=sample(), headers=auth).status_code == 409
    newer = sample(2)
    assert client.post(PATH, json=newer, headers=auth).status_code == 200
    assert client.post(PATH, json=sample(1), headers=auth).status_code == 409
    assert client.get(PATH, headers={"Authorization": "Bearer " + SERVICE}).json()["snapshot"]["sequence"] == 2


@pytest.mark.parametrize(
    "key,value",
    [
        ("completedBatches", 85),
        ("totalBatches", 0),
        ("sourceId", "other"),
        ("runId", "../private_docs"),
        ("observedAt", "2026-10-18T10:00:00"),
        ("observedAt", "2000-01-01T00:00:00Z"),
        ("status", "VERIFIED"),
        ("etaSeconds", -1),
    ],
)
def test_bad_inputs_denied(env, key: str, value: object):
    data = sample()
    data[key] = value
    assert TestClient(app).post(
        PATH, json=data, headers={"Authorization": "Bearer " + PUSH}
    ).status_code == 422


def test_private_data_fields_and_large_input_denied(env):
    client = TestClient(app)
    data = sample()
    data["document_contents"] = "Sensitive text"
    assert client.post(PATH, json=data, headers={"Authorization": "Bearer " + PUSH}).status_code == 422
    big = json.dumps({**sample(), "raw_documents": "x" * 4096})
    assert client.post(
        PATH, content=big, headers={"Authorization": "Bearer " + PUSH}
    ).status_code == 413


def test_stale_data_never_displayed_as_live(env):
    client = TestClient(app)
    assert client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + PUSH}).status_code == 200
    conn = sqlite3.connect(str(env))
    with conn:
        conn.execute(
            "UPDATE orca_r8_status SET received_at = ?",
            ((datetime.now(UTC) - timedelta(minutes=10)).isoformat(),),
        )
    conn.close()
    state = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE}).json()
    assert state["state"] == "STALE"
    assert state["evidenceStatus"] == "NOT VERIFIED"


def test_new_run_must_be_newer(env):
    client = TestClient(app)
    auth = {"Authorization": "Bearer " + PUSH}
    assert client.post(PATH, json=sample(), headers=auth).status_code == 200
    older = sample(run="r8_run_another")
    older["observedAt"] = (datetime.now(UTC) - timedelta(minutes=2)).isoformat()
    assert client.post(PATH, json=older, headers=auth).status_code == 409
    next_run = sample(run="r8_run_next")
    next_run["observedAt"] = (datetime.now(UTC) + timedelta(seconds=2)).isoformat()
    assert client.post(PATH, json=next_run, headers=auth).status_code == 200


def test_backfilled_observation_never_becomes_live(env):
    client = TestClient(app)
    report = sample()
    report["observedAt"] = (datetime.now(UTC) - timedelta(minutes=5)).isoformat()
    stored = client.post(PATH, json=report, headers={"Authorization": "Bearer " + PUSH})
    assert stored.status_code == 200
    state = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE})
    assert state.status_code == 200
    assert state.json()["state"] == "STALE"
    assert state.headers["cache-control"] == "private, no-store"


def test_missing_db_path_fails_closed(env, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AUREX_DB_PATH")
    client = TestClient(app)
    state = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE})
    assert state.status_code == 503


def test_push_token_must_not_equal_service_token(env, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUREX_ORCA_PUSH_TOKEN", SERVICE)
    client = TestClient(app)
    response = client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + SERVICE})
    assert response.status_code == 503


def test_tampered_sqlite_payload_is_refused(env):
    client = TestClient(app)
    assert client.post(PATH, json=sample(), headers={"Authorization": "Bearer " + PUSH}).status_code == 200
    conn = sqlite3.connect(str(env))
    with conn:
        conn.execute("UPDATE orca_r8_status SET payload_json = ?", ('{"private":"leak"}',))
    conn.close()
    result = client.get(PATH, headers={"Authorization": "Bearer " + SERVICE})
    assert result.status_code == 503
    assert "leak" not in result.text
