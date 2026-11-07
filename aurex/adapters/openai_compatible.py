"""Credential-scoped OpenAI-compatible HTTPS model adapter."""

import json
import os
import urllib.error
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from aurex.adapters.base import GenerationSettings, ModelAdapter, ModelAnswer


class ModelTransportError(RuntimeError):
    """A classified model failure. The message is a code, never a response or URL."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


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
        private_qwen = (
            base_url == "http://qwen-private-staging.railway.internal:8080/v1"
            and provider == "llama.cpp"
            and os.environ.get("AUREX_RAILWAY_PRIVATE_QWEN_ENABLED") == "1"
            and bool(os.environ.get("RAILWAY_ENVIRONMENT_ID"))
        )
        allowed_scheme = "http" if local_loopback or private_qwen else "https"
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

    def _request(self, path: str, body: bytes | None, timeout: float) -> dict[str, Any]:
        key = None if self.local_loopback else os.environ.get(self.api_key_env)
        if not self.local_loopback and not key:
            raise ModelTransportError("AUTHENTICATION_FAILURE")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if key:
            headers["Authorization"] = f"Bearer {key}"
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method="POST" if body is not None else "GET",
        )
        try:
            with build_opener(_NoRedirect(), ProxyHandler({})).open(
                request, timeout=timeout
            ) as response:
                status = getattr(response, "status", 200)
                data = response.read(2_000_001)
        except TimeoutError:
            raise ModelTransportError("TIMEOUT") from None
        except urllib.error.HTTPError as exc:
            code = {
                401: "AUTHENTICATION_FAILURE",
                403: "AUTHENTICATION_FAILURE",
                404: "MODEL_UNAVAILABLE",
                408: "TIMEOUT",
                429: "MODEL_UNAVAILABLE",
                503: "MODEL_UNAVAILABLE",
            }.get(exc.code, "PROVIDER_OR_SCHEMA_FAILURE")
            raise ModelTransportError(code) from None
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise ModelTransportError("TIMEOUT") from None
            raise ModelTransportError("MODEL_UNAVAILABLE") from None
        except OSError:
            raise ModelTransportError("MODEL_UNAVAILABLE") from None
        if status != 200 or len(data) > 2_000_000:
            raise ModelTransportError("PROVIDER_OR_SCHEMA_FAILURE")
        try:
            payload = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ModelTransportError("PROVIDER_OR_SCHEMA_FAILURE") from None
        if not isinstance(payload, dict):
            raise ModelTransportError("PROVIDER_OR_SCHEMA_FAILURE")
        return payload

    def answer(self, prompt: str) -> ModelAnswer:
        if not self.local_loopback:
            listing = self._request("/models", None, min(10.0, self.timeout_seconds))
            rows = listing.get("data")
            identifiers = [
                row.get("id") for row in rows if isinstance(row, dict)
            ] if isinstance(rows, list) else []
            if self.model not in identifiers:
                raise ModelTransportError("MODEL_IDENTITY_MISMATCH")
        body = json.dumps(
            {
                "model": self.model,
                **self.generation.model_dump(),
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()
        payload = self._request("/chat/completions", body, self.timeout_seconds)
        reported = payload.get("model")
        if reported != self.model and (reported is not None or not self.local_loopback):
            raise ModelTransportError("MODEL_IDENTITY_MISMATCH")
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise ModelTransportError("PROVIDER_OR_SCHEMA_FAILURE") from None
        if not isinstance(content, str):
            raise ModelTransportError("PROVIDER_OR_SCHEMA_FAILURE")
        usage = payload.get("usage") or {}
        return ModelAnswer(
            provider=self.provider,
            model=self.model,
            text=content,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )
