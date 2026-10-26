"""Remote inference must be denied before network dispatch."""

from aurex.adapters.execution import InferenceClient, ModelSpec


class RemoteAdapter:
    base_url = "https://integrate.api.nvidia.com/v1"

    def __init__(self):
        self.called = False

    def answer(self, prompt):
        self.called = True
        raise AssertionError("Remote adapter must never be called")


def test_remote_inference_denied_without_authorization():
    adapter = RemoteAdapter()
    spec = ModelSpec(
        provider="openai-compatible",
        model="synthetic-test",
        revision="test-only",
    )

    result = InferenceClient(adapter, spec).run("test", "synthetic prompt")

    assert result.status == "FAIL"
    assert adapter.called is False
