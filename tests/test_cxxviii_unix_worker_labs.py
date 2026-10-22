"""CXXVIII zero-cost Unix worker, lease failure and Python lab regression tests."""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# The candidate is a deliberately independent deployable Python package
# under integrations/kusanagi-xvi, not imported by canonical aurex.api.
BRIDGE_DIR = Path(__file__).resolve().parents[1] / "integrations" / "kusanagi-xvi"
if str(BRIDGE_DIR) not in sys.path:
    sys.path.insert(0, str(BRIDGE_DIR))

store = importlib.import_module("backend.store")
worker = importlib.import_module("backend.worker")
agent = importlib.import_module("backend.agent")
supervisor = importlib.import_module("backend.supervisor")
lab = importlib.import_module("backend.lab")
app_module = importlib.import_module("backend.app")


@pytest.fixture
def database(tmp_path):
    db = str(tmp_path / "worker.sqlite3")
    store.initialize(db)
    return db


def _job(db: str, key: str = "unix-lab-job-key-0000001"):
    return store.create_job(db, "regression_scan", {"probe": "sqlite_roundtrip_v1"}, key)


def test_opt_in_worker_never_runs_without_flag(monkeypatch, database):
    _job(database)
    monkeypatch.delenv("AUREX_ENABLE_OFFLINE_LAB", raising=False)
    assert worker.once(db_path=database)["status"] == "HOLD"
    assert store.list_jobs(database)[0]["state"] == "queued"
    assert store.evidence(database) == []


def test_failure_clears_exact_lease_and_does_not_create_evidence(monkeypatch, database):
    _job(database)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "true")

    def fail(*args, **kwargs):
        raise RuntimeError("simulated probe failure")

    monkeypatch.setattr(store, "finalize", fail)
    result = worker.once(worker_id="test-worker-failed", db_path=database)
    assert result["status"] == "FAILED"
    assert result["authority"] == "NONE"
    assert store.list_jobs(database)[0]["state"] == "failed"
    assert store.evidence(database) == []
    with store.connect(database) as c:
        row = c.execute("SELECT lease_token,lease_expires_at,worker_id,result_json "
                        " ,lease_generation FROM jobs").fetchone()
        assert all(row[k] is None for k in ("lease_token", "lease_expires_at", "worker_id", "result_json"))
        assert row["lease_generation"] == 2


def test_stale_failed_worker_does_not_override_cancelled_job(monkeypatch, database):
    record = _job(database)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "true")

    def cancel_then_fail(*args, **kwargs):
        store.cancel(database, record["id"])
        raise RuntimeError("cancelled during probe")

    monkeypatch.setattr(store, "finalize", cancel_then_fail)
    r = worker.once(worker_id="cancelled-worker", db_path=database)
    assert r["status"] == "HOLD"
    assert store.get_job(database, record["id"])["state"] == "cancelled"
    assert store.evidence(database) == []


def test_stale_lease_cannot_revive_job(database):
    record = _job(database)
    old = store.claim(database, "worker-old")
    assert old
    with store.connect(database) as c:
        c.execute("UPDATE jobs SET lease_expires_at=? WHERE id=?",
                  ("2000-01-01T00:00:00+00:00", record["id"]))
    new = store.claim(database, "worker-new")
    assert new and new["lease_generation"] > old["lease_generation"]
    assert store.fail_claim(database, old, "worker-old") is None
    with pytest.raises(ValueError):
        store.finalize(database, old, "worker-old")
    assert store.finalize(database, new, "worker-new")["state"] == "succeeded"
    assert len(store.evidence(database)) == 1


def test_replay_and_cancel_are_fenced(database):
    first = _job(database)
    assert _job(database)["id"] == first["id"]
    taken = store.claim(database, "one-worker")
    assert taken
    assert store.cancel(database, first["id"])["state"] == "cancelled"
    assert store.fail_claim(database, taken, "one-worker") is None
    assert store.evidence(database) == []


