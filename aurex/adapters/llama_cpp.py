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
        from urllib.parse import urlsplit

        private_url = "http://qwen-private-staging.railway.internal:8080/v1"
        private_staging = base_url == private_url

        if private_staging:
            import os
            if os.environ.get("AUREX_RAILWAY_PRIVATE_QWEN_ENABLED") != "1":
                raise ValueError("Private Qwen staging is disabled")
            if not os.environ.get("RAILWAY_ENVIRONMENT_ID"):
                raise ValueError("Railway environment verification required")

        super().__init__(
            model=model,
            base_url=base_url,
            provider="llama.cpp",
            local_loopback=not private_staging,
            generation=generation,
            timeout_seconds=timeout_seconds,
        )
