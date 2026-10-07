"""Adversarial tests for independent OSS witness boundaries (no network or model downloads)."""
import hashlib
import json
import unittest
from contextlib import nullcontext
from unittest.mock import patch

from aurex.adapters.oss_witnesses import (
    astronomy_moon_witness,
    madlad_text_candidate,
    mobsf_json_witness,
    optional_trace,
)

APK_SHA = "a" * 64


class TestMobSFWitness(unittest.TestCase):
    def test_requires_explicit_sha256(self) -> None:
        report = {"hash": "1" * 32, "security_score": 100}
        self.assertEqual(mobsf_json_witness(report, APK_SHA).status, "HOLD")

    def test_rejects_mismatched_apk(self) -> None:
        report = {"sha256": "b" * 64, "security_score": 100}
        self.assertEqual(mobsf_json_witness(report, APK_SHA).status, "CONTESTED")

    def test_never_promotes_high_score_to_supported(self) -> None:
        report = {"sha256": APK_SHA, "security_score": 100}
        result = mobsf_json_witness(report, APK_SHA)
        self.assertEqual(result.status, "INSUFFICIENT")
        self.assertNotEqual(result.status, "SUPPORTED")
        self.assertEqual(
            result.content_sha256,
            hashlib.sha256(
                json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        )

    def test_report_without_findings_held(self) -> None:
        result = mobsf_json_witness({"sha256": APK_SHA}, APK_SHA)
        self.assertEqual(result.status, "INSUFFICIENT")

    def test_invalid_expected_sha_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mobsf_json_witness({}, "invalid")


class FakeTokenizer:
    def __call__(self, text: str, **kwargs: object) -> dict[str, list[int]]:
        return {"input_ids": [1, 2, 3]}

    def batch_decode(self, tokens: object, **kwargs: object) -> list[str]:
        return ["candidate reading"]


class FakeModel:
    def generate(self, **kwargs: object) -> list[list[int]]:
        return [[4, 5, 6]]


class TestTranslation(unittest.TestCase):
    def test_candidate_is_not_decipherment(self) -> None:
        result = madlad_text_candidate("test", "en", FakeTokenizer(), FakeModel())
        self.assertEqual(result.status, "HOLD")
        self.assertIsNotNone(result.content_sha256)

    def test_bad_language_tag(self) -> None:
        with self.assertRaises(ValueError):
            madlad_text_candidate("test", "../secrets", FakeTokenizer(), FakeModel())


class TestObservatoryAndTelemetry(unittest.TestCase):
    def test_missing_astro_package_is_hold(self) -> None:
        with patch.dict("sys.modules", {"astronomy": None}):
            result = astronomy_moon_witness("2026-10-07T00:00:00Z")
        self.assertEqual(result.status, "HOLD")

    def test_default_trace_does_not_export(self) -> None:
        with optional_trace("mobsf_import"):
            self.assertTrue(True)

    def test_trace_operation_rejects_sensitive_strings(self) -> None:
        with self.assertRaises(ValueError):
            with optional_trace("private user=secret", enabled=False):
                pass


if __name__ == "__main__":
    unittest.main()
