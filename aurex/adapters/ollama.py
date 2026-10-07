"""Local Ollama adapter. Intended for loopback/private-network endpoints."""

import json
from urllib.request import Request, urlopen

from aurex.adapters.base import ModelAdapter, ModelAnswer


class OllamaAdapter(ModelAdapter):
    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def answer(self, prompt: str) -> ModelAnswer:
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode())
        return ModelAnswer(provider="ollama", model=self.model, text=payload["response"])
