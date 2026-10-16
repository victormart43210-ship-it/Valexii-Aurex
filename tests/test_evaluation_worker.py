"""Local evaluation worker tests; no external model or network required."""

import pytest

from aurex.database import get_job, list_evidence
from aurex.evaluation_worker import execute_local_regression
from aurex.international_eval import Case


def test_persists_unverified_observations(tmp_path):
    db_path = str(tmp_path / "worker.db")
    output = execute_local_regression(
        db_path,
        (Case("1", "question", "answer", ("answer",)),),
        lambda _: "answer",
    )
    job = get_job(db_path, output["job_id"])
    assert job is not None
    assert job["state"] == "succeeded"
    assert job["result"]["verification_status"] == "UNVERIFIED"
    assert job["result"]["authority"] == "NONE"
    evidence = list_evidence(db_path)
    assert len(evidence) == 1
    assert evidence[0]["verification_status"] == "UNVERIFIED"
    assert len(evidence[0]["sha256"]) == 64


def test_rejects_oversized_work_before_creating_job(tmp_path):
    db_path = str(tmp_path / "worker.db")
    with pytest.raises(ValueError):
        execute_local_regression(
            db_path,
            (Case("1", "a" * 4097, "x"),),
            lambda _: "x",
        )
    assert list_evidence(db_path) == []


def test_records_responder_errors_without_claiming_match(tmp_path):
    db_path = str(tmp_path / "worker.db")

    def broken(_: str) -> str:
        raise RuntimeError("offline failure")

    output = execute_local_regression(
        db_path,
        (Case("1", "q", "expected"),),
        broken,
    )
    observation = output["result"]["observations"][0]
    assert observation["error"] == "RuntimeError"
    assert observation["exact_match"] is False
