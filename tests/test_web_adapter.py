
import pytest

from aurex.web_adapter import WebsiteAdapter


class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise RuntimeError(f"HTTP {self.status_code}")


class DummyClient:
    def __init__(self):
        self.calls = []

    def post(self, path, json=None, headers=None):
        self.calls.append(("POST", path, json, headers))
        return DummyResponse(200, {"id": "job-1", "state": "queued", "kind": json.get("kind", "unknown"), "createdAt": "t", "updatedAt": "t"})

    def get(self, path, headers=None):
        self.calls.append(("GET", path, None, headers))
        if path.endswith("/jobs/job-1"):
            return DummyResponse(200, {"id": "job-1", "state": "succeeded", "kind": "regression_scan", "createdAt": "t", "updatedAt": "t"})
        return DummyResponse(404, {})


@pytest.fixture(autouse=True)
def fix_token(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "a" * 32)
    monkeypatch.setenv("AUREX_EGRESS_ALLOWLIST", "example.local")


def test_create_job_and_get_job(monkeypatch):
    adapter = WebsiteAdapter("http://example.local")
    adapter._client = DummyClient()

    payload = {"kind": "regression_scan", "params": {}, "maxCostUsd": 0.0, "invoice_id": "I1"}
    job = adapter.create_job(payload)
    posted = adapter._client.calls[0][2]
    assert set(posted) <= {"id", "state", "kind", "createdAt", "updatedAt"}
    assert "invoice_id" not in posted
    assert job["id"] == "job-1"
    adapter.create_job({"kind": '{"invoice_id":"I1","amount":"100.00"}'})
    assert "kind" not in adapter._client.calls[1][2]
    adapter._client.get = lambda path, headers=None: DummyResponse(
        200,
        {
            "id": "job-1",
            "state": "succeeded",
            "kind": "regression_scan",
            "createdAt": "2026-11-06T17:00:00+00:00",
            "updatedAt": "2026-11-06T17:00:00Z",
            "invoice_id": "I1",
        },
    )
    fetched = adapter.get_job("job-1")
    assert fetched["createdAt"] == "2026-11-06T17:00:00+00:00"
    assert "invoice_id" not in fetched
    assert job["state"] in ("queued", "succeeded")

    res = adapter.get_job("job-1")
    assert res["id"] == "job-1"
    assert res["state"] == "succeeded"


def test_missing_token(monkeypatch):
    # ensure missing token raises
    monkeypatch.delenv("AUREX_SERVICE_TOKEN", raising=False)
    adapter = WebsiteAdapter("http://example.local")
    adapter._client = DummyClient()
    with pytest.raises(RuntimeError):
        adapter.create_job({"kind": "regression_scan"})
