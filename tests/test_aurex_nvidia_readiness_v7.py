"""Offline validation of the zero-cost NVIDIA bridge preflight."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import tempfile

S = Path(__file__).resolve().parents[1] / "tools" / "aurex_nvidia_readiness_v7.py"
spec = importlib.util.spec_from_file_location("nvidia_v7", S)
assert spec and spec.loader
v7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)


class TestNvidiaBridge(TestCase):
    def agent(self):
        return {"authority": "NONE", "verification": "NOT_VERIFIED", "modelProvider": "OPENAI", "chatConfigured": False}

    def budget(self):
        return {"limitUsd": 0, "reservedUsd": 0, "spentUsd": 0}

    def test_zero_budget_and_anonymous_401(self):
        r = v7.evaluate(401, self.agent(), self.budget())
        self.assertEqual(r["status"], "PASS")
        self.assertFalse(r["modelWasCalled"])
        self.assertEqual(r["providerConnection"], "NOT_VERIFIED")

    def test_anon_200_fails(self):
        with self.assertRaises(v7.Hold):
            v7.evaluate(200, self.agent(), self.budget())

    def test_anon_503_fails(self):
        with self.assertRaises(v7.Hold):
            v7.evaluate(503, self.agent(), self.budget())

    def test_false_authority_fails(self):
        a = self.agent()
        a["authority"] = "PASS"
        with self.assertRaises(v7.Hold):
            v7.evaluate(401, a, self.budget())

    def test_missing_verification_fails(self):
        a = self.agent()
        a.pop("verification")
        with self.assertRaises(v7.Hold):
            v7.evaluate(401, a, self.budget())

    def test_nonzero_budget_fails(self):
        b = self.budget()
        b["spentUsd"] = 0.01
        with self.assertRaises(v7.Hold):
            v7.evaluate(401, self.agent(), b)

    def test_nonzero_reservation_fails(self):
        b = self.budget()
        b["reservedUsd"] = 1
        with self.assertRaises(v7.Hold):
            v7.evaluate(401, self.agent(), b)

    def test_nonzero_limit_fails(self):
        b = self.budget()
        b["limitUsd"] = 10
        with self.assertRaises(v7.Hold):
            v7.evaluate(401, self.agent(), b)

    def test_no_token_prevents_network(self):
        with patch.dict("os.environ", {"RAILWAY_ENVIRONMENT_NAME": "aurex-staging", "AUREX_SERVICE_TOKEN": ""}):
            with patch.object(v7, "_fetch", side_effect=AssertionError("network must not be used")):
                self.assertEqual(v7.main(["staging"]), 2)

    def test_wrong_env_prevents_network(self):
        with patch.dict("os.environ", {"RAILWAY_ENVIRONMENT_NAME": "production", "AUREX_SERVICE_TOKEN": "s" * 40}):
            with patch.object(v7, "_fetch", side_effect=AssertionError("network must not be used")):
                self.assertEqual(v7.main(["staging"]), 2)

    def test_only_allowlisted_paths(self):
        with self.assertRaises(v7.Hold):
            v7._fetch("/v1/agent/ask", "s" * 40)

    def test_offline_source_guard_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(v7.Hold):
                v7.local(Path(d))

    def test_https_staging_origin_is_pinned(self):
        self.assertEqual(v7.BASE, "https://aurex-api-aurex-staging.up.railway.app")
