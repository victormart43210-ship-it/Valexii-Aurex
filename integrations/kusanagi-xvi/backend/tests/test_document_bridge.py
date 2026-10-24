"""Offline contract and fail-closed tests; no NVIDIA calls are made."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request as URLRequest

from fastapi.testclient import TestClient

# Works from this distributable and from the patched repository's backend/tests folder.
BACKEND = Path(__file__).resolve().parents[1]
if not (BACKEND / "app.py").exists():
    BACKEND = BACKEND / "backend"
sys.path.insert(0, str(BACKEND))
import app  # noqa: E402
import doc_intelligence as doc  # noqa: E402

TOKEN = "owner-only-test-token-never-use-in-production-0123456789"
HEAD = {"Authorization": "Bearer " + TOKEN}
CLIENT = TestClient(app.app)


class OfflineBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = {
            "AUREX_SERVICE_TOKEN": TOKEN,
            "AUREX_NVIDIA_API_KEY": "test-secret-not-real-xxxxxxxxxxxxxxxxxxx",
            "AUREX_NVIDIA_DOCS_ENABLED": "1",
            "AUREX_DOCUMENT_MAX_CALLS_PER_DAY": "3",
            "AUREX_DOCUMENT_DAILY_BUDGET_USD": "0.03",
            "AUREX_DOCUMENT_ESTIMATE_USD_PER_CALL": "0.01",
            "AUREX_BUDGET_USD": "0.03",
            "AUREX_DOCUMENT_SQLITE_PATH": str(Path(self.temp.name) / "quota.sqlite"),
            "AUREX_DOCUMENT_TEST_MODE": "1",
        }
        self.env = patch.dict(os.environ, self.config)
        self.env.start()
        self.addCleanup(self.env.stop)

    def _analyze(self, text="Sample source text for analysis.", headers=None, **kwargs):
        return CLIENT.post(
            "/v1/documents/analyze",
            headers={**HEAD, "X-Aurex-Cloud-Consent": "approved", **(headers or {})},
            json={"text": text, **kwargs},
        )

    def test_legacy_contracts(self):
        for path in ["/v1/health", "/v1/capabilities", "/v1/evidence", "/v1/budgets", "/v1/jobs"]:
            r = CLIENT.get(path, headers=HEAD)
            self.assertEqual(r.status_code, 200, path)
        self.assertEqual(CLIENT.get("/v1/capabilities", headers=HEAD).json()["capabilities"][0]["available"], False)
        self.assertEqual(CLIENT.get("/v1/jobs", headers=HEAD).json()["jobs"], [])

    def test_no_public_diagnostics(self):
        for path in ["/v1/documents/status", "/v1/health", "/v1/budgets"]:
            self.assertEqual(CLIENT.get(path).status_code, 401)
        self.assertEqual(CLIENT.post("/v1/documents/analyze", json={"text": "x"}).status_code, 401)

    def test_disabled_by_default_and_zero_budget(self):
        os.environ.pop("AUREX_NVIDIA_DOCS_ENABLED")
        r = CLIENT.get("/v1/documents/status", headers=HEAD)
        self.assertEqual(r.json()["status"], "DISABLED")
        self.assertEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["limitUsd"], 0)
        self.assertEqual(self._analyze().status_code, 503)

    def test_no_consent(self):
        r = self._analyze(headers={"X-Aurex-Cloud-Consent": "no"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0)

    def test_invalid_request_rejected_without_spend(self):
        for text in ["", "a" * 7001]:
            self.assertEqual(self._analyze(text=text).status_code, 422)
        self.assertEqual(self._analyze(text="yes", extra="bad").status_code, 422)
        self.assertEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0)

    def test_provider_stays_not_verified(self):
        expected = "Sample source text"
        value = {"summary": "A sample source is present", "key_facts": ["sample"], "uncertainties": [], "evidence_quotes": [expected]}
        with patch.object(doc, "_provider_request", return_value=(json.dumps(value), 30, 20)) as mocked:
            r = self._analyze()
            self.assertEqual(mocked.call_count, 1)
        self.assertEqual(r.status_code, 200, r.text)
        out = r.json()
        self.assertEqual(out["status"], "CANDIDATE_COMPLETE")
        self.assertEqual(out["results"][0]["quote_checks"][0]["status"], "EXACT_MATCH")
        self.assertEqual(out["verification_status"], "NOT_VERIFIED")
        self.assertEqual(out["release"], "HOLD")
        self.assertEqual(out["authority"], "NONE")
        self.assertNotIn("Sample source text", json.dumps(out))
        self.assertEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0.01)

    def test_forged_quote_rejected_and_charged(self):
        value = {"summary": "bad", "key_facts": [], "uncertainties": [], "evidence_quotes": ["not present in sample"]}
        with patch.object(doc, "_provider_request", return_value=(json.dumps(value), 2, 3)):
            r = self._analyze()
        self.assertEqual(r.status_code, 502)
        self.assertNotIn("bad", r.text)
        self.assertEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0.01)

    def test_no_provider_exception_leak(self):
        with patch.object(doc, "_provider_request", side_effect=RuntimeError("secret xyz")):
            r = self._analyze()
        self.assertEqual(r.status_code, 502)
        self.assertNotIn("secret xyz", r.text)

    def test_budget_preflight_atomic(self):
        value = {"summary": "ok", "key_facts": [], "uncertainties": [], "evidence_quotes": ["Sample source text"]}
        with patch.object(doc, "_provider_request", return_value=(json.dumps(value), 2, 3)):
            for _ in range(3):
                self.assertEqual(self._analyze().status_code, 200)
            denied = self._analyze()
        self.assertEqual(denied.status_code, 402)
        self.assertAlmostEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0.03)

    def test_double_segment_consumes_two_calls(self):
        value = {"summary": "ok", "key_facts": [], "uncertainties": [], "evidence_quotes": ["word"]}
        with patch.object(doc, "_provider_request", return_value=(json.dumps(value), 2, 3)):
            r = self._analyze(text=("word " * 800).strip())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["segments_processed"], 2)
        self.assertAlmostEqual(CLIENT.get("/v1/budgets", headers=HEAD).json()["spentUsd"], 0.02)

    def test_invalid_quota_holds(self):
        os.environ["AUREX_DOCUMENT_MAX_CALLS_PER_DAY"] = "-1"
        self.assertEqual(CLIENT.get("/v1/documents/status", headers=HEAD).json()["status"], "DISABLED")
        self.assertEqual(self._analyze().status_code, 503)

    def test_quote_matching_separates_exact_normalized(self):
        p = "This is `an`\nexample."
        self.assertEqual(doc._quote_result(p, "This is `an`\nexample."), "EXACT_MATCH")
        self.assertEqual(doc._quote_result(p, "This is an example."), "NORMALIZED_MATCH")
        self.assertEqual(doc._quote_result(p, "not there"), "NOT_FOUND")

    def test_nvidia_request_uses_http_request_not_fastapi_request(self):
        response = {"choices": [{"message": {"content": "candidate"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 1}}
        with patch.object(doc, "build_opener") as factory:
            factory.return_value.open.return_value.__enter__.return_value.read.return_value = json.dumps(response).encode()
            output, input_tokens, output_tokens = doc._provider_request("test-only document")
            sent = factory.return_value.open.call_args.args[0]
        self.assertIsInstance(sent, URLRequest)
        self.assertEqual(sent.full_url, doc.NVIDIA_URL)
        self.assertEqual(sent.get_method(), "POST")
        self.assertEqual(output, "candidate")
        self.assertEqual((input_tokens, output_tokens), (3, 1))

    def test_auth_constant_time_header_value(self):
        self.assertEqual(CLIENT.get("/v1/health", headers={"Authorization": "Bearer bad"}).status_code, 401)

    def test_no_secrets_in_model_settings(self):
        self.assertNotIn("authorization", json.dumps(doc.WIRE_PROFILE).lower())
        self.assertNotIn("api_key", json.dumps(doc.WIRE_PROFILE).lower())
        self.assertEqual(doc.WIRE_PROFILE["seed"], "NOT_SENT")


if __name__ == "__main__":
    unittest.main()
