"""Server-side VALEXII.COM adapter for authenticated calls to AUREX.

This module is intentionally conservative and should be used only on the
server side. It is not a browser-side client.

The adapter validates the target base URL, reads the service token only from a
trusted server environment variable, preserves Idempotency-Key headers when
provided, and sanitizes outgoing job payloads before returning them to an
upstream website route.

NOT VERIFIED UNTIL LIVE STAGING ACCESS IS PROVIDED.
"""
from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

import httpx

_JOB_FIELDS = ("id", "state", "kind", "createdAt", "updatedAt")
_SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _origin(value: str) -> tuple[str, str, int]:
    """Validate a root URL without following redirects, paths, or URL credentials."""
    if (
        not isinstance(value, str) or not value or len(value) > 2048
        or any(ord(char) <= 32 or ord(char) > 126 for char in value)
    ):
        raise ValueError("invalid backend URL")
    parsed = urlsplit(value)
    if (
        parsed.scheme not in ("https", "http") or not parsed.netloc
        or parsed.username is not None or parsed.password is not None
        or parsed.path not in ("", "/") or parsed.query or parsed.fragment
    ):
        raise ValueError("backend URL must be an origin without credentials or paths")
    host = parsed.hostname
    if not host or not host.isascii():
        raise ValueError("backend host is invalid")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid backend port") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("invalid backend port")
    if parsed.scheme == "http":
        if host not in ("127.0.0.1", "::1") or os.environ.get(
            "AUREX_ALLOW_HTTP_LOOPBACK"
        ) != "1":
            raise ValueError("HTTP backend is allowed only for explicit numeric loopback")
    return parsed.scheme, host.lower(), port or (443 if parsed.scheme == "https" else 80)


class WebsiteAdapter:
    def __init__(
        self,
        base_url: str,
        service_token_env: str = "AUREX_SERVICE_TOKEN",
    ) -> None:
        # Fail closed unless the operator pinned the exact backend origin.
        # Untrusted callers must not choose the destination for a bearer secret.
        pin = os.environ.get("AUREX_BACKEND_BASE_URL", "")
        if not pin:
            raise ValueError("AUREX_BACKEND_BASE_URL is not configured")
        if _origin(base_url) != _origin(pin):
            raise ValueError("backend destination differs from operator-pinned origin")
        if service_token_env != "AUREX_SERVICE_TOKEN":
            raise ValueError("only the AUREX service-token environment is permitted")

        self.base_url = base_url.rstrip("/")
        self.token_env = service_token_env
        self._client = httpx.Client(
            base_url=self.base_url, timeout=10.0, follow_redirects=False,
            trust_env=False,
        )

    def _auth_header(self) -> dict[str, str]:
        token = os.environ.get(self.token_env)
        if (
            not token or len(token) < 32 or len(token) > 512
            or not token.isascii() or token != token.strip()
        ):
            raise RuntimeError("AUREX service token is missing or insecure")
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _sanitize_job(payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("job payload must be a mapping")
        sanitized: dict[str, Any] = {}
        for key in _JOB_FIELDS:
            if key in payload:
                sanitized[key] = payload[key]
        return sanitized

    def create_job(
        self,
        payload: Mapping[str, Any],
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        headers = self._auth_header()
        if idempotency_key is not None:
            if not isinstance(idempotency_key, str) or not _SAFE_KEY.fullmatch(
                idempotency_key
            ):
                raise ValueError("invalid idempotency key")
            headers["Idempotency-Key"] = idempotency_key

        response = self._client.post(
            "/v1/jobs",
            json=dict(payload),
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("unexpected response payload for job creation")
        return self._sanitize_job(data)

    def get_job(self, job_id: str) -> dict[str, Any]:
        if not isinstance(job_id, str) or not _SAFE_KEY.fullmatch(job_id):
            raise ValueError("invalid job ID")
        headers = self._auth_header()
        response = self._client.get(f"/v1/jobs/{job_id}", headers=headers)
        if response.status_code == 404:
            raise KeyError("job not found")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("unexpected response payload for job retrieval")
        return self._sanitize_job(data)


__all__ = ["WebsiteAdapter", "create_and_return_job"]


def create_and_return_job(
    base_url: str,
    payload: Mapping[str, Any],
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    adapter = WebsiteAdapter(base_url)
    return adapter.create_job(payload, idempotency_key=idempotency_key)
