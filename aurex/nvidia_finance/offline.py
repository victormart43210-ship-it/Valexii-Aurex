"""Four bounded *local* research hooks for NVIDIA financial developer examples.

Everything here is deterministic, synthetic-only and uses Python stdlib.
Real NVIDIA agent orchestration, NeMo training, embeddings, GNN/XGBoost and
Dynamo-Triton inference are NOT installed, available, or verified.
No network, data export, training, trading or account access is possible here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

Authority = Literal["NONE"]
Status = Literal["RESEARCH_ONLY", "HOLD"]
MAX_RECORDS = 256
_ALLOWED_MERCHANT = re.compile(r"[A-Z0-9_-]{2,32}\Z")
_ALLOWED_MODEL = re.compile(r"[a-zA-Z0-9_.:/-]{3,80}\Z")


@dataclass(frozen=True, slots=True)
class Blueprint:
    id: str
    title: str
    source_url: str
    required_runtime: str
    implemented_scope: str
    nvidia_runtime_installed: bool = False
    enabled: bool = False
    authority: Authority = "NONE"
    release: Status = "HOLD"


BLUEPRINTS: tuple[Blueprint, ...] = (
    Blueprint(
        "quantitative_signal_discovery",
        "Quantitative Signal Discovery Agent",
        "https://build.nvidia.com/nvidia/quantitative-signal-discovery-agent",
        "NVIDIA Nemotron + NeMo Agent Toolkit; optional hosted NIM",
        "Offline synthetic momentum formula; no generated-code execution or backtest",
    ),
    Blueprint(
        "transaction_foundation_model",
        "Build Your Own Transaction Foundation Model",
        "https://build.nvidia.com/nvidia/build-your-own-transaction-foundation-model",
        "NVIDIA NeMo AutoModel + RAPIDS; A100 80GB or H100 for blueprint",
        "Exact synthetic transaction summary; NOT learned transformer embeddings",
    ),
    Blueprint(
        "financial_model_distillation",
        "AI Model Distillation for Financial Data",
        "https://build.nvidia.com/nvidia/ai-model-distillation-for-financial-data",
        "NVIDIA Data Flywheel + NeMo Customizer/Evaluator; multiple GPUs",
        "Teacher/student synthetic prediction comparison; NO fine-tuning or distillation",
    ),
    Blueprint(
        "financial_fraud_detection",
        "Financial Fraud Detection",
        "https://build.nvidia.com/nvidia/financial-fraud-detection",
        "RAPIDS + GNN/XGBoost training + Dynamo-Triton inference; 32GB GPU",
        "Unverified external risk-score intake; NO model, fraud decision or payment block",
    ),
)


def _bounded(prices_or_rows: object, n: int) -> None:
    if type(prices_or_rows) not in (list, tuple) or not 1 <= n <= MAX_RECORDS:
        raise ValueError("requires 1-256 ordered synthetic records")


def _decimal(value: object, *, positive: bool = False, score: bool = False) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        raise ValueError("finite Decimal required; floats and bool are forbidden")
    if positive and value <= 0:
        raise ValueError("strictly positive Decimal required")
    if score and not Decimal("0") <= value <= Decimal("1"):
        raise ValueError("risk score must be within [0, 1]")
    return value


@dataclass(frozen=True, slots=True)
class SignalCandidate:
    formula: str
    lookback: int
    synthetic_momentum: Decimal
    provenance: str = "INPUT_PROVIDED_SYNTHETIC"
    backtested: bool = False
    authority: Authority = "NONE"
    release: Status = "HOLD"


def momentum_signal_candidate(
    synthetic_prices: list[Decimal] | tuple[Decimal, ...], lookback: int
) -> SignalCandidate:
    """A fixed reference operator only. Not NVIDIA agents, alpha, or a trade signal."""
    _bounded(synthetic_prices, len(synthetic_prices))
    if type(lookback) is not int or not 2 <= lookback < len(synthetic_prices):
        raise ValueError("lookback must precede final price by at least two observations")
    if any(type(p) is not Decimal or not p.is_finite() or p <= 0 for p in synthetic_prices):
        raise ValueError("synthetic prices must be finite, positive Decimals")
    older = synthetic_prices[-1 - lookback]
    momentum = (synthetic_prices[-1] - older) / older
    return SignalCandidate("(price[t] - price[t-lookback]) / price[t-lookback]", lookback, momentum)


@dataclass(frozen=True, slots=True)
class SyntheticTransaction:
    merchant_code: str
    amount_cents: int
    synthetic: bool = True


@dataclass(frozen=True, slots=True)
class TransactionFeatures:
    transaction_count: int
    total_cents: int
    distinct_merchants: int
    repeated_merchant_events: int
    source: str = "SYNTHETIC_STRUCTURED_INPUT"
    learned_embeddings: bool = False
    authority: Authority = "NONE"
    release: Status = "HOLD"


def summarize_synthetic_transactions(
    rows: list[SyntheticTransaction] | tuple[SyntheticTransaction, ...],
) -> TransactionFeatures:
    """Exact-cent CPU baseline, explicitly NOT a NVIDIA foundation model."""
    _bounded(rows, len(rows))
    seen: set[str] = set()
    repeats = 0
    total = 0
    for row in rows:
        if (
            type(row) is not SyntheticTransaction
            or row.synthetic is not True
            or type(row.merchant_code) is not str
            or not _ALLOWED_MERCHANT.fullmatch(row.merchant_code)
            or type(row.amount_cents) is not int
            or not 0 <= row.amount_cents <= 100_000_000
        ):
            raise ValueError("only bounded, explicitly synthetic transaction codes and cents")
        total += row.amount_cents
        if row.merchant_code in seen:
            repeats += 1
        seen.add(row.merchant_code)
    return TransactionFeatures(len(rows), total, len(seen), repeats)


@dataclass(frozen=True, slots=True)
class DistillationComparison:
    teacher_f1: Decimal
    student_f1: Decimal
    teacher_better: bool
    model_trained: bool = False
    data_origin: str = "SYNTHETIC_HUMAN_LABELS_NOT_INDEPENDENT"
    authority: Authority = "NONE"
    release: Status = "HOLD"


def _f1(reference: list[bool] | tuple[bool, ...], predictions: list[bool] | tuple[bool, ...]) -> Decimal:
    tp = sum(a and b for a, b in zip(reference, predictions, strict=True))
    fp = sum(not a and b for a, b in zip(reference, predictions, strict=True))
    fn = sum(a and not b for a, b in zip(reference, predictions, strict=True))
    denominator = 2 * tp + fp + fn
    return Decimal(2 * tp) / Decimal(denominator) if denominator else Decimal("0")


def compare_distilled_predictions(
    synthetic_reference: list[bool] | tuple[bool, ...],
    teacher_predictions: list[bool] | tuple[bool, ...],
    student_predictions: list[bool] | tuple[bool, ...],
) -> DistillationComparison:
    """Offline scoring comparison; DOES NOT train, distill or load models."""
    _bounded(synthetic_reference, len(synthetic_reference))
    if not len(synthetic_reference) == len(teacher_predictions) == len(student_predictions):
        raise ValueError("paired predictions required")
    if any(
        type(x) is not bool
        for seq in (synthetic_reference, teacher_predictions, student_predictions)
        for x in seq
    ):
        raise ValueError("predictions and synthetic labels must be exact bools")
    teacher = _f1(synthetic_reference, teacher_predictions)
    student = _f1(synthetic_reference, student_predictions)
    return DistillationComparison(teacher, student, teacher > student)


@dataclass(frozen=True, slots=True)
class FraudReview:
    case_id: str
    candidate_score: Decimal | None
    classification: str
    verified_fraud: bool = False
    model_validated: bool = False
    automated_action: bool = False
    authority: Authority = "NONE"
    release: Status = "HOLD"


def review_external_fraud_score(
    case_id: str,
    *,
    synthetic: bool,
    model_id: str | None = None,
    score: Decimal | None = None,
) -> FraudReview:
    """Accept an unverified external candidate; never infer 'fraud' or block activity."""
    if synthetic is not True or type(case_id) is not str or not re.fullmatch(r"DEMO-[0-9]{3}", case_id):
        raise ValueError("synthetic DEMO-### cases only")
    if score is None and model_id is not None:
        raise ValueError("model identity without score is not meaningful")
    if score is not None:
        _decimal(score, score=True)
        if type(model_id) is not str or not _ALLOWED_MODEL.fullmatch(model_id):
            raise ValueError("declared model identity required for unverified score")
        status = "UNVERIFIED_EXTERNAL_SCORE_REVIEW_ONLY"
    else:
        status = "NO_MODEL_SCORE"
    return FraudReview(case_id, score, status)
