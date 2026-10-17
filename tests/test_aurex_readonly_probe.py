"""Synthetic-only RED/GREEN tests for the operator Railway proof script."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "z" * 32
NOW = "2026-10-17T18:00:00+00:00"
DATA = {
    "/v1/health": {"status": "ok", "version": "1.0.0-readonly", "time": NOW},
    "/v1/capabilities": {
        "capabilities": [{"id": "memory-graph", "available": False,
                          "evidenceId": None, "verifiedAt": None}]
    },
    "/v1/evidence": {"evidence": []},
    "/v1/budgets": {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": "month"},
    "/v1/jobs": {"jobs": [], "nextCursor": None},
}


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


op = load("aurex_probe_tests", "scripts/aurex_readonly_probe.py")


def request(path, token):
    assert token == TOKEN
    return 200, "application/json", json.dumps(DATA[path]).encode()


def test_offline_five_get_positive_does_not_admit_production():
    report = op.probe(TOKEN, request)
    assert report["directRailwayVerified"] is True
    assert report["cloudflareOriginVerified"] is False
    assert report["websiteRenderingVerified"] is False
    assert report["productionAuthority"] == "HOLD"
    assert len(report["checks"]) == 5
    assert TOKEN not in json.dumps(report)


def test_short_bearer_fails_before_network():
    calls = []
    def forbidden(path, token):
        calls.append(path)
        raise AssertionError("unexpected outbound GET")
    for size in [0, 16, 24, 31]:
        assert op.probe("z" * size, forbidden)["directRailwayVerified"] is False
    assert calls == []


@pytest.mark.parametrize("path", list(DATA))
def test_extra_keys_fail_closed(path):
    altered = {k: (dict(v, injected="untrusted") if k == path else v)
               for k, v in DATA.items()}
    def injected(name, token):
        return 200, "application/json", json.dumps(altered[name]).encode()
    result = op.probe(TOKEN, injected)
    assert result["directRailwayVerified"] is False
    assert any(c["path"] == path and c["status"] == "FAIL" for c in result["checks"])


@pytest.mark.parametrize("path", list(DATA))
def test_http_401_fails_closed(path):
    def rejected(name, token):
        if name == path:
            return 401, "application/json", b'{"detail":"no"}'
        return request(name, token)
    result = op.probe(TOKEN, rejected)
    assert result["directRailwayVerified"] is False
    assert any(c["path"] == path and c["httpStatus"] == 401 for c in result["checks"])


def test_non_json_and_oversize_fail_closed():
    def bad_type(path, token):
        return 200, "text/html", b"<html>ok</html>"
    assert not op.probe(TOKEN, bad_type)["directRailwayVerified"]
    def overflow(path, token):
        return 200, "application/json", b"x" * (op.LIMIT + 1)
    assert not op.probe(TOKEN, overflow)["directRailwayVerified"]


def test_no_financial_or_job_authority_from_payloads():
    changed = dict(DATA)
    changed["/v1/budgets"] = {"limitUsd": 100, "reservedUsd": 0,
                             "spentUsd": 0, "period": "month"}
    def nonzero(path, token):
        return 200, "application/json", json.dumps(changed[path]).encode()
    assert not op.probe(TOKEN, nonzero)["directRailwayVerified"]
    changed["/v1/budgets"] = DATA["/v1/budgets"]
    changed["/v1/capabilities"] = {
        "capabilities": [{"id": "memory-graph", "available": True,
                          "evidenceId": None, "verifiedAt": None}]
    }
    assert not op.probe(TOKEN, nonzero)["directRailwayVerified"]


def test_actual_main_readonly_fastapi_contract(monkeypatch):
    bridge = load("aurex_bridge_probe_tests", "integrations/kusanagi-xvi/backend/app.py")
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    with TestClient(bridge.app) as client:
        def real_source(path, token):
            response = client.get(path, headers={"Authorization": "Bearer " + token})
            return response.status_code, response.headers.get("content-type", ""), response.content
        report = op.probe(TOKEN, real_source)
        assert report["directRailwayVerified"] is True
        assert report["productionAuthority"] == "HOLD"
        assert client.post("/v1/jobs", headers={"Authorization": "Bearer " + TOKEN}).status_code in (404, 405)
        assert op.probe("a" * 32, real_source)["directRailwayVerified"] is False
