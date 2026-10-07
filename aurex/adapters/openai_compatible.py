"""Minimal OpenAI-compatible HTTP adapter using the standard library.

No credentials are accepted in source code. Supply an API key through the named
environment variable at runtime.
"""

import json
import os
from urllib.request import Request, urlopen

from aurex.adapters.base import ModelAdapter, ModelAnswer


class OpenAICompatibleAdapter(ModelAdapter):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        provider: str = "openai-compatible",
        api_key_env: str = "AUREX_MODEL_API_KEY",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.provider = provider
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds

    def answer(self, prompt: str) -> ModelAnswer:
        key = os.environ.get(self.api_key_env)
        if not key:
            raise RuntimeError(f"Missing credential environment variable: {self.api_key_env}")
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        request = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode())
        text = payload["choices"][0]["message"]["content"]
        return ModelAnswer(provider=self.provider, model=self.model, text=text)
