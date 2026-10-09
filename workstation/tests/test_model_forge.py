"""Offline Model Forge checks. Run: python3 -m unittest discover -s workstation/tests -v"""
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_forge import ModelCandidate, tiny_training_demo, write_manifest

class ModelForgeTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(tiny_training_demo(100, 17), tiny_training_demo(100, 17))
    def test_bounds(self):
        with self.assertRaises(ValueError):
            tiny_training_demo(0)
    def test_license_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "weights.gguf"
            path.write_bytes(b"fake test bytes")
            candidate = ModelCandidate("test", "example", "commit", "unknown", False)
            with self.assertRaises(ValueError):
                write_manifest(candidate, path, Path(folder) / "manifest.json")
    def test_reviewed_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "weights.gguf"
            path.write_bytes(b"fake test bytes")
            candidate = ModelCandidate("test", "example", "commit", "test-only", True)
            manifest = write_manifest(candidate, path, Path(folder) / "manifest.json")
            self.assertEqual(manifest["verification"], "PROVENANCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED")
            self.assertEqual(len(manifest["weights_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
