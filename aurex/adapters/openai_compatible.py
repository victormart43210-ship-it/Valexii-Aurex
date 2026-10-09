"""Credential-scoped OpenAI-compatible HTTPS model adapter."""

import json
import os
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from aurex.adapters.base import GenerationSettings, ModelAdapter, ModelAnswer


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
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
        generation: GenerationSettings | None = None,
        local_loopback: bool = False,
    ) -> None:
        url = urlsplit(base_url)
        allowed_scheme = "http" if local_loopback else "https"
        if local_loopback and url.hostname not in ("127.0.0.1", "::1"):
            raise ValueError("Local inference requires a literal loopback address")
        if (
            url.scheme != allowed_scheme
            or not url.hostname
            or url.username
            or url.password
            or url.query
            or url.fragment
            or not model
        ):
            raise ValueError("Model endpoint requires a credential-free HTTPS URL")
        if not (0 < timeout_seconds <= 180):
            raise ValueError("Invalid timeout")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.provider = provider
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds
        self.generation = generation or GenerationSettings()
        self.local_loopback = local_loopback

    def answer(self, prompt: str) -> ModelAnswer:
        key = None if self.local_loopback else os.environ.get(self.api_key_env)
        if not self.local_loopback and not key:
            raise RuntimeError(f"Missing credential environment variable: {self.api_key_env}")
        body = json.dumps(
            {
                "model": self.model,
                **self.generation.model_dump(),
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()
        request = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {key}"} if key else {}),
            },
            method="POST",
        )
        with build_opener(_NoRedirect(), ProxyHandler({})).open(
            request, timeout=self.timeout_seconds
        ) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Model response exceeds allowed size")
        payload = json.loads(data.decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("Unexpected model content")
        usage = payload.get("usage") or {}
        return ModelAnswer(
            provider=self.provider,
            model=self.model,
            text=content,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )
