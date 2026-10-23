"""Fail-closed legacy database protection."""

import sqlite3

import pytest

from aurex.database import get_db


def test_fresh_database_allowed(tmp_path):
    path = str(tmp_path / "fresh.sqlite3")
    conn = get_db(path)
    try:
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"jobs", "evidence_records"} <= tables
    finally:
        conn.close()


def test_legacy_database_refused_without_mutation(tmp_path):
    path = tmp_path / "legacy.sqlite3"

    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE jobs "
            "(id TEXT PRIMARY KEY, params TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE evidence (id TEXT PRIMARY KEY)"
        )

    original = path.read_bytes()

    with pytest.raises(ValueError, match="Legacy"):
        get_db(str(path))

    assert path.read_bytes() == original


def test_incompatible_evidence_records_refused(tmp_path):
    path = tmp_path / "incompatible.sqlite3"

    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE evidence_records "
            "(id TEXT PRIMARY KEY)"
        )

    original = path.read_bytes()

    with pytest.raises(ValueError, match="Incompatible"):
        get_db(str(path))

    assert path.read_bytes() == original
