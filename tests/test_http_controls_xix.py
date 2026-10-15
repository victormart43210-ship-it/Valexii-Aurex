import logging

from fastapi.testclient import TestClient

from aurex import api


def test_correlation_and_redacted_validation(monkeypatch,caplog):
    monkeypatch.setenv('AUREX_SERVICE_TOKEN','a'*32)
    with caplog.at_level(logging.INFO,logger='aurex.http'):
        response=TestClient(api.app).post('/v1/jobs',headers={'Authorization':'Bearer '+'a'*32,'X-Request-ID':'bad-secret-id'},json={'kind':'local_inference','params':{'prompt':'SENSITIVE','extra':'SECRET'}})
    assert response.status_code==422
    assert 'SENSITIVE' not in response.text
    assert 'SECRET' not in response.text
    assert response.headers.get('x-request-id')
    assert response.headers['x-request-id']!='bad-secret-id'
    assert 'SENSITIVE' not in caplog.text
    assert 'bad-secret-id' not in caplog.text
    assert '/v1/jobs' in caplog.text


def test_rate_limit_is_bounded():
    from fastapi import FastAPI

    from aurex.http_controls import HTTPControls
    app=FastAPI()
    app.add_middleware(HTTPControls,limit=2)
    @app.get('/')
    def index(): return {'ok':True}
    c=TestClient(app)
    assert c.get('/').status_code==200
    assert c.get('/').status_code==200
    assert c.get('/').status_code==429
