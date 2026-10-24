"""Offline, adversarial tests for four NVIDIA-inspired finance entry points."""

from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from aurex.nvidia_finance import (
    BLUEPRINTS,
    SyntheticTransaction,
    compare_distilled_predictions,
    momentum_signal_candidate,
    review_external_fraud_score,
    summarize_synthetic_transactions,
)
from workstation.nvidia_fsi_lab import previews


class NvidiaFinanceBoundaryTests(TestCase):
    def test_catalog_holds_every_real_execution_path(self) -> None:
        self.assertEqual(len(BLUEPRINTS), 4)
        self.assertEqual(len({b.id for b in BLUEPRINTS}), 4)
        for b in BLUEPRINTS:
            self.assertFalse(b.enabled)
            self.assertFalse(b.nvidia_runtime_installed)
            self.assertEqual(b.release, "HOLD")
            self.assertEqual(b.authority, "NONE")
            self.assertTrue(b.source_url.startswith("https://build.nvidia.com/nvidia/"))

    def test_signal_fixed_operator(self) -> None:
        result = momentum_signal_candidate(
            [Decimal("100"), Decimal("99"), Decimal("105"), Decimal("110")], 2
        )
        self.assertEqual(result.synthetic_momentum, (Decimal(110) - Decimal(99)) / Decimal(99))
        self.assertFalse(result.backtested)
        self.assertEqual(result.release, "HOLD")

    def test_signal_rejects_unbounded_and_future_lookback(self) -> None:
        with self.assertRaises(ValueError):
            momentum_signal_candidate([Decimal("1")] * 257, 2)
        with self.assertRaises(ValueError):
            momentum_signal_candidate([Decimal("1"), Decimal("2"), Decimal("3")], 3)
        with self.assertRaises(ValueError):
            momentum_signal_candidate([Decimal("1"), Decimal("2"), Decimal("3")], True)

    def test_signal_rejects_malformed_price_inputs(self) -> None:
        for x in (Decimal("NaN"), Decimal("0"), Decimal("-1"), 1.0, True):
            with self.subTest(x=x), self.assertRaises(ValueError):
                momentum_signal_candidate([Decimal("1"), x, Decimal("3"), Decimal("4")], 2)  # type: ignore[list-item]

    def test_transaction_cent_arithmetic_and_repeats(self) -> None:
        features = summarize_synthetic_transactions(
            [
                SyntheticTransaction("STORE_01", 101),
                SyntheticTransaction("STORE_02", 250),
                SyntheticTransaction("STORE_01", 100),
            ]
        )
        self.assertEqual(features.total_cents, 451)
        self.assertEqual(features.transaction_count, 3)
        self.assertEqual(features.distinct_merchants, 2)
        self.assertEqual(features.repeated_merchant_events, 1)
        self.assertFalse(features.learned_embeddings)
        self.assertEqual(features.authority, "NONE")

    def test_transaction_rejects_real_or_identifying_data(self) -> None:
        bad = [
            SyntheticTransaction("STORE_01", 1, synthetic=False),
            SyntheticTransaction("Real merchant address with spaces", 1),
            SyntheticTransaction("STORE_01", -1),
            SyntheticTransaction("STORE_01", 2.5),  # type: ignore[arg-type]
        ]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(ValueError):
                summarize_synthetic_transactions([item])
        with self.assertRaises(ValueError):
            summarize_synthetic_transactions([])

    def test_distillation_is_metric_only_not_training(self) -> None:
        v = compare_distilled_predictions(
            [True, False, True, False],
            [True, False, True, False],
            [True, False, False, False],
        )
        self.assertEqual(v.teacher_f1, Decimal(1))
        self.assertEqual(v.student_f1, Decimal(2) / Decimal(3))
        self.assertTrue(v.teacher_better)
        self.assertFalse(v.model_trained)
        self.assertEqual(v.release, "HOLD")

    def test_distillation_rejects_label_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            compare_distilled_predictions([True], [True], [True, False])
        with self.assertRaises(ValueError):
            compare_distilled_predictions([1], [True], [False])  # type: ignore[list-item]

    def test_distillation_handles_all_negative_synthetic(self) -> None:
        v = compare_distilled_predictions([False, False], [False, False], [False, False])
        self.assertEqual(v.teacher_f1, Decimal(0))
        self.assertEqual(v.student_f1, Decimal(0))
        self.assertFalse(v.teacher_better)

    def test_fraud_missing_score_fails_closed(self) -> None:
        result = review_external_fraud_score("DEMO-001", synthetic=True)
        self.assertEqual(result.classification, "NO_MODEL_SCORE")
        self.assertIsNone(result.candidate_score)
        self.assertFalse(result.automated_action)
        self.assertFalse(result.verified_fraud)

    def test_fraud_score_remains_advisory(self) -> None:
        v = review_external_fraud_score(
            "DEMO-002", synthetic=True, score=Decimal("0.97"), model_id="provisional/v1"
        )
        self.assertEqual(v.classification, "UNVERIFIED_EXTERNAL_SCORE_REVIEW_ONLY")
        self.assertEqual(v.candidate_score, Decimal("0.97"))
        self.assertFalse(v.verified_fraud)
        self.assertFalse(v.model_validated)
        self.assertFalse(v.automated_action)
        self.assertEqual(v.authority, "NONE")

    def test_fraud_rejects_real_malformed_and_unattributed_scores(self) -> None:
        cases = [
            {"synthetic": False},
            {"synthetic": True, "score": Decimal("0.6")},
            {"synthetic": True, "score": Decimal("Infinity"), "model_id": "test"},
            {"synthetic": True, "score": Decimal("1.2"), "model_id": "test"},
            {"synthetic": True, "score": 0.2, "model_id": "test"},
            {"synthetic": True, "model_id": "test"},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                review_external_fraud_score("DEMO-001", **kwargs)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            review_external_fraud_score("customer-name", synthetic=True)

    def test_no_provider_or_network_required_in_demo(self) -> None:
        with patch("socket.socket", side_effect=AssertionError("outbound network forbidden")):
            out = previews()
        self.assertEqual(out["real_nvidia_execution"], "NOT_RUN")
        self.assertEqual(out["release"], "HOLD")
        self.assertEqual(set(out["cases"]), {b.id for b in BLUEPRINTS})

    def test_demo_has_no_granted_authority(self) -> None:
        cases = previews()["cases"]
        self.assertTrue(all(c["authority"] == "NONE" and c["release"] == "HOLD" for c in cases.values()))
