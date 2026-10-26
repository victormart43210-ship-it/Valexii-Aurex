"""Remote inference must fail closed at the adapter boundary."""

import pytest

from aurex.adapters.openai_compatible import OpenAICompatibleAdapter


def test_remote_adapter_denied_before_network(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-not-real")

    def forbidden_network(*args, **kwargs):
        raise AssertionError("Network access must not occur")

    monkeypatch.setattr(
        "aurex.adapters.openai_compatible.build_opener",
        forbidden_network,
    )

    adapter = OpenAICompatibleAdapter(
        base_url="https://integrate.api.nvidia.com/v1",
        model="synthetic-test",
        provider="llama.cpp",
    )

    with pytest.raises(RuntimeError, match="REMOTE_INFERENCE_DISABLED"):
        adapter.answer("synthetic prompt")
