"""Disabled-by-default, offline research contracts inspired by NVIDIA finance examples.

No NVIDIA code, models, container, payment integration or private data is bundled.
These adapters cannot submit trades, block payments, approve invoices, or grant authority.
"""

from .offline import (
    BLUEPRINTS,
    Blueprint,
    DistillationComparison,
    FraudReview,
    SignalCandidate,
    TransactionFeatures,
    SyntheticTransaction,
    compare_distilled_predictions,
    momentum_signal_candidate,
    review_external_fraud_score,
    summarize_synthetic_transactions,
)

__all__ = [
    "BLUEPRINTS",
    "Blueprint",
    "DistillationComparison",
    "FraudReview",
    "SignalCandidate",
    "TransactionFeatures",
    "SyntheticTransaction",
    "compare_distilled_predictions",
    "momentum_signal_candidate",
    "review_external_fraud_score",
    "summarize_synthetic_transactions",
]
