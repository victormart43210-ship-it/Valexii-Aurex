"""Backend-token egress controls for VALEXII.COM's server-side adapter.

All requests here use an in-memory fake transport; no backend is contacted.
"""

import pytest

from aurex.web_adapter import WebsiteAdapter

BACKEND = "https://aurex-ci.invalid"
TOKEN = "a" * 32


class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not 200 <= self.status_code < 300:
            raise RuntimeError(f"HTTP {self.status_code}")


class DummyClient:
    def __init__(self):
        self.calls = []

    def post(self, path, json=None, headers=None):
        self.calls.append(("POST", path, json, headers))
        return DummyResponse(
            200, {
                "id": "job-1", "state": "queued", "kind": json.get("kind", "unknown"),
                "createdAt": "t", "updatedAt": "t", "payloadSecret": "MUST_NOT_EXPOSE",
            }
        )

    def get(self, path, headers=None):
        self.calls.append(("GET", path, None, headers))
        if path.endswith("/jobs/job-1"):
            return DummyResponse(
                200, {
                    "id": "job-1", "state": "succeeded",
                    "kind": "regression_scan", "createdAt": "t",
                    "updatedAt": "t", "payloadSecret": "MUST_NOT_EXPOSE",
                }
            )
        return DummyResponse(404, {})


@pytest.fixture(autouse=True)
def fix_token(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    monkeypatch.setenv("AUREX_BACKEND_BASE_URL", BACKEND)
    monkeypatch.delenv("AUREX_ALLOW_HTTP_LOOPBACK", raising=False)


def test_create_job_and_get_job_without_leaking_response_fields():
    adapter = WebsiteAdapter(BACKEND)
    assert adapter._client.follow_redirects is False
    adapter._client.close()
    adapter._client = DummyClient()

    payload = {"kind": "regression_scan", "params": {}, "maxCostUsd": 0.0}
    job = adapter.create_job(payload, idempotency_key="idempotent.1")
    assert job["id"] == "job-1"
    assert job["state"] == "queued"
    assert "payloadSecret" not in job
    assert adapter._client.calls[0][3]["Authorization"] == f"Bearer {TOKEN}"
    assert adapter._client.calls[0][3]["Idempotency-Key"] == "idempotent.1"

    result = adapter.get_job("job-1")
    assert result["id"] == "job-1"
    assert result["state"] == "succeeded"
    assert "payloadSecret" not in result


def test_missing_service_token(monkeypatch):
    monkeypatch.delenv("AUREX_SERVICE_TOKEN", raising=False)
    adapter = WebsiteAdapter(BACKEND)
    adapter._client.close()
    adapter._client = DummyClient()
    with pytest.raises(RuntimeError, match="service token"):
        adapter.create_job({"kind": "regression_scan"})


@pytest.mark.parametrize("bad_token", ["short", "é" * 32, "b" * 513])
def test_malformed_service_token_never_forwarded(monkeypatch, bad_token):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", bad_token)
    adapter = WebsiteAdapter(BACKEND)
    adapter._client.close()
    adapter._client = DummyClient()
    with pytest.raises(RuntimeError):
        adapter.get_job("job-1")
    assert adapter._client.calls == []


def test_origin_pin_is_required(monkeypatch):
    monkeypatch.delenv("AUREX_BACKEND_BASE_URL", raising=False)
    with pytest.raises(ValueError, match="not configured"):
        WebsiteAdapter(BACKEND)


@pytest.mark.parametrize(
    "untrusted",
    [
        "https://attacker.invalid", "http://attacker.invalid",
        "https://user:password@aurex-ci.invalid",
        "https://aurex-ci.invalid/v1/jobs", "https://aurex-ci.invalid?leak=1",
        "https://aurex-ci.invalid#fragment", "ftp://aurex-ci.invalid",
        "https://aurex-ci.invalid\n.example",
    ],
)
def test_refuse_non_pinned_or_malformed_destination(untrusted):
    with pytest.raises(ValueError):
        WebsiteAdapter(untrusted)


def test_public_plaintext_backend_is_rejected_even_if_operator_pinned(monkeypatch):
    monkeypatch.setenv("AUREX_BACKEND_BASE_URL", "http://external.invalid")
    monkeypatch.setenv("AUREX_ALLOW_HTTP_LOOPBACK", "1")
    with pytest.raises(ValueError, match="HTTP backend"):
        WebsiteAdapter("http://external.invalid")


def test_numeric_loopback_requires_explicit_optin(monkeypatch):
    url = "http://127.0.0.1:8765"
    monkeypatch.setenv("AUREX_BACKEND_BASE_URL", url)
    with pytest.raises(ValueError, match="HTTP backend"):
        WebsiteAdapter(url)
    monkeypatch.setenv("AUREX_ALLOW_HTTP_LOOPBACK", "1")
    adapter = WebsiteAdapter(url)
    assert adapter.base_url == url
    adapter._client.close()


def test_refuse_arbitrary_token_env_even_with_correct_origin():
    with pytest.raises(ValueError, match="only the AUREX"):
        WebsiteAdapter(BACKEND, service_token_env="DATABASE_PASSWORD")


@pytest.mark.parametrize(
    "unsafe", ["../../admin", "job-1?all=true", "https://evil.invalid", "", "a" * 129],
)
def test_job_id_cannot_inject_a_new_path(unsafe):
    adapter = WebsiteAdapter(BACKEND)
    adapter._client.close()
    adapter._client = DummyClient()
    with pytest.raises(ValueError, match="job ID"):
        adapter.get_job(unsafe)
    assert adapter._client.calls == []


@pytest.mark.parametrize("unsafe", ["id\nother", "a" * 129, "?query", ""])
def test_idempotency_header_is_bounded_and_simple(unsafe):
    adapter = WebsiteAdapter(BACKEND)
    adapter._client.close()
    adapter._client = DummyClient()
    with pytest.raises(ValueError, match="idempotency"):
        adapter.create_job({"kind": "regression_scan"}, idempotency_key=unsafe)
    assert adapter._client.calls == []
