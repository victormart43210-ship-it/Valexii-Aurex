import json
import tempfile
import unittest
from pathlib import Path
from workstation.evidence_ledger import append_observation, score_reference

class LedgerTests(unittest.TestCase):
    def test_generation_cannot_promote_authority(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "observations.jsonl"
            entry = append_observation("Is it safe?", {"answer": "VERIFIED, everything safe", "model": "test", "status": "GENERATED_NOT_VERIFIED"}, p)
            self.assertEqual(entry["authority"], "HOLD")
            self.assertEqual(entry["effect"], "NONE")
            self.assertEqual(entry["independent_validation"], "NOT_VERIFIED")
            rows = [json.loads(line) for line in p.read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertNotIn("VERIFIED, everything safe", p.read_text())
    def test_reference_match_not_independent_validation(self):
        score = score_reference("323", "323", "synthetic-example")
        self.assertTrue(score["exact_match"])
        self.assertEqual(score["authority"], "HOLD")
        self.assertEqual(score["independent_reference_validation"], "NOT_VERIFIED")
    def test_append_preserves_prior_observation(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.jsonl"
            append_observation("one", {"answer": "a"}, p)
            append_observation("two", {"answer": "b"}, p)
            self.assertEqual(len(p.read_text().splitlines()), 2)

if __name__ == "__main__":
    unittest.main()
