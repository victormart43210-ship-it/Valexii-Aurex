import json

import pytest

from aurex.adapters.base import ModelAdapter, ModelAnswer
from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.adapters.llama_cpp import LlamaCppAdapter


class Fixture(ModelAdapter):
    provider = "fixture"
    model = "tiny"

    def answer(self, prompt):
        if prompt == "timeout":
            raise TimeoutError("Bearer SECRET_SENTINEL")
        if prompt == "bad":
            return ModelAnswer.model_construct(provider="fixture", model="tiny", text=None)
        return ModelAnswer(provider="fixture", model="tiny", text="4")


def client():
    return InferenceClient(
        Fixture(), ModelSpec(provider="fixture", model="tiny", revision="fixture-v1")
    )


@pytest.mark.parametrize("prompt", ["timeout", "bad"])
def test_failures_are_recorded_without_secret(prompt):
    r = client().run("q1", prompt)
    assert r.status == "FAIL"
    assert r.output is None
    assert "SECRET_SENTINEL" not in r.model_dump_json()
    assert r.elapsed_seconds >= 0


def test_success_is_execution_only():
    r = client().run("q1", "2+2")
    assert r.status == "PASS"
    assert r.verification_status == "NOT VERIFIED"
    assert r.output == "4"
    assert len(r.input_sha256) == len(r.output_sha256) == 64


def test_llama_endpoint_is_explicitly_loopback():
    with pytest.raises(ValueError):
        LlamaCppAdapter(model="tiny", base_url="http://example.com/v1")


def test_llama_payload_and_usage(monkeypatch):
    import io
    from types import SimpleNamespace

    from aurex.adapters.base import GenerationSettings

    def open_request(req, **kwargs):
        payload = json.loads(req.data)
        assert payload["temperature"] == 0.0
        assert payload["max_tokens"] == 20
        assert "Authorization" not in req.headers
        return io.BytesIO(
            b'{"choices":[{"message":{"content":"4"}}],"usage":{"prompt_tokens":5,"completion_tokens":1}}'
        )

    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener",
        lambda *args: SimpleNamespace(open=open_request),
    )
    a = LlamaCppAdapter(model="tiny", generation=GenerationSettings(max_tokens=20))
    answer = a.answer("2+2")
    assert answer.output_tokens == 1
    assert answer.input_tokens == 5


def test_real_loopback_http_contract():
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert payload["model"] == "fixture"
            response = json.dumps(
                {
                    "choices": [{"message": {"content": "4"}}],
                    "usage": {"prompt_tokens": 3, "completion_tokens": 1},
                }
            ).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = LlamaCppAdapter(
            model="fixture", base_url=f"http://127.0.0.1:{server.server_port}/v1"
        )
        r = InferenceClient(
            adapter, ModelSpec(provider="llama.cpp", model="fixture", revision="test-only")
        ).run("q", "2+2")
        assert r.status == "PASS" and r.output == "4" and r.output_tokens == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
