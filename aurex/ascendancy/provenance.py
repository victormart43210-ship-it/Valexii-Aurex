"""Algorithm provenance. Classifications are engineering labels, not patent claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Classification = Literal[
    "ORIGINAL_IMPLEMENTATION",
    "ADAPTED_ESTABLISHED_ALGORITHM",
    "OPEN_SOURCE_COMPONENT",
    "RESEARCH_HYPOTHESIS",
    "UNVERIFIED_CLAIM",
]


@dataclass(frozen=True, slots=True)
class AlgorithmRecord:
    algorithm_id: str
    classification: Classification
    established_basis: str
    claim: str


def registry() -> tuple[AlgorithmRecord, ...]:
    """Public classifications for this package. No USB material is included."""
    return (
        AlgorithmRecord(
            "evidence-roots",
            "ADAPTED_ESTABLISHED_ALGORITHM",
            "Directed evidence ancestry and disjoint root sets, already implemented in aurex.evidence_kernel.",
            "Derived records that share a source are one witness.",
        ),
        AlgorithmRecord(
            "bic-hypothesis-score",
            "ADAPTED_ESTABLISHED_ALGORITHM",
            "Schwarz BIC penalty k*log(n)/2 subtracted from a fixed Bernoulli log likelihood.",
            "A complexity penalty can reject a memorizer that fits training labels and fails held-out labels.",
        ),
        AlgorithmRecord(
            "decimal-constraints",
            "ADAPTED_ESTABLISHED_ALGORITHM",
            "Exact Decimal equality, identity equality, and conflicting claims on one subject.",
            "Arithmetic and identity contradictions are detectable without a financial posting.",
        ),
        AlgorithmRecord(
            "interval-supersession",
            "ADAPTED_ESTABLISHED_ALGORITHM",
            "Closed date intervals with a named predecessor, the same rule DISPATER uses for rates.",
            "A successor removes only the named predecessor. The old record stays in history.",
        ),
        AlgorithmRecord(
            "brier-calibration",
            "OPEN_SOURCE_COMPONENT",
            "aurex.governance_math.calibration, Brier score and a prior-only temporal baseline.",
            "On one synthetic holdout the selected rule is better calibrated than the training base rate.",
        ),
        AlgorithmRecord(
            "manifest-sha256",
            "ADAPTED_ESTABLISHED_ALGORITHM",
            "Canonical JSON and SHA-256.",
            "The same inputs produce the same manifest digest.",
        ),
        AlgorithmRecord(
            "ancient-decipherment",
            "UNVERIFIED_CLAIM",
            "No licensed Voynich, Linear A, or Rongorongo corpus was loaded.",
            "This package does not decipher any historical script.",
        ),
    )
