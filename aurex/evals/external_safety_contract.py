"""Provider-neutral, offline safety evaluation contract.

This module does not authorize actions, contact providers, or declare compliance.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True)
class SafetyCase:
    scenario_id: str
    fixture: bytes
    expected_security_property: str
    tenant_id: str = "synthetic"

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.expected_security_property.strip():
            raise ValueError("scenario and security property are required")
        if not self.tenant_id.strip():
            raise ValueError("tenant is required")
        if not self.fixture or len(self.fixture) > 65536:
            raise ValueError("fixture must be 1..65536 bytes")

    @property
    def fixture_sha256(self) -> str:
        return sha256(self.fixture).hexdigest()


@dataclass(frozen=True)
class SafetyResult:
    scenario_id: str
    fixture_sha256: str
    expected_security_property: str
    verdict: Verdict
    engine_version: str
    source_commit_sha: str
    reviewer_id: str | None = None
    implementer_id: str | None = None
    evidence_receipt: str | None = None
    explanation: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, Verdict):
            raise ValueError("unknown verdict")
        if not self.scenario_id.strip() or not self.expected_security_property.strip():
            raise ValueError("scenario and property required")
        if len(self.fixture_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.fixture_sha256):
            raise ValueError("invalid fixture hash")
        if not self.engine_version.strip() or not self.source_commit_sha.strip():
            raise ValueError("engine version and source commit required")
        if self.verdict is Verdict.PASS and (
            not self.implementer_id or not self.implementer_id.strip()
            or self.reviewer_id == self.implementer_id
            or not self.reviewer_id or not self.reviewer_id.strip()
            or not self.evidence_receipt or not self.evidence_receipt.strip()
        ):
            raise ValueError("PASS requires independent reviewer and evidence receipt")


Evaluator = Callable[[SafetyCase], SafetyResult]


def evaluate_offline(case: SafetyCase, evaluator: Evaluator, *,
                     engine_version: str, source_commit_sha: str) -> SafetyResult:
    """Run an injected evaluator, demoting exceptions and mismatches to NOT_VERIFIED."""
    if not engine_version.strip() or not source_commit_sha.strip():
        raise ValueError("version and source SHA required")
    try:
        result = evaluator(case)
        if not isinstance(result, SafetyResult):
            raise TypeError("invalid evaluator result")
        if (result.scenario_id != case.scenario_id
                or result.fixture_sha256 != case.fixture_sha256
                or result.expected_security_property != case.expected_security_property
                or result.engine_version != engine_version
                or result.source_commit_sha != source_commit_sha):
            raise ValueError("evaluation provenance mismatch")
        return result
    except Exception:
        return SafetyResult(
            scenario_id=case.scenario_id,
            fixture_sha256=case.fixture_sha256,
            expected_security_property=case.expected_security_property,
            verdict=Verdict.NOT_VERIFIED,
            engine_version=engine_version,
            source_commit_sha=source_commit_sha,
            explanation="Evaluator failed or provenance could not be verified.",
        )
