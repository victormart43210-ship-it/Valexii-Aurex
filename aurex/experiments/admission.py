"""Fail-closed admission rules for experiment results."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint

from .contracts import ExperimentManifest, ResultStatus


class VerificationAttestation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    verifier_id: str = Field(min_length=1)
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    passed: bool
    experiment_id: str = ""
    verifier_family: str = ""
    verification_protocol_version: str = "1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signature_scheme: str = "none"
    signature: str = ""

    def digest(self) -> str:
        body = {
            "experiment_id": self.experiment_id,
            "verifier_id": self.verifier_id,
            "verifier_family": self.verifier_family,
            "manifest_sha256": self.manifest_sha256,
            "run_sha256": self.run_sha256,
            "verification_protocol_version": self.verification_protocol_version,
            "passed": self.passed,
            "signature_scheme": self.signature_scheme,
        }
        return fingerprint(body)


class AdmissionDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ResultStatus
    rationale: str


def decide_admission(
    manifest: ExperimentManifest,
    manifest_sha256: str,
    run_sha256: str,
    attestation: VerificationAttestation | None,
    ledger_valid: bool,
    run_complete: bool,
) -> AdmissionDecision:
    if not ledger_valid:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="ledger integrity failed")
    if not run_complete:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="run is incomplete")
    if not manifest.dataset_authorized:
        return AdmissionDecision(
            status=ResultStatus.HOLD, rationale="dataset authorization not established"
        )
    if not manifest.contamination_checked:
        return AdmissionDecision(
            status=ResultStatus.HOLD, rationale="contamination check not established"
        )
    if attestation is None:
        return AdmissionDecision(
            status=ResultStatus.NOT_VERIFIED,
            rationale="independent verification is missing",
        )
    if attestation.experiment_id and attestation.experiment_id != manifest.experiment_id:
        return AdmissionDecision(
            status=ResultStatus.HOLD, rationale="attestation experiment ID mismatch"
        )
    if attestation.verifier_id != manifest.verifier.verifier_id:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="verifier identity mismatch")
    if attestation.verifier_family and attestation.verifier_family != manifest.verifier.family:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="verifier family mismatch")
    if attestation.manifest_sha256 != manifest_sha256 or attestation.run_sha256 != run_sha256:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="attestation target mismatch")
    if not attestation.passed:
        return AdmissionDecision(
            status=ResultStatus.FAIL, rationale="independent verifier rejected run"
        )
    return AdmissionDecision(
        status=ResultStatus.PASS, rationale="independent verification admitted"
    )
