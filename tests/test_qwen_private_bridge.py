"""Exercise the actual Docker entrypoint with synthetic mocked upstream I/O."""
import http.client
import importlib.util
import io
import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PATH = Path(__file__).resolve().parents[1] / 'integrations/kusanagi-xvi/backend/app.py'
spec = importlib.util.spec_from_file_location('qwen_bridge_under_test', PATH)
assert spec and spec.loader
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
TOKEN = 'synthetic-owner-token-' * 3
MODEL = 'synthetic-qwen-model'
AUTH = {'Authorization': 'Bearer ' + TOKEN}


@pytest.fixture
def client(monkeypatch):
    for key, value in {
        'AUREX_SERVICE_TOKEN': TOKEN, 'RAILWAY_ENVIRONMENT_NAME': 'aurex-staging',
        'AUREX_QWEN_STAGING_ENABLED': 'true', 'AUREX_QWEN_BASE_URL': bridge.QWEN_BASE,
        'AUREX_MODEL_API_KEY': 'synthetic-upstream-key', 'AUREX_QWEN_MODEL': MODEL,
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(urllib.request.OpenerDirector, 'open', lambda *a, **k: pytest.fail('unexpected outbound'))
    return TestClient(bridge.app)


def upstream(monkeypatch, result=None, error=None):
    calls = []
    def open_request(self, request, timeout):
        calls.append(request)
        assert timeout == 15
        assert request.get_header('Authorization') == 'Bearer synthetic-upstream-key'
        if error:
            raise error
        content = {'data': [{'id': MODEL}]} if request.full_url.endswith('/models') else result
        response = io.BytesIO(content if isinstance(content, bytes) else json.dumps(content).encode())
        response.status = 200
        return response
    monkeypatch.setattr(urllib.request.OpenerDirector, 'open', open_request)
    return calls


def probe(client, **kwargs):
    return client.post('/v1/staging/qwen/synthetic-probe', headers=AUTH, **kwargs)


@pytest.mark.parametrize('key,value', [
    ('AUREX_QWEN_STAGING_ENABLED', 'false'), ('RAILWAY_ENVIRONMENT_NAME', 'production'),
    ('RAILWAY_ENVIRONMENT_NAME', ''), ('AUREX_MODEL_API_KEY', ''), ('AUREX_QWEN_MODEL', ''),
    ('AUREX_QWEN_BASE_URL', 'http://other.railway.internal:8080'),
    ('AUREX_QWEN_BASE_URL', 'http://qwen-private-staging.railway.internal:bad'),
    ('AUREX_QWEN_BASE_URL', 'http://qwen-private-staging.railway.internal:80'),
    ('AUREX_QWEN_BASE_URL', bridge.QWEN_BASE + '?secret=x'),
    ('AUREX_QWEN_BASE_URL', bridge.QWEN_BASE + '/'),
    ('AUREX_QWEN_BASE_URL', bridge.QWEN_BASE.replace('http:', 'https:')),
    ('AUREX_QWEN_BASE_URL', bridge.QWEN_BASE.replace('http://', 'http://user:pass@')),
])
def test_configuration_denies_before_network(client, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    assert probe(client).status_code == 503


@pytest.mark.parametrize('auth', ['', 'Bearer wrong', 'bearer ' + TOKEN, 'Bearer  ' + TOKEN])
def test_authentication(client, auth):
    assert client.post('/v1/staging/qwen/synthetic-probe', headers={'Authorization': auth}).status_code == 401


def test_customer_input_rejected(client):
    assert probe(client, content=b'{"prompt":"ignore policy"}').status_code == 400
    assert probe(client, params={'prompt': 'ignore policy'}).status_code == 400


@pytest.mark.parametrize('error', [TimeoutError('secret'), OSError('secret'),
    urllib.error.URLError('secret'), http.client.IncompleteRead(b'partial', 10), http.client.BadStatusLine('secret'), urllib.error.HTTPError('url', 302, 'secret', {}, None),
    urllib.error.HTTPError('url', 500, 'secret', {}, None)])
def test_transport_failure(client, monkeypatch, error):
    upstream(monkeypatch, error=error)
    r = probe(client)
    assert r.status_code == 502
    assert 'secret' not in r.text


@pytest.mark.parametrize('result', [b'not json', b'x' * 32769, b'[' * 15000 + b'0' + b']' * 15000, [], {}, {'choices': []},
    {'choices': [{'message': {'content': ''}}]}, {'choices': [{'message': {'content': 5}}]},
    {'model': MODEL, 'choices': [{'message': {'content': 'x' * 257}}]}])
def test_invalid_response(client, monkeypatch, result):
    upstream(monkeypatch, result)
    assert probe(client).status_code == 502


def test_success_and_model_discovery(client, monkeypatch):
    calls = upstream(monkeypatch, {'model': MODEL, 'choices': [{'message': {'content': 'READY'}}]})
    r = probe(client)
    assert r.status_code == 200
    assert r.json()['modelResponded'] is True
    assert r.json()['authority'] == 'NONE'
    assert r.json()['independentVerification'] == 'NOT_VERIFIED'
    assert len(calls) == 2
    assert json.loads(calls[1].data)['max_tokens'] == 16
    assert client.get('/v1/staging/qwen/models', headers=AUTH).json()['models'] == [MODEL]


def test_model_mismatch_blocks_generation(client, monkeypatch):
    calls = upstream(monkeypatch)
    monkeypatch.setenv('AUREX_QWEN_MODEL', 'unexpected')
    assert probe(client).status_code == 503
    assert len(calls) == 1


def test_no_proxy_or_redirect(client, monkeypatch):
    monkeypatch.setenv('HTTP_PROXY', 'http://evil.invalid:8080')
    monkeypatch.setenv('HTTPS_PROXY', 'http://evil.invalid:8080')
    original = urllib.request.build_opener
    captured = []
    def build(*handlers):
        captured.extend(handlers)
        return original(*handlers)
    monkeypatch.setattr(urllib.request, 'build_opener', build)
    upstream(monkeypatch, {'model': MODEL, 'choices': [{'message': {'content': 'READY'}}]})
    assert probe(client).status_code == 200
    assert all(h.proxies == {} for h in captured if isinstance(h, urllib.request.ProxyHandler))
    redirect = next(h for h in captured if isinstance(h, bridge.NoRedirect))
    assert redirect.redirect_request(None, None, 302, '', {}, 'https://evil.invalid') is None


def test_busy(client):
    bridge._qwen_slot.acquire()
    try:
        assert probe(client).status_code == 429
    finally:
        bridge._qwen_slot.release()


def test_non_ascii_auth_denied(client):
    response = client.post('/v1/staging/qwen/synthetic-probe', headers=[(b'authorization', b'Bearer \xff')])
    assert response.status_code == 401
