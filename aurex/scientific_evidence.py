"""Scientific Evidence & Reproducibility Foundation (REANA, in-toto, Inspect AI inspired)."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint


class ScientificManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    job_id: str = Field(min_length=1)
    source_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    worker_id: str = Field(min_length=1)
    environment_digest: str = Field(min_length=1)
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evaluation_result: Literal["PASS", "FAIL", "UNKNOWN"] = "UNKNOWN"
    started_at: str
    completed_at: str
    evidence_id: str = Field(min_length=1)
    verification_status: Literal["NOT VERIFIED", "VERIFIED", "REJECTED"] = "NOT VERIFIED"
    authority_granted: bool = False

    def manifest_sha256(self) -> str:
        body = {
            "job_id": self.job_id,
            "source_commit": self.source_commit,
            "worker_id": self.worker_id,
            "environment_digest": self.environment_digest,
            "input_sha256": self.input_sha256,
            "output_sha256": self.output_sha256,
            "evaluation_result": self.evaluation_result,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "evidence_id": self.evidence_id,
        }
        return fingerprint(body)


class InTotoSubject(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    digest: dict[str, str]


class InTotoStatement(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: Literal["https://in-toto.io/Statement/v0.1"] = "https://in-toto.io/Statement/v0.1"
    subject: tuple[InTotoSubject, ...]
    predicate_type: str = "https://aurex.valexii.ai/scientific-evidence/v1"
    predicate: dict[str, Any]


def build_scientific_manifest(
    job_id: str,
    source_commit: str,
    worker_id: str,
    environment_digest: str,
    input_bytes: bytes,
    output_bytes: bytes,
    evaluation_result: Literal["PASS", "FAIL", "UNKNOWN"],
    started_at: datetime,
    completed_at: datetime,
    evidence_id: str,
    verification_status: Literal["NOT VERIFIED", "VERIFIED", "REJECTED"] = "NOT VERIFIED",
    authority_granted: bool = False,
) -> ScientificManifest:
    return ScientificManifest(
        job_id=job_id,
        source_commit=source_commit,
        worker_id=worker_id,
        environment_digest=environment_digest,
        input_sha256=hashlib.sha256(input_bytes).hexdigest(),
        output_sha256=hashlib.sha256(output_bytes).hexdigest(),
        evaluation_result=evaluation_result,
        started_at=started_at.astimezone(UTC).isoformat(),
        completed_at=completed_at.astimezone(UTC).isoformat(),
        evidence_id=evidence_id,
        verification_status=verification_status,
        authority_granted=authority_granted,
    )


def verify_scientific_manifest(
    manifest: ScientificManifest, input_bytes: bytes, output_bytes: bytes
) -> bool:
    computed_input = hashlib.sha256(input_bytes).hexdigest()
    computed_output = hashlib.sha256(output_bytes).hexdigest()
    if manifest.input_sha256 != computed_input or manifest.output_sha256 != computed_output:
        return False
    return True


def build_intoto_statement(manifest: ScientificManifest) -> InTotoStatement:
    return InTotoStatement(
        subject=(
            InTotoSubject(
                name=f"aurex-job-{manifest.job_id}",
                digest={"sha256": manifest.manifest_sha256()},
            ),
        ),
        predicate=json.loads(manifest.model_dump_json()),
    )
