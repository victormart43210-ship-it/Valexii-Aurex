"""Governed Learning Ledger for AUREX.

Quarantines human audit corrections by default. Model weights and prompts
cannot be modified automatically without explicit owner review and separate admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class CorrectionStatus(StrEnum):
    QUARANTINED = "QUARANTINED"
    REVIEWED = "REVIEWED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class LearningCorrection:
    correction_id: str
    audit_id: str
    original_conclusion: str
    human_correction: str
    status: CorrectionStatus = CorrectionStatus.QUARANTINED
    created_at_iso: str = ""

    def __post_init__(self) -> None:
        if not self.created_at_iso:
            object.__setattr__(self, "created_at_iso", datetime.now(UTC).isoformat())


class GovernedLearningLedger:
    """In-memory or persistent store enforcing default quarantine on learning corrections."""

    def __init__(self) -> None:
        self._corrections: dict[str, LearningCorrection] = {}

    def submit_correction(
        self, correction_id: str, audit_id: str, original: str, human_fix: str
    ) -> LearningCorrection:
        """Submit a correction into mandatory quarantine."""
        entry = LearningCorrection(
            correction_id=correction_id,
            audit_id=audit_id,
            original_conclusion=original,
            human_correction=human_fix,
            status=CorrectionStatus.QUARANTINED,
        )
        self._corrections[correction_id] = entry
        return entry

    def get_correction(self, correction_id: str) -> LearningCorrection | None:
        return self._corrections.get(correction_id)

    def can_apply_to_production(self, correction_id: str) -> bool:
        """Enforce invariant: Quarantined or non-owner corrections NEVER modify production prompts/weights."""
        entry = self.get_correction(correction_id)
        if entry is None or entry.status != CorrectionStatus.REVIEWED:
            return False
        return False  # Autonomous self-modification is strictly prohibited
