"""Local-only inference boundary tests; no network calls."""
import json
from unittest.mock import patch
import pytest
from aurex.local_inference import run_local_inference, _endpoint, LocalInferenceError

class FakeResponse:
    status = 200
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size): return self.data

@pytest.mark.parametrize('url', ['https://127.0.0.1:8080', 'http://example.com:8080',
    'http://192.168.1.1:8080', 'http://127.0.0.1:8080/path',
    'http://user:pass@127.0.0.1:8080', 'http://127.0.0.1'])
def test_rejects_nonlocal_or_invalid_endpoints(url):
    with pytest.raises(ValueError): _endpoint(url)

def test_requires_approval():
    with pytest.raises(PermissionError):
        run_local_inference(prompt='hi', model='local', base_url='http://127.0.0.1:8080')

def test_rejects_oversized_prompt():
    with pytest.raises(ValueError):
        run_local_inference(prompt='x'*9000, model='local', base_url='http://127.0.0.1:8080', approved=True)

@pytest.mark.parametrize('backend,data', [
    ('llama.cpp', {'choices':[{'message':{'content':'hello'}}]}),
    ('ollama', {'response':'hello'}),
])
def test_local_output_is_never_authority(backend, data):
    with patch('aurex.local_inference.build_opener') as mock:
        mock.return_value.open.return_value = FakeResponse(json.dumps(data).encode())
        result = run_local_inference(prompt='hi', model='local', base_url='http://127.0.0.1:8080', backend=backend, approved=True)
    assert result.text == 'hello'
    assert result.verified is False
    assert result.authority_granted is False
    assert len(result.sha256) == 64

def test_invalid_response_fails_closed():
    with patch('aurex.local_inference.build_opener') as mock:
        mock.return_value.open.return_value = FakeResponse(b'{}')
        with pytest.raises(LocalInferenceError):
            run_local_inference(prompt='hi', model='local', base_url='http://127.0.0.1:8080', approved=True)
