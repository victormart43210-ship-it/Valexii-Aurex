"""Opt-in offline lab contract; no model calls, no public execution."""
from fastapi.testclient import TestClient
from aurex.api import app
import aurex.api

TOKEN = "z" * 32

def test_offline_lab_opt_in_and_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setattr(aurex.api, "DEFAULT_DB_PATH", str(tmp_path / "lab.db"))
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"}, "maxCostUsd": 0}
    monkeypatch.delenv("AUREX_ENABLE_OFFLINE_LAB", raising=False)
    assert client.post("/v1/jobs", json=payload, headers=headers).status_code == 503
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    assert client.post("/v1/jobs", json={**payload, "params": {}}, headers=headers).status_code == 503
    assert client.post("/v1/jobs", json={**payload, "maxCostUsd": 1}, headers=headers).status_code == 402
    assert client.post("/v1/jobs", json={**payload, "kind": "hypothesis_test"}, headers=headers).status_code == 400
    first = client.post("/v1/jobs", json=payload, headers={**headers, "Idempotency-Key": "probe-key"})
    assert first.status_code == 200, first.text
    assert first.json()["state"] == "succeeded"
    second = client.post("/v1/jobs", json=payload, headers={**headers, "Idempotency-Key": "probe-key"})
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    jobs = client.get("/v1/jobs", headers=headers).json()["jobs"]
    evidence = client.get("/v1/evidence", headers=headers).json()["evidence"]
    assert len(jobs) == 1
    assert len(evidence) == 1
    assert len(evidence[0]["sha256"]) == 64
    assert "NOT independently verified" in evidence[0]["summary"]
