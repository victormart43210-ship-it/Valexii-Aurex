"""Source-only checks for the recovered legacy runtime."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0, str(ROOT / "integrations/kusanagi-xvi")
)

from backend import store, supervisor, worker
from aurex.database import get_db


def test_default_supervisor_has_no_worker():
    commands = supervisor.child_commands({})

    assert len(commands) == 1
    assert "backend.app:app" in commands[0]


def test_missing_required_volume_fails_closed():
    env = {
        "AUREX_DB_PATH": "/data/aurex.sqlite3",
        "AUREX_REQUIRED_VOLUME": "true",
    }

    with pytest.raises(ValueError, match="Required persistent"):
        supervisor.validate_config(
            env,
            mount_check=lambda _: False,
        )


def test_legacy_worker_disabled_by_default(
    tmp_path, monkeypatch
):
    monkeypatch.delenv(
        "AUREX_ENABLE_OFFLINE_LAB",
        raising=False,
    )

    path = tmp_path / "unused.sqlite3"

    result = worker.once(db_path=str(path))

    assert result["status"] == "HOLD"
    assert result["authority"] == "NONE"
    assert not path.exists()


def test_canonical_engine_refuses_real_legacy_schema(
    tmp_path
):
    path = str(tmp_path / "legacy.sqlite3")

    store.initialize(path)

    with pytest.raises(ValueError, match="Legacy"):
        get_db(path)
