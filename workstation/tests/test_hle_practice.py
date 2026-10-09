import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hle_practice import evaluate

class PracticeTests(unittest.TestCase):
    def test_scores_and_does_not_claim_official(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = Path(tmp)/"q.json"
            a = Path(tmp)/"a.json"
            q.write_text(json.dumps([{"id":"x","answer":"42"},{"id":"y","answer":"W"}]))
            a.write_text(json.dumps({"x":"42"}))
            result = evaluate(q,a)
            self.assertEqual(result["exact_matches"],1)
            self.assertEqual(result["answered"],1)
            self.assertEqual(result["questions"],2)
            self.assertFalse(result["official_hle"])
            self.assertEqual(result["independent_reference_validation"],"NOT_VERIFIED")

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = Path(tmp)/"q.json"
            a = Path(tmp)/"a.json"
            q.write_text(json.dumps([{"id":"x","answer":"a"},{"id":"x","answer":"b"}]))
            a.write_text("{}")
            with self.assertRaises(ValueError):
                evaluate(q,a)

if __name__ == "__main__":
    unittest.main()
