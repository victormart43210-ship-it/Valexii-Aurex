"""Real SQLite privacy and retention checks for bounded analytics."""
import importlib
import importlib.util
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest


def analytics() -> ModuleType:
    assert importlib.util.find_spec("aurex.analytics") is not None, "analytics collector missing"
    return importlib.import_module("aurex.analytics")


def test_counts_are_real_events_not_unique_people(tmp_path: Path) -> None:
    module = analytics()
    db = str(tmp_path / "events.db")
    assert module.summary(db) == {}
    first = module.record_event(db, "page_view", "/aurex", "mobile")
    second = module.record_event(db, "page_view", "/aurex", "mobile")
    module.record_event(db, "job_failed")
    assert first != second
    assert module.summary(db) == {"page_view": 2, "job_failed": 1}


@pytest.mark.parametrize("event,route,device", [
    ("prompt:private", "/", "unknown"),
    ("page_view'); DROP TABLE jobs;--", "/", "unknown"),
    ("page_view", "https://private.example/token", "unknown"),
    ("page_view", "/user/private-identifier", "unknown"),
    ("page_view", "/" + "x" * 4096, "unknown"),
    ("page_view", "/", "private fingerprint"),
    ("page_view", "/aurex\x00", "unknown"),
])
def test_untrusted_dimensions_rejected(tmp_path: Path, event: str, route: str, device: str) -> None:
    module = analytics()
    db = str(tmp_path / "events.db")
    with pytest.raises(ValueError):
        module.record_event(db, event, route, device)
    assert module.summary(db) == {}


def test_query_and_fragment_never_persist(tmp_path: Path) -> None:
    module = analytics()
    db = str(tmp_path / "events.db")
    module.record_event(db, "navigation", "/aurex?token=secret#private-prompt", "desktop")
    with sqlite3.connect(db) as conn:
        row = conn.execute("SELECT * FROM analytics_events").fetchone()
        columns = {item[1] for item in conn.execute("PRAGMA table_info(analytics_events)")}
    assert "secret" not in str(row)
    assert "private" not in str(row)
    assert columns == {"id", "event", "route", "device", "created_at"}
    with pytest.raises(TypeError):
        module.record_event(db, "page_view", payload={"prompt": "secret"})


def test_retention_deletes_only_old_analytics(tmp_path: Path) -> None:
    module = analytics()
    db = str(tmp_path / "events.db")
    old_id = module.record_event(db, "page_view")
    module.record_event(db, "job_completed")
    old = (datetime.now(UTC) - timedelta(days=31)).isoformat()
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE analytics_events SET created_at=? WHERE id=?", (old, old_id))
        conn.execute("CREATE TABLE sentinel (value TEXT)")
        conn.execute("INSERT INTO sentinel VALUES ('preserve')")
    assert module.retention(db) == 1
    assert module.retention(db) == 0
    assert module.summary(db) == {"job_completed": 1}
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT value FROM sentinel").fetchone()[0] == "preserve"


@pytest.mark.parametrize("days", [0, -1, 366, True, 1.5])
def test_retention_bounds(tmp_path: Path, days: object) -> None:
    with pytest.raises(ValueError):
        analytics().retention(str(tmp_path / "events.db"), days)
