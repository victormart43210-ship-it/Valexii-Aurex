"""Read-only bridge integration and fail-closed regression tests."""
import importlib
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex_workflows.core import JobRequest, WorkflowEngine

TOKEN = 'XXVI_LOCAL_ONLY_TOKEN_0123456789abcdef'


@pytest.fixture
def client(monkeypatch):
    with tempfile.TemporaryDirectory(prefix='aurex-xxvi-') as tmp:
        db = Path(tmp) / 'workflow.sqlite'
        engine = WorkflowEngine(db)
        ids = [engine.submit(JobRequest(kind='dataset_validate', payload={'examples': [], 'secret': 'XXVI_PRIVATE_MARKER'}, approved=False, budget_usd=0.0)) for _ in range(5)]
        monkeypatch.setenv('AUREX_READ_TOKEN', TOKEN)
        monkeypatch.setenv('AUREX_WORKFLOW_DB', str(db))
        module = importlib.import_module('xxv_website_bridge.backend')
        yield TestClient(module.app, raise_server_exceptions=False), engine, ids, db


def test_public_assets_and_api_separation(client):
    api, _, _, _ = client
    for path in ('/', '/app.js', '/app.css'):
        assert api.get(path).status_code == 200
    for path in ('/v1/health', '/v1/capabilities', '/v1/jobs'):
        assert api.get(path).status_code == 401
        assert api.get(path, headers={'Authorization': 'Bearer wrong'}).status_code == 401


def test_real_jobs_metadata_only_and_no_implicit_approval(client):
    api, _, ids, _ = client
    response = api.get('/v1/jobs', headers={'Authorization': 'Bearer ' + TOKEN})
    assert response.status_code == 200
    assert {job['id'] for job in response.json()['jobs']} == set(ids)
    assert all(job['state'] == 'PENDING_APPROVAL' for job in response.json()['jobs'])
    assert 'XXVI_PRIVATE_MARKER' not in response.text
    assert all('payload' not in job and 'result' not in job for job in response.json()['jobs'])


def test_cursor_survives_deleted_anchor(client):
    api, _, _, db = client
    import sqlite3
    auth = {'Authorization': 'Bearer ' + TOKEN}
    first = api.get('/v1/jobs?limit=2', headers=auth)
    assert first.status_code == 200
    cursor = first.json()['nextCursor']
    assert cursor
    with sqlite3.connect(db) as conn:
        conn.execute('DELETE FROM jobs WHERE id=?', (first.json()['jobs'][-1]['id'],))
    second = api.get('/v1/jobs', params={'limit': 2, 'cursor': cursor}, headers=auth)
    assert second.status_code == 200
    assert len(second.json()['jobs']) == 2
    assert not {j['id'] for j in first.json()['jobs']} & {j['id'] for j in second.json()['jobs']}


@pytest.mark.parametrize('cursor', ['garbage', '!', 'A' * 5000])
def test_bad_cursor_rejected(client, cursor):
    api, _, _, _ = client
    response = api.get('/v1/jobs', params={'cursor': cursor}, headers={'Authorization': 'Bearer ' + TOKEN})
    assert response.status_code == 400


def test_database_unavailable_is_503(client, monkeypatch):
    api, _, _, _ = client
    monkeypatch.setenv('AUREX_WORKFLOW_DB', '/nonexistent/xxvi-database.sqlite')
    response = api.get('/v1/jobs', headers={'Authorization': 'Bearer ' + TOKEN})
    assert response.status_code == 503
    assert 'jobs' not in response.text


def test_missing_token_configuration_is_503(client, monkeypatch):
    api, _, _, _ = client
    monkeypatch.delenv('AUREX_READ_TOKEN')
    assert api.get('/v1/jobs', headers={'Authorization': 'Bearer ' + TOKEN}).status_code == 503
