"""Owner isolation and honest readiness at the HTTP boundary."""
import json

import pytest
from fastapi.testclient import TestClient

from aurex import api
from aurex.database import create_job

TOKEN = 'a' * 32

@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', TOKEN)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.delenv('AUREX_EXECUTION_ENABLED', raising=False)
    monkeypatch.setenv('AUREX_USER_TOKENS', json.dumps({'alice': 'b'*32, 'bob': 'c'*32}))
    monkeypatch.setattr(api, 'DEFAULT_DB_PATH', str(tmp_path/'jobs.db'))
    return TestClient(api.app)


def auth(char='a'):
    return {'Authorization': 'Bearer '+char*32}


def test_process_alive_is_separate_from_readiness(client):
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 503
    assert client.get('/health/dependencies').status_code == 401
    status = client.get('/health/dependencies', headers=auth()).json()
    assert status['database'] == 'PASS'
    assert status['worker'] == 'NOT VERIFIED'
    assert status['model'] == 'NOT VERIFIED'


def test_owner_is_derived_from_credential_not_request(client):
    create_job(api.DEFAULT_DB_PATH, 'private', 'local_inference', {'prompt':'private'}, owner_id='alice')
    assert client.get('/v1/jobs/private', headers=auth('b')).status_code == 200
    assert client.get('/v1/jobs/private', headers=auth('c')).status_code == 404
    assert client.get('/v1/jobs/private/result', headers=auth('c')).status_code == 404
    assert client.get('/v1/jobs/private/evidence', headers=auth('c')).status_code == 404
    assert client.post('/v1/jobs/private/cancel', headers=auth('c')).status_code == 404
    assert client.get('/v1/jobs', headers=auth('c')).json()['jobs'] == []
    assert client.get('/v1/jobs/private/result', headers=auth('b')).json()['result'] is None


def test_local_submission_fails_closed_until_enabled(client):
    r=client.post('/v1/jobs', headers=auth(), json={'kind':'local_inference','params':{'prompt':'test'}})
    assert r.status_code == 503
    assert client.get('/v1/jobs', headers=auth()).json()['jobs'] == []


def test_read_pagination(client):
    for i in range(201):
        create_job(api.DEFAULT_DB_PATH, f'job{i}', 'local_inference', {'prompt':'test'})
    first=client.get('/v1/jobs', headers=auth()).json()
    assert len(first['jobs'])==200
    assert first['nextCursor']
    second=client.get('/v1/jobs',params={'cursor':first['nextCursor']},headers=auth()).json()
    assert len(second['jobs'])==1
    assert second['jobs'][0]['id'] not in {j['id'] for j in first['jobs']}


def test_duplicate_identity_configuration_fails_closed(client, monkeypatch):
    monkeypatch.setenv('AUREX_USER_TOKENS', json.dumps({'alice':TOKEN}))
    assert client.get('/v1/jobs',headers=auth()).status_code == 503


def test_prompt_size_and_extra_fields(client):
    for params in ({'prompt':' '},{'prompt':'x'*8193},{'prompt':'ok','owner':'alice'}):
        assert client.post('/v1/jobs',headers=auth(),json={'kind':'local_inference','params':params}).status_code==422


def test_tampered_result_is_withheld(client):
    import sqlite3

    from aurex.database import claim_job, finish_job
    create_job(api.DEFAULT_DB_PATH,'tamper','local_inference',{'prompt':'test'})
    claim=claim_job(api.DEFAULT_DB_PATH,'worker')
    finish_job(api.DEFAULT_DB_PATH,'tamper','worker',claim['fence'],{'text':'original','model':'fixture','provider':'fixture'})
    assert client.get('/v1/jobs/tamper/result',headers=auth()).status_code==200
    with sqlite3.connect(api.DEFAULT_DB_PATH) as conn:
        conn.execute('UPDATE jobs SET result_json=? WHERE id=?',(json.dumps({'text':'CORRUPT'}),'tamper'))
    response=client.get('/v1/jobs/tamper/result',headers=auth())
    assert response.status_code==409
    assert 'CORRUPT' not in response.text


def test_invalid_identity_config_never_ready(client, monkeypatch):
    from aurex.database import register_worker
    register_worker(api.DEFAULT_DB_PATH,'worker')
    monkeypatch.setenv('AUREX_USER_TOKENS',json.dumps({'alice':TOKEN}))
    assert client.get('/health/ready').status_code==503


def test_authorized_durable_job_contract(client, monkeypatch):
    from aurex.database import claim_job, finish_job, register_worker
    monkeypatch.setenv('AUREX_EXECUTION_ENABLED','true')
    register_worker(api.DEFAULT_DB_PATH,'worker')
    headers={**auth('b'),'Idempotency-Key':'same'}
    payload={'kind':'local_inference','params':{'prompt':'Explain historical observation vs current authority'},'maxCostUsd':0}
    first=client.post('/v1/jobs',headers=headers,json=payload)
    assert first.status_code==200
    job=first.json()
    assert client.post('/v1/jobs',headers=headers,json=payload).json()['id']==job['id']
    payload['params']['prompt']='different'
    assert client.post('/v1/jobs',headers=headers,json=payload).status_code==409
    claim=claim_job(api.DEFAULT_DB_PATH,'worker')
    assert finish_job(api.DEFAULT_DB_PATH,job['id'],'worker',claim['fence'],{'text':'SYNTHETIC FIXTURE','provider':'fixture','model':'fixture','modelIdentity':'DECLARED'})
    result=client.get('/v1/jobs/'+job['id']+'/result',headers=auth('b')).json()
    assert result['result']=={'text':'SYNTHETIC FIXTURE','provider':'fixture','model':'fixture','verification':'NOT VERIFIED','authorityGranted':False}
    assert client.get('/v1/jobs/'+job['id']+'/evidence',headers=auth('b')).json()['evidence'][0]['integrity']=='PASS'
    assert client.get('/v1/jobs/'+job['id']+'/result',headers=auth('c')).status_code==404


def test_analytics_is_owner_only_and_never_accepts_job_claims(client):
    assert client.get('/v1/analytics').status_code==401
    assert client.get('/v1/analytics',headers=auth('b')).status_code==403
    assert client.post('/v1/analytics/events',headers=auth(),json={'event':'job_completed'}).status_code==422
    assert client.post('/v1/analytics/events',headers=auth(),json={'event':'page_view','route':'/aurex?secret=discard'}).status_code==202
    report=client.get('/v1/analytics',headers=auth()).json()
    assert report['counts']=={'page_view':1}
    assert report['uniqueVisitors'] is None


def test_disabled_execution_is_never_ready(client):
    from aurex.database import register_worker
    register_worker(api.DEFAULT_DB_PATH,'worker',model_configured=True)
    assert client.get('/health/ready').status_code==503


def test_evidence_capability_matches_frontend_contract(client):
    from aurex.database import claim_job, finish_job
    create_job(api.DEFAULT_DB_PATH,'contract','local_inference',{'prompt':'test'})
    lease=claim_job(api.DEFAULT_DB_PATH,'worker')
    finish_job(api.DEFAULT_DB_PATH,'contract','worker',lease['fence'],{'text':'fixture','model':'fixture','provider':'fixture'})
    evidence=client.get('/v1/jobs/contract/evidence',headers=auth()).json()['evidence'][0]
    assert evidence['capabilityId']=='local-inference'