def test_supervisor_config_and_optional_unix_children():
    with pytest.raises(ValueError):
        supervisor.validate_config({"AUREX_DB_PATH": ":memory:"})
    with pytest.raises(ValueError):
        supervisor.validate_config({"AUREX_DB_PATH": "relative.db"})
    with pytest.raises(ValueError):
        supervisor.validate_config({"AUREX_DB_PATH": "/tmp/c.db", "PORT": "0"})
    with pytest.raises(ValueError):
        supervisor.validate_config({"AUREX_DB_PATH": "/tmp/c.db", "PORT": "8080; echo unsafe"})
    with pytest.raises(ValueError):
        supervisor.validate_config(
            {"AUREX_DB_PATH": "/data/jobs.db", "AUREX_REQUIRED_VOLUME": "true"},
            mount_check=lambda _: False,
        )
    assert supervisor.validate_config({"AUREX_DB_PATH": "/data/jobs.db",
        "AUREX_REQUIRED_VOLUME": "true"}, mount_check=lambda _: True) == "/data/jobs.db"
    assert len(supervisor.child_commands({})) == 1
    enabled = supervisor.child_commands({
        "AUREX_ENABLE_OFFLINE_LAB": "true",
        "AUREX_OBSERVER_ENABLED": "true",
        "PORT": "8765",
    })
    assert len(enabled) == 3
    assert all("shell" not in " ".join(c) for c in enabled)
    assert any("backend.worker" in cmd for cmd in enabled)
    assert any("backend.agent" in cmd for cmd in enabled)
    assert enabled[-1][-2:] == ["8765", "--no-access-log"]


def test_python_labs_staged_and_executed_in_temporary_directory(tmp_path):
    env = os.environ.copy()
    env.pop("AUREX_ENABLE_OFFLINE_LAB", None)
    env.pop("AUREX_DB_PATH", None)
    env["PYTHONPATH"] = str(BRIDGE_DIR)
    root = Path(__file__).resolve().parents[1]
    staged = subprocess.run([sys.executable, "-m", "backend.lab"], cwd=root, env=env,
                            capture_output=True, text=True, check=True, timeout=20)
    obj = json.loads(staged.stdout)
    assert obj["status"] == "STAGED"
    executed = subprocess.run([sys.executable, "-m", "backend.lab", "--execute"],
                              cwd=root, env=env, capture_output=True, text=True, check=True, timeout=20)
    info = json.loads(executed.stdout)
    assert info["status"] == "LOCAL_OFFLINE_LABS_PASS"
    assert [x["status"] for x in info["labs"]] == ["PASS", "PASS"]
    assert info["authority"] == "NONE"
    assert info["independentEfficacy"] == "NOT VERIFIED"
    assert not (tmp_path / "aurex.sqlite3").exists()


def test_observer_provides_freshness_not_independent_proof(database):
    value = agent.once(database)
    assert value["authority"] == "NONE"
    assert value["worker"] == "NOT_VERIFIED"
    snap = agent.snapshot(database)
    assert snap["running"] is True
    assert snap["verification"] == "NOT_VERIFIED"


def test_fastapi_readonly_and_default_disabled(tmp_path, monkeypatch):
    db = str(tmp_path / "http.sqlite3")
    monkeypatch.setenv("AUREX_DB_PATH", db)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "q" * 40)
    monkeypatch.delenv("AUREX_ENABLE_OFFLINE_LAB", raising=False)
    with TestClient(app_module.app) as client:
        headers = {"Authorization": "Bearer " + "q" * 40}
        assert client.get("/v1/health").status_code == 401
        assert client.get("/v1/health", headers=headers).status_code == 200
        for path in ("/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs"):
            assert client.get(path, headers=headers).status_code == 200
        result = client.post("/v1/jobs", headers={**headers, "Idempotency-Key": "unix-lab-job-000001"},
            json={"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"}, "maxCostUsd": 0})
        assert result.status_code == 503
        assert client.get("/v1/jobs", headers=headers).json()["jobs"] == []
