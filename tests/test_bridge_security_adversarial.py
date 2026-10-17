"""Adversarial offline tests for the independent read-only production verifier."""

from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterator
from unittest.mock import patch

import pytest

from scripts.verify_live_bridge import (
    ENDPOINTS,
    MAX_PAYLOAD_BYTES,
    PRODUCTION_BASE,
    run_bridge_verification,
    validate_endpoint_schema,
    verify_live_endpoint,
)

TOKEN = "T" * 32  # synthetic credential, never use a production token in tests
NOW = datetime.now(UTC).isoformat()
VALID: dict[str, dict[str, Any]] = {
    "/v1/health": {"status": "ok", "version": "1.0.0-readonly", "time": NOW},
    "/v1/capabilities": {"capabilities": [
        {"id": "memory-graph", "available": False, "evidenceId": None, "verifiedAt": None}
    ]},
    "/v1/evidence": {"evidence": []},
    "/v1/budgets": {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": "month"},
    "/v1/jobs": {"jobs": [], "nextCursor": None},
}


@pytest.mark.parametrize("path", ENDPOINTS)
def test_empty_and_missing_fields_rejected(path: str) -> None:
    assert not validate_endpoint_schema(path, {})


@pytest.mark.parametrize("path", ENDPOINTS)
def test_real_deployed_response_shapes_accepted(path: str) -> None:
    assert validate_endpoint_schema(path, VALID[path])


@pytest.mark.parametrize("path,invalid", [
    ("/v1/health", {"status": "compromised"}),
    ("/v1/health", {"status": "ok", "version": "v", "time": "yesterday"}),
    ("/v1/health", {**VALID["/v1/health"], "unexpected": 1}),
    ("/v1/capabilities", {"capabilities": [{"id": 123, "available": "yes"}]}),
    ("/v1/capabilities", {"capabilities": [{"id": "good", "available": "yes", "evidenceId": None, "verifiedAt": None}]}),
    ("/v1/capabilities", {"capabilities": [{"id": "good", "available": False, "evidenceId": [], "verifiedAt": None}]}),
    ("/v1/evidence", {"evidence": [{"id": "e1", "sha256": "broken"}]}),
    ("/v1/evidence", {"evidence": [{"id": "e1", "capabilityId": "good", "kind": [], "collectedAt": NOW, "sha256": "0" * 64, "summary": ""}]}),
    ("/v1/budgets", {"limitUsd": -99}),
    ("/v1/budgets", {"limitUsd": False, "reservedUsd": 0, "spentUsd": 0, "period": "month"}),
    ("/v1/budgets", {"limitUsd": float("inf"), "reservedUsd": 0, "spentUsd": 0, "period": "month"}),
    ("/v1/jobs", {"jobs": [{"id": "job", "state": "I_BYPASS"}]}),
    ("/v1/jobs", {"jobs": [{"id": "job", "kind": [], "state": [], "createdAt": NOW, "updatedAt": NOW, "reservationUsd": 0}], "nextCursor": None}),
    ("/v1/jobs", {"jobs": [], "nextCursor": 99}),
])
def test_strict_contract_rejection(path: str, invalid: dict[str, Any]) -> None:
    assert validate_endpoint_schema(path, invalid) is False


class MockResponse:
    def __init__(self, raw: bytes, status: int = 200):
        self.raw = raw
        self.status = status

    def __enter__(self) -> "MockResponse":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def read(self, size: int) -> bytes:
        return self.raw[:size]


class MockOpener:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.requests = []

    def open(self, req: Any, timeout: float) -> MockResponse:
        self.requests.append(req)
        return MockResponse(self.raw)


def test_missing_token_never_opens_network() -> None:
    with patch("urllib.request.build_opener", side_effect=AssertionError("Should never call")):
        for endpoint in ENDPOINTS:
            result = verify_live_endpoint(PRODUCTION_BASE, endpoint, token=None)
            assert result["status"] == "HOLD"


def test_malformed_http200_with_authenticated_token_is_hold() -> None:
    opener = MockOpener(b"{}")
    with patch("urllib.request.build_opener", return_value=opener):
        result = verify_live_endpoint(PRODUCTION_BASE, "/v1/health", TOKEN)
    assert result["status"] == "HOLD"
    assert result["reason"] == "FAIL — SCHEMA INVALID"


def test_invalid_json_duplicate_keys_and_nonfinite_are_hold() -> None:
    for raw in (b'{"status":"ok","status":"ok"}', b'{"limitUsd":NaN}', b"broken-json"):
        opener = MockOpener(raw)
        with patch("urllib.request.build_opener", return_value=opener):
            result = verify_live_endpoint(PRODUCTION_BASE, "/v1/health", TOKEN)
        assert result["status"] == "HOLD"


def test_payload_larger_than_cap_is_hold_and_capped_read() -> None:
    opener = MockOpener(b"{" + (b" " * MAX_PAYLOAD_BYTES) + b"}")
    with patch("urllib.request.build_opener", return_value=opener):
        result = verify_live_endpoint(PRODUCTION_BASE, "/v1/health", TOKEN)
    assert result["status"] == "HOLD"
    assert result["reason"] == "Response too large"


@pytest.mark.parametrize("base,path", [
    ("http://aurex-api-production-c535.up.railway.app", "/v1/health"),
    ("https://untrusted.example", "/v1/health"),
    ("https://aurex-api-production-c535.up.railway.app:8443", "/v1/health"),
    ("https://user:pass@aurex-api-production-c535.up.railway.app", "/v1/health"),
    ("https://aurex-api-production-c535.up.railway.app?q=bad", "/v1/health"),
    ("https://aurex-api-production-c535.up.railway.app", "http://127.0.0.1:9876/steal"),
    ("https://aurex-api-production-c535.up.railway.app", "//127.0.0.1/steal"),
    ("https://aurex-api-production-c535.up.railway.app", "/health"),
    ("http://127.0.0.1:8080", "/v1/health"),  # not loopback mode
])
def test_destinations_and_paths_fail_before_io(base: str, path: str) -> None:
    with patch("urllib.request.build_opener", side_effect=AssertionError("Should never call")):
        result = verify_live_endpoint(base, path, TOKEN)
    assert result["status"] == "REJECTED"


def test_report_does_not_contain_token_or_raw_responses() -> None:
    result_json = json.dumps(VALID["/v1/health"]).encode()
    with patch("urllib.request.build_opener", return_value=MockOpener(result_json)):
        report = run_bridge_verification(PRODUCTION_BASE, token=TOKEN)
    rendered = json.dumps(report)
    assert TOKEN not in rendered
    assert "1.0.0-readonly" not in rendered
    assert report["status"] == "HOLD"  # other four contracts are not health
    assert report["website_to_backend"] == "NOT VERIFIED"


def test_complete_simulated_response_never_claims_live_or_website_verification() -> None:
    class SimulatedOpener:
        def open(self, req: Any, timeout: float) -> MockResponse:
            path = req.full_url.split(".app", 1)[-1]
            return MockResponse(json.dumps(VALID[path]).encode())

    with patch("urllib.request.build_opener", return_value=SimulatedOpener()):
        report = run_bridge_verification(PRODUCTION_BASE, TOKEN)
    assert report["status"] == "PASS_TRANSPORT_ONLY"
    assert report["website_to_backend"] == "NOT VERIFIED"
    assert report["authority"] == "NONE"


@contextmanager
def redirect_fixture() -> Iterator[tuple[str, list[str]]]:
    received: list[str] = []

    class Receiver(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            received.append(self.headers.get("Authorization", ""))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, _format: str, *_args: Any) -> None:
            return None

    receiver = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
    target = f"http://127.0.0.1:{receiver.server_port}/steal"

    class Redirector(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(302)
            self.send_header("Location", target)
            self.end_headers()

        def log_message(self, _format: str, *_args: Any) -> None:
            return None

    redirector = ThreadingHTTPServer(("127.0.0.1", 0), Redirector)
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (receiver, redirector)]
    for thread in threads:
        thread.start()
    try:
        yield f"http://127.0.0.1:{redirector.server_port}", received
    finally:
        for server in (redirector, receiver):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)


def test_real_http_redirect_is_rejected_and_token_never_forwarded() -> None:
    with redirect_fixture() as (base, captured):
        result = verify_live_endpoint(base, "/v1/health", TOKEN, allow_loopback=True)
    assert result["status"] == "HOLD"
    assert result["http_code"] == 302
    assert captured == []


def test_loopback_mode_is_explicit_and_never_counts_as_production() -> None:
    # Even a local successful response must not become production evidence.
    assert verify_live_endpoint("http://127.0.0.1:8080", "/v1/health", TOKEN)["status"] == "REJECTED"
