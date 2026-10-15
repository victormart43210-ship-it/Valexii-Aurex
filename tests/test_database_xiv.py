"""Storage boundary regressions using real SQLite connections and contention."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from aurex.database import (
    create_job,
    get_db,
    get_job,
    list_evidence,
    list_jobs,
    record_evidence,
    update_job_state,
)


def test_concurrent_duplicate_submission_creates_one_job(tmp_path):
    db = str(tmp_path / "concurrent.db")
    get_db(db).close()
    barrier = Barrier(12)

    def submit(i):
        barrier.wait()
        return create_job(db, f"job-{i}", "regression_scan", {"suite": "quick"}, "retry-key")["id"]

    with ThreadPoolExecutor(max_workers=12) as pool:
        ids = list(pool.map(submit, range(12)))
    assert len(set(ids)) == 1
    assert len(list_jobs(db)) == 1


def test_replayed_key_cannot_change_cost(tmp_path):
    db = str(tmp_path / "cost.db")
    create_job(db, "one", "regression_scan", {}, "key", reservation_usd=0)
    with pytest.raises(ValueError):
        create_job(db, "two", "regression_scan", {}, "key", reservation_usd=1)


def test_owner_isolation_for_jobs_transitions_and_idempotency(tmp_path):
    db = str(tmp_path / "owners.db")
    create_job(db, "alice-job", "regression_scan", {}, "key", owner_id="alice")
    create_job(db, "bob-job", "regression_scan", {}, "key", owner_id="bob")
    assert get_job(db, "alice-job", owner_id="bob") is None
    assert update_job_state(db, "alice-job", "running", owner_id="bob") is None
    assert [j["id"] for j in list_jobs(db, owner_id="alice")] == ["alice-job"]
    assert list_jobs(db) == []


def test_evidence_cannot_be_replaced(tmp_path):
    db = str(tmp_path / "evidence.db")
    original = record_evidence(db, "ev-one", "regression-scan", "test_run", "a" * 64, "original")
    with pytest.raises(ValueError):
        record_evidence(db, "ev-one", "regression-scan", "test_run", "b" * 64, "replacement")
    assert list_evidence(db) == [original]
    assert record_evidence(db, "ev-one", "regression-scan", "test_run", "a" * 64, "original") == original


def test_evidence_owner_isolation_and_invalid_digest(tmp_path):
    db = str(tmp_path / "evidence-owners.db")
    record_evidence(db, "ev-one", "regression-scan", "test_run", "a" * 64, "observation", owner_id="alice")
    assert list_evidence(db, owner_id="bob") == []
    with pytest.raises(ValueError):
        record_evidence(db, "ev-bad", "regression-scan", "test_run", "not-a-digest", "observation")


def test_database_enforces_unique_key_outside_helper(tmp_path):
    db = str(tmp_path / "constraint.db")
    create_job(db, "one", "regression_scan", {}, "key")
    with sqlite3.connect(db) as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO jobs (id,kind,state,idempotency_key,params_json,reservation_usd,created_at,updated_at,result_json,owner_id) SELECT 'two', kind, state, idempotency_key, params_json, reservation_usd, created_at, updated_at, result_json, owner_id FROM jobs WHERE id = 'one'")


def legacy_db(db, duplicate=False):
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE jobs (id TEXT PRIMARY KEY, kind TEXT NOT NULL, state TEXT NOT NULL, idempotency_key TEXT, params_json TEXT NOT NULL, reservation_usd REAL NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, result_json TEXT)")
        for name in (["one", "two"] if duplicate else ["one"]):
            conn.execute("INSERT INTO jobs VALUES (?, 'regression_scan', 'queued', 'key', '{}', 0, '2026-01-01', '2026-01-01', NULL)", (name,))


def test_legacy_duplicate_keys_fail_closed_without_deletion_or_partial_migration(tmp_path):
    db = str(tmp_path / "legacy-duplicate.db")
    legacy_db(db, duplicate=True)
    with pytest.raises(ValueError):
        get_db(db)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2
        assert "owner_id" not in [r[1] for r in conn.execute("PRAGMA table_info(jobs)")]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 0


def test_legacy_row_preserved_in_service_scope(tmp_path):
    db = str(tmp_path / "legacy.db")
    legacy_db(db)
    assert get_job(db, "one")["owner_id"] == "service"
    assert get_job(db, "one", owner_id="alice") is None


def test_list_is_bounded(tmp_path):
    db = str(tmp_path / "bounded.db")
    for i in range(205):
        create_job(db, f"job-{i}", "regression_scan", {})
    assert len(list_jobs(db)) == 200
