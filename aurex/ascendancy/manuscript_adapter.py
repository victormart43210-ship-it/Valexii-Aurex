"""Synthetic known-language calibration before any historical script is scored.

The calibration language is invented for this test. A sequence is grammatical
when it has three signs, starts with ``1``, and ends with ``2``. One training
row violates that rule on purpose so a memorizer can outscore the rule until
the complexity penalty is applied. Voynich, Linear A, and Rongorongo are not
loaded and are not deciphered.
"""

from __future__ import annotations

from aurex.ascendancy.hypothesis import Hypothesis, ScoredHypothesis, score_hypotheses

TRAIN: tuple[tuple[tuple[str, ...], bool], ...] = (
    (("1", "0", "2"), True),
    (("1", "3", "2"), True),
    (("1", "4", "2"), True),
    (("1", "1", "2"), True),
    (("9", "9", "9"), True),
    (("1", "0", "0"), False),
    (("0", "3", "2"), False),
    (("3", "3", "3"), False),
)

HOLDOUT: tuple[tuple[tuple[str, ...], bool], ...] = (
    (("1", "5", "2"), True),
    (("1", "2", "2"), True),
    (("4", "4", "4"), False),
    (("0", "1", "2"), False),
)

_MEMORY = frozenset(sequence for sequence, label in TRAIN if label)


def kite_rule(sequence: tuple[str, ...]) -> bool:
    return len(sequence) == 3 and sequence[0] == "1" and sequence[2] == "2"


def memorize_train(sequence: tuple[str, ...]) -> bool:
    return sequence in _MEMORY


def accept_all(sequence: tuple[str, ...]) -> bool:
    return True


def hypotheses() -> tuple[Hypothesis, ...]:
    return (
        Hypothesis("kite-rule", 2, kite_rule),
        Hypothesis("memorize-train", len(_MEMORY), memorize_train),
        Hypothesis("accept-all", 0, accept_all),
    )


def rank_training(*, penalty: bool) -> tuple[ScoredHypothesis, ...]:
    return score_hypotheses(hypotheses(), TRAIN, penalty=penalty)


def unlabeled_status(corpus: str) -> dict[str, object]:
    """Historical corpora stay unevaluated. An unlabeled sample is not a reading."""
    if corpus in {"Voynich", "Linear A", "Rongorongo"}:
        return {
            "corpus": corpus,
            "status": "NOT_EVALUATED",
            "decipherment_claimed": False,
            "reason": "No licensed corpus was loaded.",
        }
    return {
        "corpus": corpus,
        "status": "INSUFFICIENT_EVIDENCE",
        "decipherment_claimed": False,
        "reason": "Sequences without held-out labels do not select a reading.",
    }
