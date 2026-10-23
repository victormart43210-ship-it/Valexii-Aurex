"""Canonical detached worker contract; fixed fictional data only."""
from __future__ import annotations

from fastapi.testclient import TestClient

import aurex.api as api
from aurex.database import get_job

AUTH = {"Authorization": "Bearer " + "q" * 40, "Idempotency-Key": "cxxix-fictional-0001"}
BODY = {"kind": "regression_scan", "params": {"probe": "synthetic_field_audit_v1"}, "maxCostUsd": 0}


def test_queued_financial_job_requires_worker_and_persists_receipt(tmp_path, monkeypatch):
    path = str(tmp_path / "jobs.sqlite3")
    monkeypatch.setattr(api, "DEFAULT_DB_PATH", path)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "q" * 40)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    monkeypatch.setenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", "1")
    monkeypatch.setenv("AUREX_JOB_EXECUTION_MODE", "queued")
    with TestClient(api.app) as client:
        submitted = client.post("/v1/jobs", headers=AUTH, json=BODY)
        assert submitted.status_code == 200
        assert submitted.json()["state"] == "queued"
        job_id = submitted.json()["id"]
        assert client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH).status_code == 409
        from aurex.offline_worker import run_once
        assert run_once(path, "test-worker") is True
        receipt = client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH)
        assert receipt.status_code == 200
        report = receipt.json()
        assert report["observation"]["exact_case_matches"] == 100
        assert report["authority"] == "NONE" and report["release"] == "HOLD"
        assert get_job(path, job_id)["state"] == "succeeded"
        assert run_once(path, "test-worker") is False
        replay = client.post("/v1/jobs", headers=AUTH, json=BODY)
        assert replay.json()["id"] == job_id
        assert client.get(f"/v1/jobs/{job_id}/receipt", headers=AUTH).json() == report


def test_cancelled_and_failed_jobs_never_receive_worker_receipts(tmp_path, monkeypatch):
    import pytest

    from aurex.database import create_job
    from aurex.fenced_worker import cancel_job
    from aurex.offline_worker import run_once
    from aurex.pipeline_receipts import read_pipeline_receipt

    path = str(tmp_path / "jobs.sqlite3")
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    monkeypatch.setenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", "0")
    cancelled = "job-" + "a" * 24
    disabled = "job-" + "b" * 24
    for job_id in (cancelled, disabled):
        create_job(path, job_id, "regression_scan", BODY["params"])
    cancel_job(path, cancelled)
    assert run_once(path, "worker") is True
    assert get_job(path, cancelled)["state"] == "cancelled"
    assert get_job(path, disabled)["state"] == "failed"
    for job_id in (cancelled, disabled):
        with pytest.raises(ValueError):
            read_pipeline_receipt(path, job_id)
    assert run_once(path, "worker") is False
