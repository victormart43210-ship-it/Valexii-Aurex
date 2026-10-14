import importlib.util
import os
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bridge', ROOT / 'backend' / 'app.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class ContractTests(unittest.TestCase):
    def test_token_rejects_unconfigured(self):
        with patch.dict(os.environ, {'AUREX_SERVICE_TOKEN': ''}):
            with self.assertRaises(Exception) as e:
                bridge.authorize('Bearer test')
            self.assertEqual(e.exception.status_code, 503)
    def test_token_rejects_wrong(self):
        with patch.dict(os.environ, {'AUREX_SERVICE_TOKEN': 'a' * 32}):
            with self.assertRaises(Exception) as e:
                bridge.authorize('Bearer ' + 'b' * 32)
            self.assertEqual(e.exception.status_code, 401)
    def test_token_accepts_correct(self):
        with patch.dict(os.environ, {'AUREX_SERVICE_TOKEN': 'a' * 32}):
            self.assertIsNone(bridge.authorize('Bearer ' + 'a' * 32))
    def test_capabilities_fail_closed(self):
        self.assertTrue(all(not c['available'] and c['evidenceId'] is None for c in bridge.capabilities()['capabilities']))
    def test_budget_zero(self):
        self.assertEqual(bridge.budgets()['limitUsd'], 0)
    def test_evidence_empty(self):
        self.assertEqual(bridge.evidence()['evidence'], [])
    def test_health_shape(self):
        self.assertEqual(set(bridge.health()), {'status', 'version', 'time'})
    def test_jobs_disabled(self):
        self.assertEqual(bridge.jobs(), {'jobs': [], 'nextCursor': None})
if __name__ == '__main__': unittest.main()
