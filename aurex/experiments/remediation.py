"""Immutable remediation lineage tracking for FAIL -> remediation -> retest -> replication."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aurex.experiments.contracts import ResultStatus
from aurex.provenance import fingerprint


class RemediationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    remediation_id: str = Field(min_length=1)
    original_experiment_id: str = Field(min_length=1)
    original_run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    original_outcome: ResultStatus = ResultStatus.FAIL
    remediation_reason: str = Field(min_length=1)
    changes_description: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RetestRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    retest_id: str = Field(min_length=1)
    remediation_id: str = Field(min_length=1)
    retest_experiment_id: str = Field(min_length=1)
    retest_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retest_run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retest_outcome: ResultStatus
    verified_independently: bool = False
    lineage_digest: str


def compute_lineage_digest(
    original_run_sha256: str,
    remediation_id: str,
    retest_run_sha256: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    body = {
        "original_run_sha256": original_run_sha256,
        "remediation_id": remediation_id,
        "retest_run_sha256": retest_run_sha256,
        "metadata": metadata or {},
    }
    return fingerprint(body)
