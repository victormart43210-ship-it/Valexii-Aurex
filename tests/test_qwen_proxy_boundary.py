"""Prove local inference bypasses inherited proxy environment settings."""
import json
from unittest.mock import patch
from urllib.request import ProxyHandler

import pytest

from aurex.local_inference import run_local_inference


class _Reply:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _limit):
        return self.payload


@pytest.mark.parametrize("backend,payload", [
    ("llama.cpp", {"choices": [{"message": {"content": "ok"}}]}),
    ("ollama", {"response": "ok"}),
])
def test_local_call_disables_proxy_handlers(backend, payload, monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://attacker.invalid:9999")
    monkeypatch.setenv("HTTPS_PROXY", "http://attacker.invalid:9999")
    with patch("aurex.local_inference.build_opener") as opener:
        opener.return_value.open.return_value = _Reply(json.dumps(payload).encode())
        result = run_local_inference(
            prompt="synthetic local test", model="qwen-local",
            base_url="http://127.0.0.1:8080",
            backend=backend, approved=True,
        )
    handlers = opener.call_args.args
    assert any(isinstance(handler, ProxyHandler) and handler.proxies == {} for handler in handlers)
    assert result.text == "ok" and result.authority_granted is False
