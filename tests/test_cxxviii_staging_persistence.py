"""Staging boot proof runs only in isolated Railway staging and never burns credits."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).resolve().parents[1] / "integrations" / "kusanagi-xvi"
if str(BRIDGE_DIR) not in sys.path:
    sys.path.insert(0, str(BRIDGE_DIR))

probe = importlib.import_module("backend.staging_probe")
store = importlib.import_module("backend.store")

ENV = {
    "RAILWAY_ENVIRONMENT_NAME": "aurex-staging",
    "AUREX_STAGING_PERSISTENCE_PROBE": "true",
    "AUREX_REQUIRED_VOLUME": "true",
    "AUREX_LLM_ENABLED": "false",
    "AUREX_LLM_ALLOW_BILLING": "false",
}


def test_first_and_second_boot_prove_one_durable_observation(tmp_path):
    db = str(tmp_path / "volume" / "aurex.sqlite3")
    first = probe.run(db, ENV)
    assert first["status"] == "STAGING_PERSISTENCE_CHECK_PASS"
    assert first["previousBootRecordPresent"] is False
    assert first["evidenceDigestMatched"] is True
    second = probe.run(db, ENV)
    assert second["previousBootRecordPresent"] is True
    assert second["observationCount"] == 1
    with store.connect(db) as c:
        assert c.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
        assert c.execute("SELECT count(*) FROM evidence").fetchone()[0] == 1


@pytest.mark.parametrize("field,value", [
    ("RAILWAY_ENVIRONMENT_NAME", "production"),
    ("RAILWAY_ENVIRONMENT_NAME", "aurex-staging-typo"),
    ("AUREX_STAGING_PERSISTENCE_PROBE", "false"),
    ("AUREX_REQUIRED_VOLUME", "false"),
    ("AUREX_LLM_ENABLED", "true"),
    ("AUREX_LLM_ALLOW_BILLING", "true"),
])
def test_probe_refuses_unapproved_environment_without_db_write(tmp_path, field, value):
    env = {**ENV, field: value}
    db = tmp_path / "must-not-create.sqlite3"
    with pytest.raises(ValueError):
        probe.run(str(db), env)
    assert not db.exists()


def test_tampered_staging_receipt_fails_closed(tmp_path):
    db = str(tmp_path / "tamper.sqlite3")
    assert probe.run(db, ENV)["status"] == "STAGING_PERSISTENCE_CHECK_PASS"
    with store.connect(db) as conn:
        conn.execute("UPDATE evidence SET sha256=?", ("0" * 64,))
    with pytest.raises(RuntimeError, match="integrity check"):
        probe.run(db, ENV)



def test_local_receipt_readback_and_tamper_rejected(tmp_path):
    db = str(tmp_path / "staged.sqlite3")
    probe.run(db, ENV)
    jobs = store.list_jobs(db)
    assert len(jobs) == 1
    jid = jobs[0]["id"]
    valid = store.read_receipt(db, jid)
    assert valid is not None
    assert valid["state"] == "succeeded"
    assert valid["verification"] == "NOT VERIFIED"
    assert valid["authority"] == "NONE"
    assert valid["observation"]["passed"] is True
    assert store.read_receipt(db, "unknown") is None
    with store.connect(db) as conn:
        conn.execute("UPDATE evidence SET sha256=? WHERE job_id=?", ("f" * 64, jid))
    with pytest.raises(ValueError, match="integrity"):
        store.read_receipt(db, jid)


def test_bearer_protected_http_receipt_after_local_staging_boot(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    import importlib

    app = importlib.import_module("backend.app")
    db = str(tmp_path / "http-staging.sqlite3")
    monkeypatch.setenv("AUREX_DB_PATH", db)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "z" * 40)
    probe.run(db, ENV)
    jid = store.list_jobs(db)[0]["id"]
    with TestClient(app.app) as client:
        route = f"/v1/jobs/{jid}/receipt"
        assert client.get(route).status_code == 401
        assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
        r = client.get(route, headers={"Authorization": "Bearer " + "z" * 40})
        assert r.status_code == 200
        assert r.json()["verification"] == "NOT VERIFIED"
        assert "params" not in r.text
        with store.connect(db) as conn:
            conn.execute("UPDATE evidence SET sha256=? WHERE job_id=?", ("0" * 64, jid))
        failure = client.get(route, headers={"Authorization": "Bearer " + "z" * 40})
        assert failure.status_code == 409
        assert "0" * 64 not in failure.text
