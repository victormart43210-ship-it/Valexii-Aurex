import pytest

from aurex.adapters.ollama import OllamaAdapter
from aurex.adapters.openai_compatible import OpenAICompatibleAdapter


@pytest.mark.parametrize("url", ["http://example.com", "https://user:pass@example.com",
                                 "https://example.com?token=123", "file:///tmp/data"])
def test_openai_unsafe_endpoint(url):
    with pytest.raises(ValueError):
        OpenAICompatibleAdapter(base_url=url, model="test")


@pytest.mark.parametrize("url", ["http://example.com:11434", "http://192.168.1.5:11434",
                                 "https://127.0.0.1:11434"])
def test_ollama_unsafe_endpoint(url):
    with pytest.raises(ValueError):
        OllamaAdapter(model="test", base_url=url)


def test_safe_endpoints_construct():
    assert OllamaAdapter(model="test").model == "test"
    assert OpenAICompatibleAdapter(base_url="https://example.com/v1", model="test").model == "test"
