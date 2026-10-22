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
