"""CLII auth, payload admission, deterministic fixtures and malformed-record gates."""
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from aurex.api import app
from aurex.governance_math.industrial_readiness import EvidenceRecord, assess_readiness

TOKEN = 'synthetic-local-only-' + 'x' * 32


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('AUREX_SERVICE_TOKEN', TOKEN)
    monkeypatch.delenv('AUREX_ADMIN_TOKEN', raising=False)
    monkeypatch.setenv('AUREX_ENABLE_INDUSTRIAL_DEMO', '1')
    monkeypatch.setenv('AUREX_DEPLOYMENT_SCOPE', 'sandbox')
    return TestClient(app)


def call(client, body='{"fixture":"towing_v1"}', **kwargs):
    return client.post('/v1/industrial/audit/demo', content=body,
                       headers={'Authorization': 'Bearer ' + TOKEN,
                                'Content-Type': 'application/json'}, **kwargs)


def test_readiness_requires_authentication(client):
    assert client.get('/v1/industrial-audit/readiness').status_code == 401


def test_readiness_fails_closed_until_tenant_and_receipt_controls_exist(client):
    response = client.get(
        '/v1/industrial-audit/readiness',
        headers={'Authorization': 'Bearer ' + TOKEN},
    )
    assert response.status_code == 503
    assert response.headers['cache-control'] == 'no-store'
    body = response.json()
    assert body['status'] == 'NOT_VERIFIED'
    assert body['authority'] == 'ADVISORY_ONLY_NO_CERTIFICATION'
    assert {item['control'] for item in body['now']} == {
        'tenant_mapping', 'tenant_scoped_persistence', 'receipt_verification',
    }
    assert {item['control'] for item in body['next']} == {
        'tenant_mapping', 'tenant_scoped_persistence', 'receipt_verification',
    }
    assert body['changed'] == 'NOT_VERIFIED_NO_PRIOR_SNAPSHOT'
    assert body['proof']['status'] == 'NOT_VERIFIED'


def test_authenticated_demo_is_deterministic_and_advisory(client):
    first, second = call(client), call(client)
    assert first.status_code == 200
    assert first.json() == second.json()
    d = first.json()
    assert d['operator'] == 'Permian Recovery Services (fictional)'
    assert d['as_of'] == '2026-10-24'
    assert d['proof']['status'] == 'NOT_VERIFIED'
    assert d['authority'] == 'ADVISORY_ONLY_NO_CERTIFICATION'
    assert [f['status'] for f in d['now']] == ['PRESENT_NOT_VERIFIED', 'EXPIRED', 'CONFLICTING', 'NOT_VERIFIED', 'MISSING']
    assert first.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize('authorization', ['', 'Bearer bad', 'Basic x', 'Bearer', 'Bearer '+TOKEN+'x'])
def test_missing_invalid_auth(client, authorization):
    response = client.post('/v1/industrial/audit/demo', json={'fixture':'towing_v1'},
                           headers={'Authorization':authorization})
    assert response.status_code == 401


@pytest.mark.parametrize('body', ['{}', '[]', 'null', '{', '{"fixture":"customer"}', '{"fixture":"towing_v1","records":[]}', '{"fixture":"towing_v1","tenant":"other"}', '{"fixture":"towing_v1","fixture":"oilfield_v1"}'])
def test_payload_rejected(client, body):
    assert call(client, body).status_code == 422


def test_size_type_and_scope_fail_closed(client, monkeypatch):
    assert call(client, ' ' * 129).status_code == 413
    r = client.post('/v1/industrial/audit/demo', content='{}', headers={'Authorization':'Bearer '+TOKEN})
    assert r.status_code == 415
    monkeypatch.setenv('AUREX_DEPLOYMENT_SCOPE', 'production')
    assert call(client).status_code == 503
    monkeypatch.setenv('AUREX_DEPLOYMENT_SCOPE', 'sandbox')
    monkeypatch.delenv('AUREX_ENABLE_INDUSTRIAL_DEMO')
    assert call(client).status_code == 503


def test_oilfield_uses_same_engine(client):
    r = call(client, '{"fixture":"oilfield_v1"}')
    assert r.status_code == 200
    assert r.json()['now'][0]['category'] == 'crew_qualification'
    assert r.json()['proof']['status'] == 'NOT_VERIFIED'


@pytest.mark.parametrize('record', [EvidenceRecord(123, 'a', 'a'*64), EvidenceRecord('a', None, 'a'*64), EvidenceRecord('a','a',None), EvidenceRecord('a','a','a'*64,'yesterday')])
def test_malformed_record_types_fail_closed(record):
    with pytest.raises(ValueError):
        assess_readiness((record,), ('a',), as_of=date(2026,10,24))


def test_datetime_and_unhashable_categories_rejected():
    with pytest.raises(ValueError):
        assess_readiness((), ('a',), as_of=datetime(2026,10,24))
    with pytest.raises(ValueError):
        assess_readiness((), ([],), as_of=date(2026,10,24))
