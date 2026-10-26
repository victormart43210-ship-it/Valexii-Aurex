import pytest
from fastapi.testclient import TestClient

from aurex import agent
from aurex.adapters.base import ModelAnswer
from aurex.api import app
from aurex.xaeli import api as xapi
from aurex.xaeli import core

TOKEN = "synthetic-local-only-" + "x" * 32
H = {"Authorization": "Bearer " + TOKEN}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    xapi.limiter = core.RateLimiter(100, 60, 1000)
    return TestClient(app)


def fake(text, calls=None):
    class A:
        model = "qwen3:0.6b"
        def answer(self, prompt):
            if calls is not None:
                calls.append(prompt)
            return ModelAnswer(provider="ollama", model=self.model, text=text)
    return lambda: A()


def test_extract_final():
    assert agent.extract_final("<think>secret</think>Answer") == "Answer"
    assert agent.extract_final("<think>unterminated") == ""


def test_requires_auth(client):
    assert client.post("/v1/agent/ask", json={"question": "hi"}).status_code == 401
    assert client.get("/v1/agent/status").status_code == 401


def test_ask_strips_thinking_and_correlates(client, monkeypatch):
    monkeypatch.setattr(agent, "_adapter", fake("<think>x</think>XAELI is an assistant."))
    r = client.post("/v1/agent/ask", json={"question": "what is XAELI assistant"},
                    headers={**H, "X-Request-ID": "req-12345678"})
    j = r.json()
    assert r.status_code == 200 and j["answer"] == "XAELI is an assistant."
    assert "think" not in r.text and r.headers["x-request-id"] == "req-12345678"
    assert j["citations"][0]["id"] == "pub-001"


def test_inference_failure_not_fabricated(client, monkeypatch):
    def boom():
        raise OSError("down")
    monkeypatch.setattr(agent, "_adapter", boom)
    r = client.post("/v1/agent/ask", json={"question": "what is XAELI"}, headers=H)
    assert r.status_code == 502 and "answer" not in r.json()["detail"]


def test_only_thinking_is_error(client, monkeypatch):
    monkeypatch.setattr(agent, "_adapter", fake("<think>only"))
    assert client.post("/v1/agent/ask", json={"question": "what is XAELI"}, headers=H).status_code == 502


def test_non_chat_routes_not_sent_to_model(client, monkeypatch):
    calls = []
    monkeypatch.setattr(agent, "_adapter", fake("x", calls))
    r = client.post("/v1/agent/ask", json={"question": "deploy to production"}, headers=H)
    assert r.json()["state"] == "REFERRED" and not calls


def test_bounds_and_remote_rejected(client, monkeypatch):
    assert client.post("/v1/agent/ask", json={"question": "a" * 1001}, headers=H).status_code == 422
    monkeypatch.setenv("AUREX_QWEN_URL", "http://10.0.0.5:11434")
    assert client.get("/v1/agent/status", headers=H).json()["state"] == "MISCONFIGURED"


def test_status_unreachable(client, monkeypatch):
    monkeypatch.setenv("AUREX_QWEN_URL", "http://127.0.0.1:1")
    j = client.get("/v1/agent/status", headers=H).json()
    assert j["reachable"] is False and j["state"] == "UNREACHABLE"
