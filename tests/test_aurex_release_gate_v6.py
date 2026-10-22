"""Zero-network, no-token AUREX XXV release gate regression tests."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parents[1] / "tools" / "aurex_release_gate.py"
spec = importlib.util.spec_from_file_location("aurex_release_gate_v6", HERE)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

class GateTests(unittest.TestCase):
    def test_staging_host_locked(self):
        self.assertEqual(gate.STAGING, "https://aurex-api-aurex-staging.up.railway.app")
    def test_website_host_locked(self):
        self.assertEqual(gate.WEBSITE, "https://valexii.com/aurex/ox")
    def test_llm_never_auto_activated(self):
        self.assertNotIn("/v1/agent/ask", gate.GET_PATHS)
    def test_missing_token_stays_hold(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(gate.stage_readonly()["status"], "HOLD")
    def test_short_token_stays_hold(self):
        with mock.patch.dict("os.environ", {"AUREX_SERVICE_TOKEN": "x" * 3}, clear=True):
            self.assertEqual(gate.stage_readonly()["status"], "HOLD")
    def test_unauth_denial_first(self):
        with (
            mock.patch.dict("os.environ", {"AUREX_SERVICE_TOKEN": "A" * 64}, clear=True),
            mock.patch.object(gate, "_open", return_value=(200, b"{}")) as req,
        ):
            got = gate.stage_readonly()
            self.assertEqual(got["status"], "FAIL")
            self.assertEqual(req.call_count, 1)
    def test_all_valid_statuses_no_nvidia(self):
        def response(url, token=None):
            if token is None:
                return 401, b""
            if url.endswith("/v1/health"):
                return 200, b'{"status":"ok"}'
            if url.endswith("/v1/budgets"):
                return 200, b'{"limitUsd":0,"spentUsd":0}'
            if url.endswith("/v1/agent/status"):
                return 200, b'{"chatConfigured":false}'
            return 200, b"{}"
        with (
            mock.patch.dict("os.environ", {"AUREX_SERVICE_TOKEN": "A" * 64}, clear=True),
            mock.patch.object(gate, "_open", side_effect=response) as req,
        ):
            x = gate.stage_readonly()
            self.assertEqual(x["status"], "PASS")
            self.assertEqual(req.call_count, 1 + len(gate.GET_PATHS))
            self.assertEqual(x["modelInference"], "NOT_RUN")
    def test_llm_enabled_fails(self):
        def response(url, token=None):
            if token is None:
                return 401, b""
            if url.endswith("/v1/agent/status"):
                return 200, b'{"chatConfigured":true}'
            if url.endswith("/v1/health"):
                return 200, b'{"status":"ok"}'
            if url.endswith("/v1/budgets"):
                return 200, b'{"limitUsd":0,"spentUsd":0}'
            return 200, b"{}"
        with (
            mock.patch.dict("os.environ", {"AUREX_SERVICE_TOKEN":"A"*64}, clear=True),
            mock.patch.object(gate,"_open",side_effect=response),
        ):
            self.assertEqual(gate.stage_readonly()["status"],"FAIL")
    def test_nonzero_cost_fails(self):
        def response(url, token=None):
            if token is None:
                return 401, b""
            if url.endswith("/v1/health"):
                return 200, b'{"status":"ok"}'
            if url.endswith("/v1/budgets"):
                return 200, b'{"limitUsd":1,"spentUsd":0}'
            return 200,b"{}"
        with (
            mock.patch.dict("os.environ", {"AUREX_SERVICE_TOKEN":"A"*64}, clear=True),
            mock.patch.object(gate,"_open",side_effect=response),
        ):
            self.assertEqual(gate.stage_readonly()["status"],"FAIL")
    def test_website_200_marker_not_browser_proof(self):
        with mock.patch.object(gate,"_open",return_value=(200,b"<html>AUREX</html>")):
            x=gate.website_readonly()
            self.assertEqual(x["status"],"PASS")
            self.assertEqual(x["coreWebVitals"],"NOT_MEASURED")
    def test_website_without_marker_fails(self):
        with mock.patch.object(gate,"_open",return_value=(200,b"<html/>")):
            self.assertEqual(gate.website_readonly()["status"],"FAIL")
    def test_redirect_refused(self):
        self.assertIsNone(gate._NoRedirect().redirect_request(None,None,302,"Moved",{},"https://invalid.example"))
    def test_no_repo(self):
        with tempfile.TemporaryDirectory() as p:
            self.assertEqual(gate.repo_readonly(Path(p))["status"],"FAIL")
    def test_emit_cannot_upgrade_authority(self):
        with mock.patch("builtins.print") as output:
            self.assertEqual(gate.emit({"status":"HOLD", "authority":"PASS", "release":"CLEAR"}),2)
            obj = json.loads(output.call_args.args[0])
            self.assertEqual(obj["release"],"HOLD")
            self.assertEqual(obj["authority"],"NONE")

if __name__ == "__main__":
    unittest.main()
