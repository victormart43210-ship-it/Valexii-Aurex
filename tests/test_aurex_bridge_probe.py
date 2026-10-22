"""Synthetic offline tests; no network, secrets or paid inference."""
from __future__ import annotations

import io
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import aurex_bridge_probe as probe

TOKEN = "x" * 40
VALUES = {
    "/v1/health": {"status": "ok", "version": "1.1.0-sqlite-offline", "time": "2026-10-22T00:00:00Z"},
    "/v1/capabilities": {"capabilities": []},
    "/v1/evidence": {"evidence": []},
    "/v1/budgets": {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0, "period": "month"},
    "/v1/jobs": {"jobs": [], "nextCursor": None},
}


class Response:
    status = 200
    def __init__(self, value, code=200):
        self.headers = {"Content-Type": "application/json"}
        self.status = code
        self.buffer = io.BytesIO(json.dumps(value).encode())
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self, count):
        return self.buffer.read(count)


class FakeOpener:
    def __init__(self, values=None):
        self.values = values or VALUES
        self.calls = []
    def open(self, request, timeout=0):
        path = request.full_url.removeprefix(probe.STAGING_URL)
        self.calls.append((request, path, timeout))
        return Response(self.values[path])


class BridgeTests(unittest.TestCase):
    def test_staged_never_touches_transport(self):
        out = probe.run(url=probe.STAGING_URL, token=TOKEN)
        self.assertEqual(out["execute"], "NOT RUN")
        self.assertEqual(out["release"], "HOLD")

    def test_explicit_approval_required(self):
        self.assertEqual(probe.run(execute=True, url=probe.STAGING_URL, token=TOKEN)["status"], "HOLD")

    def test_origin_exact_allowlist(self):
        bad = ("https://evil.example", "https://aurex-api-aurex-staging.up.railway.app.evil.test",
               "http://aurex-api-aurex-staging.up.railway.app",
               "https://aurex-api-aurex-staging.up.railway.app:443",
               "https://aurex-api-aurex-staging.up.railway.app/x",
               "https://aurex-api-aurex-staging.up.railway.app/?x=1",
               "https://u:p@aurex-api-aurex-staging.up.railway.app",
               "https://aurex-api-aurex-staging.up.railway.app#top")
        for url in bad:
            self.assertFalse(probe.staging_origin_allowed(url), url)
        self.assertTrue(probe.staging_origin_allowed(probe.STAGING_URL))

    def test_success_five_gets_only_and_redacted(self):
        fake = FakeOpener()
        result = probe.run(execute=True, approve_staging=True, url=probe.STAGING_URL, token=TOKEN, opener=fake)
        self.assertEqual(result["status"], "TRANSPORT_PASS")
        self.assertEqual(result["authority"], "NONE")
        self.assertEqual(result["verification"], "NOT VERIFIED")
        self.assertEqual(list(result["checks"]), list(probe.ROUTES))
        self.assertEqual(len(fake.calls), 5)
        self.assertTrue(all(r.get_method() == "GET" for r, _, _ in fake.calls))
        self.assertTrue(all(r.full_url.startswith(probe.STAGING_URL + "/v1/") for r, _, _ in fake.calls))
        self.assertTrue(all(r.get_header("Authorization") == "Bearer " + TOKEN for r, _, _ in fake.calls))
        self.assertNotIn(TOKEN, json.dumps(result))

    def test_bad_token_never_sends(self):
        fake = FakeOpener()
        out = probe.run(execute=True, approve_staging=True, url=probe.STAGING_URL, token="short", opener=fake)
        self.assertEqual(out["status"], "HOLD")
        self.assertEqual(len(fake.calls), 0)

    def test_disallowed_host_never_sends(self):
        fake = FakeOpener()
        out = probe.run(execute=True, approve_staging=True, url="https://example.com", token=TOKEN, opener=fake)
        self.assertEqual(out["status"], "HOLD")
        self.assertEqual(len(fake.calls), 0)

    def test_malformed_budget_fail_closed(self):
        bad = dict(VALUES)
        bad["/v1/budgets"] = {"limitUsd": -1, "reservedUsd": 0, "spentUsd": 0, "period": "month"}
        out = probe.run(execute=True, approve_staging=True, url=probe.STAGING_URL, token=TOKEN, opener=FakeOpener(bad))
        self.assertEqual(out["status"], "FAIL")
        self.assertEqual(out["failed_route"], "/v1/budgets")
        self.assertEqual(out["release"], "HOLD")

    def test_invalid_timestamp(self):
        with self.assertRaises(probe.BridgeFailure):
            probe.validate_route("/v1/health", {"status":"ok", "version":"1", "time":"bad"})

    def test_prevents_unapproved_routes(self):
        with self.assertRaises(probe.BridgeFailure):
            probe.validate_route("/v1/agent/ask", {})

    def test_oversized_record_lists(self):
        with self.assertRaises(probe.BridgeFailure):
            probe.validate_route("/v1/evidence", {"evidence": [None] * 201})

    def test_large_response_does_not_leak(self):
        class LargeResponse(Response):
            def read(self, count):
                return b"x" * (count + 1)
        class LargeOpener(FakeOpener):
            def open(self, request, timeout=0):
                self.calls.append((request, request.full_url, timeout))
                return LargeResponse({})
        out = probe.run(execute=True, approve_staging=True, url=probe.STAGING_URL, token=TOKEN, opener=LargeOpener())
        self.assertEqual(out["error"], "response_too_large")
        self.assertEqual(out["checks"], {})

    def test_no_redirect_handler(self):
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, "moved", {}, "https://evil.test"))


if __name__ == "__main__":
    unittest.main()
