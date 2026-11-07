"""M2. Competing hypotheses with a fixed likelihood and a BIC-style penalty.

The likelihood is not estimated from the data. A correct label contributes
log(0.9) and an incorrect label contributes log(0.1). The penalty is the
established BIC term k*log(n)/2 in nats. Turning the penalty off is the ablation.
Scores are advisory and cannot authorize money, security, or a decipherment.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

CORRECT_LOG = math.log(0.9)
INCORRECT_LOG = math.log(0.1)
Predictor = Callable[[tuple[str, ...]], bool]


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    complexity: int
    predict: Predictor


@dataclass(frozen=True, slots=True)
class ScoredHypothesis:
    hypothesis_id: str
    complexity: int
    correct: int
    total: int
    log_likelihood: float
    penalty: float
    score: float
    authority: str = "ADVISORY_ONLY"


def score_hypotheses(
    hypotheses: Sequence[Hypothesis],
    labeled: Sequence[tuple[tuple[str, ...], bool]],
    *,
    penalty: bool,
) -> tuple[ScoredHypothesis, ...]:
    """Score every hypothesis. Higher score is preferred, then lower complexity."""
    if not hypotheses:
        raise ValueError("at least one hypothesis is required")
    if not labeled or len(labeled) > 10_000:
        raise ValueError("labeled sample must contain 1..10000 rows")
    n = len(labeled)
    scored: list[ScoredHypothesis] = []
    for item in hypotheses:
        if item.complexity < 0:
            raise ValueError("complexity must be nonnegative")
        correct = sum(item.predict(sequence) is label for sequence, label in labeled)
        wrong = n - correct
        log_likelihood = correct * CORRECT_LOG + wrong * INCORRECT_LOG
        applied = (item.complexity * math.log(n) / 2) if penalty else 0.0
        scored.append(
            ScoredHypothesis(
                hypothesis_id=item.hypothesis_id,
                complexity=item.complexity,
                correct=correct,
                total=n,
                log_likelihood=log_likelihood,
                penalty=applied,
                score=log_likelihood - applied,
            )
        )
    scored.sort(key=lambda row: (-row.score, row.complexity, row.hypothesis_id))
    return tuple(scored)
