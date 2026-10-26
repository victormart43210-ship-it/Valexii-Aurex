"""No provider request may occur before durable remote admission exists."""

import pytest

from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.adapters.openai_compatible import OpenAICompatibleAdapter
from aurex.evals.cli import build_client


@pytest.mark.parametrize("enable", [None, "0", "1", "true"])
def test_direct_remote_adapter_never_dispatches(monkeypatch, enable):
    monkeypatch.setenv("AUREX_MODEL_API_KEY", "synthetic-secret")
    if enable is not None:
        monkeypatch.setenv("AUREX_REMOTE_INFERENCE_ENABLED", enable)
    calls = []

    def forbidden(*args):
        calls.append(args)
        raise AssertionError("network attempted")

    monkeypatch.setattr("aurex.adapters.openai_compatible.build_opener", forbidden)
    adapter = OpenAICompatibleAdapter(
        base_url="https://integrate.api.nvidia.com/v1", model="fixture"
    )
    with pytest.raises(RuntimeError, match="REMOTE_INFERENCE_DISABLED"):
        adapter.answer("synthetic")
    assert calls == []


def test_client_records_specific_remote_denial(monkeypatch):
    monkeypatch.setenv("AUREX_MODEL_API_KEY", "synthetic-secret")
    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener", lambda *a: pytest.fail("network")
    )
    adapter = OpenAICompatibleAdapter(base_url="https://example.com/v1", model="fixture")
    result = InferenceClient(
        adapter, ModelSpec(provider="openai-compatible", model="fixture", revision="test")
    ).run("q", "synthetic")
    assert result.status == "FAIL"
    assert result.error_code == "REMOTE_INFERENCE_DISABLED"
    assert result.output is None
    assert "synthetic-secret" not in result.model_dump_json()


def test_mutating_local_flag_cannot_authorize_remote(monkeypatch):
    adapter = OpenAICompatibleAdapter(base_url="https://example.com/v1", model="fixture")
    adapter.local_loopback = True
    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener", lambda *a: pytest.fail("network")
    )
    with pytest.raises(RuntimeError, match="REMOTE_INFERENCE_DISABLED"):
        adapter.answer("synthetic")


def test_ollama_factory_accepts_generation_settings():
    client = build_client(
        {
            "identity": {"provider": "ollama", "model": "fixture", "revision": "test"},
            "base_url": "http://127.0.0.1:11434",
            "generation": {"max_tokens": 12},
        }
    )
    assert client.generation.max_tokens == 12
