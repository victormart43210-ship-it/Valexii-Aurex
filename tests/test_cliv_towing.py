"""Actual canonical app, disposable SQLite, no provider or production access."""
import hashlib
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from aurex.api import app

URL = '/v1/industrial/audit/towing'
HEADERS = {'Authorization': 'Bearer ' + 's' * 40, 'Idempotency-Key': 'cliv-test-001'}


@pytest.fixture
def sandbox(monkeypatch, tmp_path):
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', 's' * 40)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_INDUSTRIAL_DEMO', '1')
    monkeypatch.setenv('AUREX_DEPLOYMENT_SCOPE', 'sandbox')
    path = str(tmp_path / 'canonical.db')
    monkeypatch.setenv('AUREX_DB_PATH', path)
    return TestClient(app, raise_server_exceptions=False), path


def submit(client, **kwargs):
    return client.post(URL, headers=HEADERS, json={'fixture': 'heavy_recovery_v1'}, **kwargs)


def test_towing_persists_replays_and_survives_new_client(sandbox):
    client, path = sandbox
    response = submit(client)
    assert response.status_code == 200
    receipt = response.json()
    assert receipt['observation']['candidate_amount_cents'] == 385000
    assert receipt['review'] == 'NOT_REVIEWED'
    assert receipt['authority'] == 'NONE'
    assert receipt['verification'] == 'NOT_VERIFIED'
    assert receipt['sha256'] == hashlib.sha256(json.dumps(receipt['observation'], sort_keys=True).encode()).hexdigest()
    assert submit(client).json() == receipt
    with TestClient(app) as restarted:
        read = restarted.get(f"{URL}/{receipt['job_id']}/receipt", headers=HEADERS)
        assert read.json() == receipt
    with sqlite3.connect(path) as db:
        assert db.execute('select count(*) from evidence_records').fetchone()[0] == 1
        assert db.execute('select state from jobs').fetchone()[0] == 'succeeded'


@pytest.mark.parametrize('header', [None, 'Bearer wrong', 'Basic abc', 'Bearer  ' + 's' * 40])
def test_authentication_rejects(sandbox, header):
    client, _ = sandbox
    headers = {} if header is None else {'Authorization': header}
    assert client.post(URL, headers=headers, json={'fixture': 'heavy_recovery_v1'}).status_code == 401


def test_non_ascii_auth_is_401(sandbox):
    client, _ = sandbox
    assert client.get('/v1/jobs', headers=[(b'authorization', b'Bearer \xff')]).status_code == 401


@pytest.mark.parametrize('body', [{}, {'fixture': 'customer'}, {'fixture': 'heavy_recovery_v1', 'records': []}, {'fixture': 'heavy_recovery_v1', 'review': 'APPROVED'}])
def test_reject_customer_and_review_inputs(sandbox, body):
    client, _ = sandbox
    assert client.post(URL, headers=HEADERS, json=body).status_code == 422


def test_disabled_never_writes(sandbox, monkeypatch):
    client, path = sandbox
    monkeypatch.setenv('AUREX_DEPLOYMENT_SCOPE', 'production')
    assert submit(client).status_code == 503
    from pathlib import Path
    assert not Path(path).exists()


def test_receipt_detects_tampering(sandbox):
    client, path = sandbox
    receipt = submit(client).json()
    with sqlite3.connect(path) as db:
        db.execute("update evidence_records set sha256=?", ('0' * 64,))
    assert client.get(f"{URL}/{receipt['job_id']}/receipt", headers=HEADERS).status_code == 409


def test_invalid_database_fails_closed(sandbox, monkeypatch, tmp_path):
    client, _ = sandbox
    monkeypatch.setenv('AUREX_DB_PATH', str(tmp_path))
    assert submit(client).status_code == 503


def test_cancelled_replay_cannot_issue_receipt(sandbox):
    client, path = sandbox
    assert submit(client).status_code == 200
    with sqlite3.connect(path) as db:
        db.execute("update jobs set state='cancelled'")
    assert submit(client).status_code == 409


def test_corrupted_result_shape_fails_closed(sandbox):
    client, path = sandbox
    receipt = submit(client).json()
    with sqlite3.connect(path) as db:
        db.execute("update jobs set result_json='[]'")
    assert client.get(f"{URL}/{receipt['job_id']}/receipt", headers=HEADERS).status_code == 409


def test_legacy_schema_is_not_mutated(sandbox):
    client, path = sandbox
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE jobs (id TEXT PRIMARY KEY, params TEXT)')
    assert submit(client).status_code == 503
    with sqlite3.connect(path) as db:
        assert db.execute("select name from sqlite_master where type='table'").fetchall() == [('jobs',)]
