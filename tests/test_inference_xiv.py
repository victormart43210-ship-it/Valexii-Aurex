"""Controlled transport regressions; no model host or paid API is contacted."""

import io
import json
from types import SimpleNamespace
from urllib.error import URLError

import pytest

from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.adapters.llama_cpp import LlamaCppAdapter


def install_response(monkeypatch, payload):
    raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener",
        lambda *args: SimpleNamespace(open=lambda *args, **kwargs: io.BytesIO(raw)),
    )


def payload(**extra):
    return {"choices": [{"message": {"content": "4"}}], **extra}


def client():
    return InferenceClient(
        LlamaCppAdapter(model="tiny"),
        ModelSpec(provider="llama.cpp", model="tiny", revision="declared-test"),
    )


@pytest.mark.parametrize("model", ["other", "", None, 1])
def test_explicit_response_identity_must_match(monkeypatch, model):
    install_response(monkeypatch, payload(model=model))
    record = client().run("q", "2+2")
    assert record.status == "FAIL"
    assert record.output is None


@pytest.mark.parametrize("identity", [{}, {"model": "tiny"}])
def test_compatible_identity_remains_declared(monkeypatch, identity):
    install_response(monkeypatch, payload(**identity))
    record = client().run("q", "2+2")
    assert record.status == "PASS"
    assert record.model.identity_status == "DECLARED"
    assert record.verification_status == "NOT VERIFIED"


@pytest.mark.parametrize("content", ["", "  \n\t"])
def test_adapter_rejects_blank_content(monkeypatch, content):
    install_response(monkeypatch, {"choices": [{"message": {"content": content}}]})
    with pytest.raises(ValueError):
        LlamaCppAdapter(model="tiny").answer("q")


@pytest.mark.parametrize(
    "reason,expected",
    [
        (TimeoutError("SECRET_SENTINEL"), "TIMEOUT"),
        (OSError("SECRET_SENTINEL"), "PROVIDER_OR_SCHEMA_FAILURE"),
        ("timed out SECRET_SENTINEL", "PROVIDER_OR_SCHEMA_FAILURE"),
    ],
)
def test_wrapped_transport_errors_are_classified_without_text(monkeypatch, reason, expected):
    def fail(*args, **kwargs):
        raise URLError(reason)

    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener",
        lambda *args: SimpleNamespace(open=fail),
    )
    record = client().run("q", "q")
    assert record.status == "FAIL"
    assert record.error_code == expected
    assert "SECRET_SENTINEL" not in record.model_dump_json()


@pytest.mark.parametrize("delta", [0, 1])
def test_serialized_request_byte_limit(monkeypatch, delta):
    adapter = LlamaCppAdapter(model="tiny")
    empty_size = len(
        json.dumps(
            {
                "model": "tiny",
                **adapter.generation.model_dump(),
                "messages": [{"role": "user", "content": ""}],
            }
        ).encode()
    )
    prompt = "x" * (131072 - empty_size + delta)
    install_response(monkeypatch, payload())
    if delta:
        with pytest.raises(ValueError, match="request exceeds"):
            adapter.answer(prompt)
    else:
        assert adapter.answer(prompt).text == "4"


@pytest.mark.parametrize("delta", [0, 1])
def test_response_byte_limit(monkeypatch, delta):
    raw = json.dumps(payload()).encode()
    install_response(monkeypatch, raw + b" " * (2_000_000 - len(raw) + delta))
    if delta:
        with pytest.raises(ValueError, match="response exceeds"):
            LlamaCppAdapter(model="tiny").answer("q")
    else:
        assert LlamaCppAdapter(model="tiny").answer("q").text == "4"


@pytest.mark.parametrize(
    "invalid",
    [
        b"not json",
        [],
        {},
        {"choices": []},
        {"choices": [{"message": {"content": None}}]},
        payload(usage={"prompt_tokens": -1}),
    ],
)
def test_invalid_schema_returns_failure_without_output(monkeypatch, invalid):
    install_response(monkeypatch, invalid)
    record = client().run("q", "q")
    assert record.status == "FAIL"
    assert record.error_code == "PROVIDER_OR_SCHEMA_FAILURE"
    assert record.output is None


def test_request_limit_counts_serialized_unicode_bytes(monkeypatch):
    # JSON's escaped unicode occupies more wire bytes than prompt characters.
    install_response(monkeypatch, payload())
    with pytest.raises(ValueError, match="request exceeds"):
        LlamaCppAdapter(model="tiny").answer("é" * 30_000)


def test_direct_timeout_is_redacted(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("SECRET_SENTINEL")

    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener",
        lambda *args: SimpleNamespace(open=fail),
    )
    record = client().run("q", "q")
    assert record.error_code == "TIMEOUT"
    assert record.status == "FAIL"
    assert "SECRET_SENTINEL" not in record.model_dump_json()
