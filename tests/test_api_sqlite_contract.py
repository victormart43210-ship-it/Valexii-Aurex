"""$0 in-process HTTP -> fenced worker -> SQLite -> evidence contract proof.

This exercises canonical API implementation only, not Lovable, Railway, or
financial audit accuracy. No remote network, model inference or customer data.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

import aurex.api as aurex_api
from aurex.database import get_job

TOKEN = "v" * 40
AUTH = {"Authorization": f"Bearer {TOKEN}"}
PROBE = {"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"}, "maxCostUsd": 0.0}


@pytest.fixture
def local_lab(tmp_path, monkeypatch):
    db_path = str(tmp_path / "api_contract.sqlite3")
    monkeypatch.setattr(aurex_api, "DEFAULT_DB_PATH", db_path)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "1")
    with TestClient(aurex_api.app) as client:
        yield client, db_path


def test_full_authenticated_http_sqlite_evidence_roundtrip(local_lab):
    client, db = local_lab
    idempotency_key = "source-bound-synthetic-probe-001"
    headers = {**AUTH, "Idempotency-Key": idempotency_key}
    submitted = client.post("/v1/jobs", json=PROBE, headers=headers)
    assert submitted.status_code == 200
    job = submitted.json()
    assert job["kind"] == "regression_scan"
    assert job["state"] == "succeeded"
    assert job["reservationUsd"] == 0
    assert set(job) == {"id", "kind", "state", "createdAt", "updatedAt", "reservationUsd"}

    # HTTP read-back and durable SQLite copy must have the same job identifier.
    retrieved = client.get(f"/v1/jobs/{job['id']}", headers=AUTH)
    assert retrieved.status_code == 200
    assert retrieved.json() == job
    persisted = get_job(db, job["id"])
    assert persisted is not None
    assert persisted["state"] == "succeeded"
    assert persisted["reservation_usd"] == 0
    assert persisted["result"]["observation"]["verification"] == "NOT VERIFIED"
    assert persisted["result"]["observation"]["probe"] == "sqlite_roundtrip_v1"
    assert persisted["result"]["observation"]["executed"] is True

    # Verify recorded digest against the canonical persisted observation bytes.
    digest = hashlib.sha256(
        json.dumps(persisted["result"]["observation"], sort_keys=True).encode()
    ).hexdigest()
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT id, capability_id, kind, sha256, integrity_status, "
            "verification_status, summary FROM evidence_records WHERE id=?",
            (persisted["evidence_id"],),
        ).fetchone()
    assert row is not None
    evidence_id, capability, kind, stored_digest, integrity, verification, summary = row
    assert (capability, kind) == ("regression_scan", "offline_probe")
    assert stored_digest == digest
    assert (integrity, verification) == ("RECORDED", "UNVERIFIED")
    assert "NOT VERIFIED" in summary
    assert evidence_id == persisted["result"]["evidence_id"]

    # Website-facing projection currently lists receipts without observation bodies.
    public = client.get("/v1/evidence", headers=AUTH)
    assert public.status_code == 200
    events = public.json()["evidence"]
    assert len(events) == 1
    assert events[0]["id"] == evidence_id
    assert events[0]["capabilityId"] == "regression_scan"
    assert events[0]["kind"] == "offline_probe"
    assert events[0]["sha256"] == digest
    assert all("observation" not in e for e in events)
    assert client.get("/v1/budgets", headers=AUTH).json()["limitUsd"] == 0

    # Exact idempotent replay must not create a second job or evidence receipt.
    replay = client.post("/v1/jobs", json=PROBE, headers=headers)
    assert replay.status_code == 200
    assert replay.json()["id"] == job["id"]
    assert len(client.get("/v1/jobs", headers=AUTH).json()["jobs"]) == 1
    assert len(client.get("/v1/evidence", headers=AUTH).json()["evidence"]) == 1


def test_authentication_fails_closed_before_financial_or_probe_effects(local_lab):
    client, db = local_lab
    for headers in ({}, {"Authorization": "Bearer wrong"}, {"Authorization": "Basic wrong"}):
        assert client.post("/v1/jobs", json=PROBE, headers={
            **headers, "Idempotency-Key": "unauthorized-probe-001"
        }).status_code == 401
        assert client.get("/v1/evidence", headers=headers).status_code == 401
        assert client.get("/v1/jobs", headers=headers).status_code == 401
        assert client.get("/v1/budgets", headers=headers).status_code == 401
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT count(*) FROM jobs").fetchone()[0] if (
            conn.execute("SELECT name FROM sqlite_master WHERE name='jobs'").fetchone()
        ) else 0
    assert count == 0


def test_non_probe_requests_and_payments_stay_disabled(local_lab):
    client, _ = local_lab
    for request, expected in [
        ({"kind": "regression_scan", "params": {"probe": "other"}, "maxCostUsd": 0}, 422),
        ({"kind": "benchmark", "params": {}, "maxCostUsd": 0}, 400),
        ({"kind": "regression_scan", "params": {"probe": "sqlite_roundtrip_v1"},
          "maxCostUsd": 0.01}, 402),
    ]:
        response = client.post("/v1/jobs", json=request, headers={
            **AUTH, "Idempotency-Key": "forbidden-job-probe-001"
        })
        assert response.status_code == expected
    assert client.get("/v1/jobs", headers=AUTH).json()["jobs"] == []
    assert client.get("/v1/evidence", headers=AUTH).json()["evidence"] == []


def test_disabled_worker_remains_unavailable(local_lab, monkeypatch):
    client, _ = local_lab
    monkeypatch.setenv("AUREX_ENABLE_OFFLINE_LAB", "0")
    response = client.post("/v1/jobs", json=PROBE, headers={
        **AUTH, "Idempotency-Key": "offline-worker-probe-001"
    })
    assert response.status_code == 503
    assert client.get("/v1/jobs", headers=AUTH).json()["jobs"] == []


def test_conflicting_server_auth_tokens_fail_closed(local_lab, monkeypatch):
    client, _ = local_lab
    monkeypatch.setenv("AUREX_ADMIN_TOKEN", "different-secret-token-longer-than-32")
    assert client.get("/v1/evidence", headers=AUTH).status_code == 500
    assert client.post("/v1/jobs", json=PROBE, headers={
        **AUTH, "Idempotency-Key": "conflicted-secret-probe-001"
    }).status_code == 500


def test_fixed_synthetic_financial_100_case_job_is_persisted_hold(local_lab, monkeypatch):
    client, db = local_lab
    monkeypatch.setenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", "1")
    request = {"kind": "regression_scan",
               "params": {"probe": "synthetic_field_audit_v1"}, "maxCostUsd": 0}
    headers = {**AUTH, "Idempotency-Key": "synthetic-fixed-field-001"}
    response = client.post("/v1/jobs", json=request, headers=headers)
    assert response.status_code == 200
    job = response.json()
    assert job["state"] == "succeeded"
    persisted = get_job(db, job["id"])
    assert persisted is not None
    obs = persisted["result"]["observation"]
    assert obs["probe"] == "synthetic_field_audit_v1"
    assert obs["synthetic"] is True
    assert obs["case_count"] == obs["exact_case_matches"] == 100
    assert obs["finding_labels"] == 70
    assert obs["false_positive_flags"] == obs["false_negative_flags"] == 0
    assert obs["independent_verification"] == "NOT_VERIFIED"
    assert obs["real_document_accuracy"] == "NOT_MEASURED"
    assert (obs["authority"], obs["effect"], obs["production_release"]) == (
        "HOLD", "NONE", "HOLD"
    )
    assert len(obs["suite_sha256"]) == 64
    digest = hashlib.sha256(json.dumps(obs, sort_keys=True).encode()).hexdigest()
    records = client.get("/v1/evidence", headers=AUTH).json()["evidence"]
    assert len(records) == 1 and records[0]["sha256"] == digest
    assert records[0]["kind"] == "offline_probe"
    assert client.post("/v1/jobs", json=request, headers=headers).json()["id"] == job["id"]
    assert len(client.get("/v1/evidence", headers=AUTH).json()["evidence"]) == 1


def test_synthetic_financial_probe_disabled_by_default(local_lab, monkeypatch):
    client, _ = local_lab
    monkeypatch.delenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", raising=False)
    response = client.post("/v1/jobs", json={
        "kind": "regression_scan", "params": {"probe": "synthetic_field_audit_v1"},
        "maxCostUsd": 0,
    }, headers={**AUTH, "Idempotency-Key": "disabled-synthetic-case-001"})
    assert response.status_code == 503
    assert client.get("/v1/jobs", headers=AUTH).json()["jobs"] == []


def test_synthetic_financial_probe_refuses_supplied_financial_records(local_lab, monkeypatch):
    client, _ = local_lab
    monkeypatch.setenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", "1")
    response = client.post("/v1/jobs", json={
        "kind": "regression_scan",
        "params": {"probe": "synthetic_field_audit_v1", "invoice_cents": 99999},
        "maxCostUsd": 0,
    }, headers={**AUTH, "Idempotency-Key": "refused-financial-input-001"})
    assert response.status_code == 422
    assert client.get("/v1/jobs", headers=AUTH).json()["jobs"] == []


def test_corrupt_synthetic_candidate_cannot_return_a_verified_job(local_lab, monkeypatch):
    client, db = local_lab
    monkeypatch.setenv("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT", "1")
    import workstation.field_audit_beta_pipeline as pipeline

    original = pipeline.candidate_from_suite

    def corrupt(suite_data):
        candidate = original(suite_data)
        candidate["results"][0]["flags"] = ["MISSING_RATE_APPROVAL"]
        return candidate

    monkeypatch.setattr(pipeline, "candidate_from_suite", corrupt)
    response = client.post("/v1/jobs", json={
        "kind": "regression_scan", "params": {"probe": "synthetic_field_audit_v1"},
        "maxCostUsd": 0,
    }, headers={**AUTH, "Idempotency-Key": "corrupt-synthetic-case-001"})
    assert response.status_code == 503
    jobs = client.get("/v1/jobs", headers=AUTH).json()["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["state"] != "succeeded"
    assert client.get("/v1/evidence", headers=AUTH).json()["evidence"] == []
    assert get_job(db, jobs[0]["id"])["evidence_id"] is None


def test_fenced_failure_is_terminal_and_does_not_create_evidence(local_lab, monkeypatch):
    client, db = local_lab

    def fail_probe(_params):
        raise RuntimeError("Synthetic forced worker failure")

    monkeypatch.setattr(aurex_api, "execute_sqlite_roundtrip", fail_probe)
    headers = {**AUTH, "Idempotency-Key": "fenced-terminal-failure-001"}
    response = client.post("/v1/jobs", json=PROBE, headers=headers)
    assert response.status_code == 503

    jobs = client.get("/v1/jobs", headers=AUTH).json()["jobs"]
    assert len(jobs) == 1 and jobs[0]["state"] == "failed"
    record = get_job(db, jobs[0]["id"])
    assert record is not None
    assert record["lease_token"] is None
    assert record["lease_expires_at"] is None
    assert json.loads(record["error_json"])["code"] == "PROBE_FAILED"
    assert record["evidence_id"] is None
    assert client.get("/v1/evidence", headers=AUTH).json()["evidence"] == []

    # Exactly-once replay must not re-execute or manufacture evidence.
    replay = client.post("/v1/jobs", json=PROBE, headers=headers)
    assert replay.status_code == 200 and replay.json()["state"] == "failed"
    assert len(client.get("/v1/jobs", headers=AUTH).json()["jobs"]) == 1


def test_failed_worker_cannot_overwrite_cancelled_or_superseded_lease(local_lab):
    _client, db = local_lab
    from aurex.database import create_job
    from aurex.fenced_worker import cancel_job, claim_job, fail_job

    first_job = create_job(db, "job-fenced-cancel", "regression_scan", {"probe": "sqlite_roundtrip_v1"})
    first = claim_job(db, first_job["id"], "worker-a")
    assert first is not None
    assert cancel_job(db, first_job["id"])["state"] == "cancelled"
    assert fail_job(db, first_job["id"], "worker-a", first["lease_token"], first["lease_generation"]) is None
    assert get_job(db, first_job["id"])["state"] == "cancelled"

    second_job = create_job(db, "job-fenced-takeover", "regression_scan", {"probe": "sqlite_roundtrip_v1"})
    stale = claim_job(db, second_job["id"], "worker-a")
    assert stale is not None
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE jobs SET lease_expires_at = ? WHERE id = ?",
                     ("2000-01-01T00:00:00+00:00", second_job["id"]))
    replacement = claim_job(db, second_job["id"], "worker-b")
    assert replacement is not None
    assert replacement["lease_generation"] > stale["lease_generation"]
    assert fail_job(db, second_job["id"], "worker-a", stale["lease_token"], stale["lease_generation"]) is None
    live = get_job(db, second_job["id"])
    assert live["state"] == "running" and live["worker_id"] == "worker-b"
    assert live["lease_token"] == replacement["lease_token"]
