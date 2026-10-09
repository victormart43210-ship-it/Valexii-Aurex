"""llama-server adapter. Local service startup is an external prerequisite."""

from aurex.adapters.base import GenerationSettings
from aurex.adapters.openai_compatible import OpenAICompatibleAdapter


class LlamaCppAdapter(OpenAICompatibleAdapter):
    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://127.0.0.1:8080/v1",
        generation: GenerationSettings | None = None,
        timeout_seconds: float = 60,
    ) -> None:
        super().__init__(
            model=model,
            base_url=base_url,
            provider="llama.cpp",
            local_loopback=True,
            generation=generation,
            timeout_seconds=timeout_seconds,
        )
