import sqlite3

import pytest

from aurex_workflows.read_model import WorkflowReadModel


def test_reads_persisted_jobs(tmp_path):
    db = tmp_path / "jobs.sqlite"

    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )
        conn.execute(
            "INSERT INTO jobs VALUES (?,?,?,?,?,?,?)",
            (
                "job-001",
                "llm_eval",
                "COMPLETED",
                '{"secret":"DO_NOT_EXPOSE"}',
                '{"status":"LOCAL_INFERENCE_COMPLETED"}',
                100.0,
                101.0,
            ),
        )

    model = WorkflowReadModel(db)
    result = model.list_jobs(limit=10, cursor=None)

    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["id"] == "job-001"
    assert result["jobs"][0]["state"] == "COMPLETED"
    assert "DO_NOT_EXPOSE" not in str(result)


def test_missing_database_fails_closed(tmp_path):
    db = tmp_path / "missing.sqlite"

    model = WorkflowReadModel(db)

    with pytest.raises((FileNotFoundError, RuntimeError)):
        model.list_jobs(limit=10, cursor=None)

    assert not db.exists()


def test_invalid_page_size_rejected(tmp_path):
    db = tmp_path / "jobs.sqlite"

    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )

    model = WorkflowReadModel(db)

    with pytest.raises(ValueError):
        model.list_jobs(limit=0, cursor=None)

    with pytest.raises(ValueError):
        model.list_jobs(limit=10001, cursor=None)


# KUSANAGI XXV ADVERSARIAL PAGINATION TESTS


def test_pagination_stable_order(tmp_path):
    db = tmp_path / "pagination.sqlite"

    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )

        for number in range(5):
            conn.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,?,?)",
                (
                    f"job-{number}",
                    "llm_eval",
                    "COMPLETED",
                    '{"secret":"PRIVATE"}',
                    None,
                    float(number),
                    float(number),
                ),
            )

    model = WorkflowReadModel(db)

    first = model.list_jobs(limit=2, cursor=None)
    second = model.list_jobs(limit=2, cursor=first["nextCursor"])
    third = model.list_jobs(limit=2, cursor=second["nextCursor"])

    ids = [
        job["id"]
        for page in (first, second, third)
        for job in page["jobs"]
    ]

    assert ids == [
        "job-4",
        "job-3",
        "job-2",
        "job-1",
        "job-0",
    ]

    assert len(ids) == len(set(ids))
    assert third["nextCursor"] is None


def test_invalid_cursor_rejected(tmp_path):
    db = tmp_path / "cursor.sqlite"

    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )

    model = WorkflowReadModel(db)

    with pytest.raises(ValueError):
        model.list_jobs(limit=2, cursor="nonexistent-job")


def test_equal_timestamps_have_deterministic_order(tmp_path):
    db = tmp_path / "ties.sqlite"

    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )

        for job_id in ("alpha", "charlie", "bravo"):
            conn.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,?,?)",
                (
                    job_id,
                    "llm_eval",
                    "COMPLETED",
                    "{}",
                    None,
                    100.0,
                    100.0,
                ),
            )

    model = WorkflowReadModel(db)

    first = model.list_jobs(limit=2, cursor=None)
    second = model.list_jobs(limit=2, cursor=first["nextCursor"])

    ids = [
        job["id"]
        for page in (first, second)
        for job in page["jobs"]
    ]

    assert ids == ["charlie", "bravo", "alpha"]
