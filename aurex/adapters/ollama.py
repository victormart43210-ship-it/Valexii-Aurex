"""Loopback-only Ollama adapter; no remote Ollama hosts or redirects."""

import json
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from aurex.adapters.base import GenerationSettings, ModelAdapter, ModelAnswer


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        raise ValueError("Ollama redirects are forbidden")


class OllamaAdapter(ModelAdapter):
    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 120.0,
        generation: GenerationSettings | None = None,
    ) -> None:
        url = urlsplit(base_url)
        if (
            url.scheme != "http"
            or url.hostname not in ("localhost", "127.0.0.1", "::1")
            or url.username
            or url.password
            or url.query
            or url.fragment
            or not model
            or not (0 < timeout_seconds <= 180)
        ):
            raise ValueError("Ollama requires an HTTP loopback endpoint and valid timeout")
        self.provider = "ollama"
        self.generation = generation or GenerationSettings()
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def answer(self, prompt: str) -> ModelAnswer:
        body = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.generation.temperature,
                    "seed": self.generation.seed,
                    "num_predict": self.generation.max_tokens,
                },
            }
        ).encode()
        request = Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with build_opener(_NoRedirect(), ProxyHandler({})).open(
            request, timeout=self.timeout_seconds
        ) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Ollama response exceeds allowed size")
        payload = json.loads(data.decode("utf-8"))
        text = payload["response"]
        if not isinstance(text, str):
            raise TypeError("Unexpected Ollama response")
        return ModelAnswer(
            provider="ollama",
            model=self.model,
            text=text,
            input_tokens=payload.get("prompt_eval_count"),
            output_tokens=payload.get("eval_count"),
        )
