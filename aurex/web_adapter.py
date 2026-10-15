"""Server-side website adapter (minimal, safe scaffold)

This module is a minimal, well-tested scaffold meant to be used on the server-side of VALEXII.COM. It is NOT a frontend library.

Responsibilities:
- Send authenticated requests to AUREX API (server-to-server)
- Preserve Idempotency-Key
- Sanitize and return only allowed fields to upstream handlers

The adapter uses httpx for HTTP interactions and expects a server-side environment variable
`AUREX_SERVICE_TOKEN` to be set. This module performs conservative validation and is suitable
for rapid integration with Lovable server routes.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx


class WebsiteAdapter:
    def __init__(self, base_url: str, service_token_env: str = "AUREX_SERVICE_TOKEN") -> None:
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url.rstrip("/")
        self.token_env = service_token_env
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def _auth_header(self) -> Dict[str, str]:
        token = os.environ.get(self.token_env)
        if not token:
            raise RuntimeError(f"Missing service token env var: {self.token_env}")
        return {"Authorization": f"Bearer {token}"}

    def create_job(self, payload: Dict[str, Any], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        headers = self._auth_header()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        resp = self._client.post("/v1/jobs", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # Only surface known safe fields
        return {k: data[k] for k in ("id", "state", "kind", "createdAt", "updatedAt") if k in data}

    def get_job(self, job_id: str) -> Dict[str, Any]:
        headers = self._auth_header()
        resp = self._client.get(f"/v1/jobs/{job_id}", headers=headers)
        if resp.status_code == 404:
            raise KeyError("job not found")
        resp.raise_for_status()
        data = resp.json()
        return {k: data[k] for k in ("id", "state", "kind", "createdAt", "updatedAt") if k in data}


# Lightweight convenience function for server handlers
def create_and_return_job(base_url: str, payload: Dict[str, Any], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
    adapter = WebsiteAdapter(base_url)
    return adapter.create_job(payload, idempotency_key=idempotency_key)
