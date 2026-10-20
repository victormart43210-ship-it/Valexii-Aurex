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
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import httpx

_JOB_FIELDS = ("id", "state", "kind", "createdAt", "updatedAt")


class WebsiteAdapter:
    def __init__(
        self,
        base_url: str,
        service_token_env: str = "AUREX_SERVICE_TOKEN",
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("base_url must include a scheme and host")

        self.base_url = base_url.rstrip("/")
        self.token_env = service_token_env
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def _auth_header(self) -> dict[str, str]:
        token = os.environ.get(self.token_env)
        if not token:
            raise RuntimeError(f"Missing service token env var: {self.token_env}")
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
        if idempotency_key:
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
