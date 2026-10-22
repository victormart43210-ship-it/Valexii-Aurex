"""Run synthetic offline previews for the four NVIDIA financial developer examples.

Use: python -m workstation.nvidia_fsi_lab --catalog|--demo
No NVIDIA runtime calls, payments, model weights or network connectivity.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from aurex.nvidia_finance import (
    BLUEPRINTS,
    SyntheticTransaction,
    compare_distilled_predictions,
    momentum_signal_candidate,
    review_external_fraud_score,
    summarize_synthetic_transactions,
)


def previews() -> dict[str, Any]:
    signal = momentum_signal_candidate(
        [Decimal("100"), Decimal("101"), Decimal("102"), Decimal("104")], lookback=2
    )
    transactions = summarize_synthetic_transactions(
        [
            SyntheticTransaction("STORE_01", 1400),
            SyntheticTransaction("STORE_02", 2500),
            SyntheticTransaction("STORE_01", 800),
        ]
    )
    distilled = compare_distilled_predictions(
        [True, False, True, False],
        [True, False, True, False],
        [True, False, False, False],
    )
    fraud = review_external_fraud_score("DEMO-001", synthetic=True)
    return {
        "input_type": "FICTIONAL_SYNTHETIC_ONLY",
        "release": "HOLD",
        "authority": "NONE",
        "real_nvidia_execution": "NOT_RUN",
        "cases": {
            "quantitative_signal_discovery": asdict(signal),
            "transaction_foundation_model": asdict(transactions),
            "financial_model_distillation": asdict(distilled),
            "financial_fraud_detection": asdict(fraud),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    opts = parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--catalog", action="store_true", help="List staged, disabled integrations")
    opts.add_argument("--demo", action="store_true", help="Run four synthetic local previews")
    args = parser.parse_args()
    payload = (
        {"blueprints": [asdict(spec) for spec in BLUEPRINTS]}
        if args.catalog
        else previews()
    )
    print(json.dumps(payload, indent=2, default=str, sort_keys=True))


if __name__ == "__main__":
    main()
