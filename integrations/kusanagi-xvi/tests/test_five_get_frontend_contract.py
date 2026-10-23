"""Contract replay for the *older* deployed read-only Railway bridge source.

No outbound network access, no real bearer token, no Qwen, no customer records,
no cloud deployment. This does NOT prove real Cloudflare→Railway connectivity.
"""

import importlib.util
import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

BRIDGE = Path(__file__).resolve().parents[1] / "backend" / "app.py"
SPEC = importlib.util.spec_from_file_location("aurex_readonly_bridge_test", BRIDGE)
assert SPEC is not None and SPEC.loader is not None
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)

AUTH = "Bearer " + "t" * 32
PATHS = (
    "/v1/health",
    "/v1/capabilities",
    "/v1/jobs",
    "/v1/evidence",
    "/v1/budgets",
)


def _client() -> TestClient:
    return TestClient(bridge.app)


def test_all_five_gets_match_strict_frontend_v1_shapes() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": "t" * 32}):
        client = _client()
        values = {}
        for path in PATHS:
            response = client.get(path, headers={"Authorization": AUTH})
            assert response.status_code == 200, (path, response.status_code)
            values[path] = response.json()
        assert set(values["/v1/health"]) == {"status", "version", "time"}
        assert values["/v1/health"]["status"] == "ok"
        assert set(values["/v1/capabilities"]) == {"capabilities"}
        for cap in values["/v1/capabilities"]["capabilities"]:
            assert set(cap) == {"id", "available", "evidenceId", "verifiedAt"}
            assert cap == {**cap, "available": False, "evidenceId": None, "verifiedAt": None}
        assert values["/v1/jobs"] == {"jobs": [], "nextCursor": None}
        assert values["/v1/evidence"] == {"evidence": []}
        assert values["/v1/budgets"] == {
            "limitUsd": 0,
            "reservedUsd": 0,
            "spentUsd": 0,
            "period": "month",
        }


def test_missing_or_wrong_auth_cannot_read_bridge_data() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": "t" * 32}):
        client = _client()
        for path in PATHS:
            assert client.get(path).status_code == 401
            assert client.get(path, headers={"Authorization": "Bearer " + "f" * 32}).status_code == 401


def test_unconfigured_bridge_fails_closed() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": ""}):
        assert _client().get(PATHS[0], headers={"Authorization": AUTH}).status_code == 503


def test_readonly_bridge_does_not_admit_write_jobs() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": "t" * 32}):
        client = _client()
        for path in ("/v1/jobs", "/v1/jobs/demo/cancel", "/v1/evidence", "/v1/budgets"):
            response = client.post(path, headers={"Authorization": AUTH}, json={})
            assert response.status_code in (404, 405), (path, response.status_code)


def test_source_does_not_fake_model_readiness() -> None:
    with patch.dict(os.environ, {"AUREX_SERVICE_TOKEN": "t" * 32}):
        client = _client()
        assert client.get("/v1/evidence", headers={"Authorization": AUTH}).json()["evidence"] == []
        assert not any(
            cap["available"]
            for cap in client.get("/v1/capabilities", headers={"Authorization": AUTH}).json()["capabilities"]
        )
