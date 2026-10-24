"""Bounded offline tests; never contact the internet or AUREX production."""
from __future__ import annotations

import io
import json

import pytest

from workstation.wiring_preflight import ENDPOINTS, check_service, check_url, main

TOKEN = "s" * 40
URL = "https://aurex-api-production-c535.up.railway.app"
STAMP = "2026-10-21T12:00:00+00:00"


def fixtures():
    return {
        "health": {"status": "ok", "version": "0.1.0a1", "time": STAMP},
        "capabilities": {"capabilities": [{
            "id": "regression_scan", "available": False, "evidenceId": None,
            "verifiedAt": None
        }]},
        "evidence": {"evidence": [{
            "id": "ev-example", "capabilityId": "regression_scan",
            "kind": "offline_probe", "collectedAt": STAMP,
            "sha256": "a" * 64, "summary": "synthetic NOT VERIFIED"
        }]},
        "budgets": {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": "month"},
        "jobs": {"jobs": [{
            "id": "job-example", "kind": "regression_scan", "state": "succeeded",
            "createdAt": STAMP, "updatedAt": STAMP, "reservationUsd": 0
        }], "nextCursor": None},
    }


class Reply:
    status = 200

    def __init__(self, body: bytes):
        self.file = io.BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.file.close()

    def read(self, limit):
        return self.file.read(limit)


class FakeOpener:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def open(self, request, timeout):
        assert timeout == 5
        assert request.get_method() == "GET"
        assert request.full_url.startswith(URL + "/v1/")
        assert "s" * 20 not in request.full_url
        endpoint = request.full_url.rsplit("/", 1)[-1]
        assert endpoint in ENDPOINTS
        assert request.get_header("Accept") == "application/json"
        # The older deployed bridge requires a Bearer token even on /v1/health.
        assert request.get_header("Authorization") == f"Bearer {TOKEN}"
        self.calls.append(endpoint)
        return Reply(self.payloads[endpoint])


def encoded(data):
    return {key: json.dumps(value).encode() for key, value in data.items()}


def test_read_only_wire_contract_is_transport_only():
    fake = FakeOpener(encoded(fixtures()))
    report = check_service(URL, TOKEN, opener=fake)
    assert fake.calls == list(ENDPOINTS)
    assert report["transport"] == "READ_ONLY_SHAPES_ACCEPTED"
    assert report["production_release"] == "HOLD"
    assert report["backend"] == "NOT_INDEPENDENTLY_VERIFIED"
    assert report["model_inference"] == "NOT_RUN"
    assert report["financial_authority"] == "NONE"


@pytest.mark.parametrize("url", [
    "http://aurex-api-production-c535.up.railway.app",
    "https://localhost",
    "https://127.0.0.1",
    "https://169.254.169.254",
    "https://evil.com",
    "https://aurex-api-production-c535.up.railway.app.evil.net",
    "https://user:pass@aurex-api-production-c535.up.railway.app",
    "https://aurex-api-production-c535.up.railway.app:8443",
    "https://aurex-api-production-c535.up.railway.app/other",
    "https://aurex-api-production-c535.up.railway.app?a=1",
    "file:///etc/passwd",
])
def test_nonrailway_or_unsafe_url_refused(url):
    with pytest.raises(ValueError):
        check_url(url)


def test_token_missing_blocks_before_any_network():
    fake = FakeOpener(encoded(fixtures()))
    with pytest.raises(ValueError, match="token"):
        check_service(URL, "short", opener=fake)
    assert fake.calls == []


def test_unknown_capability_or_evidence_kinds_fail_without_promotion():
    data = fixtures()
    data["evidence"]["evidence"][0]["kind"] = "PAYMENT_APPROVED"
    report = check_service(URL, TOKEN, opener=FakeOpener(encoded(data)))
    assert report["checks"]["evidence"] == "HOLD_BAD_SCHEMA"
    assert report["production_release"] == "HOLD"


def test_oversized_response_does_not_leak_data():
    bad = encoded(fixtures())
    bad["evidence"] = b"{" + (b"x" * (256 * 1024 + 1))
    report = check_service(URL, TOKEN, opener=FakeOpener(bad))
    assert report["checks"]["evidence"] == "HOLD_TOO_LARGE"
    assert report["production_release"] == "HOLD"


def test_bad_utf8_fails_closed():
    bad = encoded(fixtures())
    bad["capabilities"] = b"\xff\xfe"
    result = check_service(URL, TOKEN, opener=FakeOpener(bad))
    assert result["checks"]["capabilities"] == "HOLD_INVALID_JSON"


def test_default_cli_does_not_touch_network(monkeypatch, capsys):
    monkeypatch.setenv("AUREX_SERVICE_URL", URL)
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", TOKEN)
    assert main([]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "NOT_RUN"
    assert response["production_release"] == "HOLD"


def test_cli_without_configuration_fails_closed(monkeypatch, capsys):
    monkeypatch.delenv("AUREX_SERVICE_TOKEN", raising=False)
    monkeypatch.setenv("AUREX_SERVICE_URL", URL)
    assert main(["--execute"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "HOLD_INVALID_CONFIGURATION"


def test_duplicate_wire_json_keys_are_hold():
    bad = encoded(fixtures())
    bad["health"] = b'{"status":"ok","status":"ok","version":"0.1","time":"today"}'
    report = check_service(URL, TOKEN, opener=FakeOpener(bad))
    assert report["checks"]["health"] == "HOLD_INVALID_JSON"
    assert report["production_release"] == "HOLD"


def test_non_string_evidence_kind_returns_hold_not_traceback():
    data = fixtures()
    data["evidence"]["evidence"][0]["kind"] = ["offline_probe"]
    report = check_service(URL, TOKEN, opener=FakeOpener(encoded(data)))
    assert report["checks"]["evidence"] == "HOLD_BAD_SCHEMA"
    assert report["production_release"] == "HOLD"
