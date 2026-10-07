"""Credential-scoped OpenAI-compatible HTTPS model adapter."""
import json
import os
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from aurex.adapters.base import ModelAdapter, ModelAnswer


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Any:
        raise ValueError("Model endpoint redirects are forbidden")


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
        url = urlsplit(base_url)
        if (url.scheme != "https" or not url.hostname or url.username
                or url.password or url.query or url.fragment or not model):
            raise ValueError("Model endpoint requires a credential-free HTTPS URL")
        if not (0 < timeout_seconds <= 180):
            raise ValueError("Invalid timeout")
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
        with build_opener(_NoRedirect()).open(
            request, timeout=self.timeout_seconds
        ) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Model response exceeds allowed size")
        payload = json.loads(data.decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Unexpected model content")
        return ModelAnswer(provider=self.provider, model=self.model, text=content)
