"""Failures must persist without granting a stale worker write authority."""
import json
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

import aurex.api as api
from aurex.database import get_db, get_job, list_evidence, list_jobs
from aurex.fenced_worker import cancel_job, claim_job


def test_api_failure_is_durable_and_redacted(tmp_path, monkeypatch):
    db = str(tmp_path / 'jobs.db')
    monkeypatch.setattr(api, 'DEFAULT_DB_PATH', db)
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', 'a' * 32)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_OFFLINE_LAB', '1')

    def broken_probe(params):
        raise RuntimeError('secret-token-private-prompt')

    monkeypatch.setattr(api, 'execute_sqlite_roundtrip', broken_probe)
    client = TestClient(api.app)
    headers = {'Authorization': 'Bearer ' + 'a' * 32, 'Idempotency-Key': 'failure-case'}
    body = {'kind': 'regression_scan', 'params': {'probe': 'sqlite_roundtrip_v1'}}
    response = client.post('/v1/jobs', headers=headers, json=body)
    assert response.status_code == 503
    jobs = list_jobs(db)
    assert len(jobs) == 1
    job = jobs[0]
    assert job['state'] == 'failed'
    assert job['lease_token'] is None
    assert job['lease_expires_at'] is None
    assert json.loads(job['error_json']) == {'kind': 'EXECUTION_FAILURE'}
    assert 'secret-token' not in json.dumps(job) + response.text
    assert list_evidence(db) == []
    replay = client.post('/v1/jobs', headers=headers, json=body)
    assert replay.status_code == 200
    assert replay.json()['state'] == 'failed'
    assert len(list_jobs(db)) == 1


def test_failure_does_not_overwrite_cancellation(tmp_path, monkeypatch):
    db = str(tmp_path / 'jobs.db')
    monkeypatch.setattr(api, 'DEFAULT_DB_PATH', db)
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', 'a' * 32)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_OFFLINE_LAB', '1')

    def cancelled_probe(params):
        cancel_job(db, list_jobs(db)[0]['id'])
        raise RuntimeError('cancelled')

    monkeypatch.setattr(api, 'execute_sqlite_roundtrip', cancelled_probe)
    response = TestClient(api.app).post('/v1/jobs',
        headers={'Authorization': 'Bearer ' + 'a' * 32, 'Idempotency-Key': 'cancel'},
        json={'kind': 'regression_scan', 'params': {'probe': 'sqlite_roundtrip_v1'}})
    assert response.status_code == 503
    assert list_jobs(db)[0]['state'] == 'cancelled'
    assert list_evidence(db) == []


def test_failed_stale_worker_cannot_overwrite_new_owner(tmp_path, monkeypatch):
    db = str(tmp_path / 'jobs.db')
    monkeypatch.setattr(api, 'DEFAULT_DB_PATH', db)
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', 'a' * 32)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_OFFLINE_LAB', '1')
    replacement = {}

    def superseded_probe(params):
        job_id = list_jobs(db)[0]['id']
        conn = get_db(db)
        conn.execute('UPDATE jobs SET lease_expires_at=? WHERE id=?',
                     ((datetime.now(UTC) - timedelta(seconds=1)).isoformat(), job_id))
        conn.commit()
        conn.close()
        replacement.update(claim_job(db, job_id, 'replacement'))
        raise RuntimeError('old worker failed')

    monkeypatch.setattr(api, 'execute_sqlite_roundtrip', superseded_probe)
    response = TestClient(api.app).post('/v1/jobs',
        headers={'Authorization': 'Bearer ' + 'a' * 32, 'Idempotency-Key': 'stale'},
        json={'kind': 'regression_scan', 'params': {'probe': 'sqlite_roundtrip_v1'}})
    assert response.status_code == 503
    job = get_job(db, replacement['id'])
    assert job['state'] == 'running'
    assert job['worker_id'] == 'replacement'
    assert job['lease_token'] == replacement['lease_token']
    assert job['error_json'] is None


def test_failure_requires_unexpired_lease(tmp_path):
    from aurex.database import create_job
    from aurex.fenced_worker import fail_job

    db = str(tmp_path / 'expired.db')
    create_job(db, 'job', 'regression_scan', {})
    claimed = claim_job(db, 'job', 'worker')
    conn = get_db(db)
    conn.execute('UPDATE jobs SET lease_expires_at=? WHERE id=?',
                 ((datetime.now(UTC) - timedelta(seconds=1)).isoformat(), 'job'))
    conn.commit()
    conn.close()
    assert not fail_job(db, 'job', 'worker', claimed['lease_token'], claimed['lease_generation'])
    assert get_job(db, 'job')['state'] == 'running'
    assert get_job(db, 'job')['error_json'] is None


def test_database_failure_is_not_reported_as_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(api, 'DEFAULT_DB_PATH', str(tmp_path / 'db.db'))
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', 'a' * 32)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_OFFLINE_LAB', '1')

    def broken(*args):
        raise RuntimeError('secret-storage-details')

    monkeypatch.setattr(api, 'execute_sqlite_roundtrip', broken)
    monkeypatch.setattr(api, 'fail_job', broken)
    response = TestClient(api.app).post('/v1/jobs',
        headers={'Authorization': 'Bearer ' + 'a' * 32, 'Idempotency-Key': 'db-failure'},
        json={'kind': 'regression_scan', 'params': {'probe': 'sqlite_roundtrip_v1'}})
    assert response.status_code == 503
    assert response.json()['detail'] == 'Job persistence unavailable; execution not verified'
    assert 'secret-storage-details' not in response.text


def test_success_and_failure_race_has_one_terminal_outcome(tmp_path):
    import hashlib
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from aurex.database import create_job
    from aurex.fenced_worker import fail_job, finalize_job

    for index in range(10):
        db = str(tmp_path / f'race-{index}.db')
        create_job(db, 'job', 'regression_scan', {})
        claimed = claim_job(db, 'job', 'worker')
        args = (db, 'job', 'worker', claimed['lease_token'], claimed['lease_generation'])
        observation = {'executed': True}
        digest = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
        barrier = Barrier(2)

        def succeed():
            barrier.wait()
            try:
                finalize_job(*args, observation, digest, 'evidence')
                return True
            except ValueError:
                return False

        def fail():
            barrier.wait()
            return fail_job(*args)

        with ThreadPoolExecutor(max_workers=2) as pool:
            success, failure = pool.submit(succeed), pool.submit(fail)
            assert sum((success.result(), failure.result())) == 1
        job = get_job(db, 'job')
        assert job['state'] in {'succeeded', 'failed'}
        assert len(list_evidence(db)) == (1 if job['state'] == 'succeeded' else 0)
        assert job['lease_token'] is None
