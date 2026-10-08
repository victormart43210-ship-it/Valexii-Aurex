"""Fail-closed admission rules for experiment results."""

from pydantic import BaseModel, ConfigDict

from .contracts import ExperimentManifest, ResultStatus


class VerificationAttestation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    verifier_id: str
    manifest_sha256: str
    run_sha256: str
    passed: bool


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
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="dataset authorization not established")
    if not manifest.contamination_checked:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="contamination check not established")
    if attestation is None:
        return AdmissionDecision(
            status=ResultStatus.NOT_VERIFIED,
            rationale="independent verification is missing",
        )
    if attestation.verifier_id != manifest.verifier.verifier_id:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="verifier identity mismatch")
    if attestation.manifest_sha256 != manifest_sha256 or attestation.run_sha256 != run_sha256:
        return AdmissionDecision(status=ResultStatus.HOLD, rationale="attestation target mismatch")
    if not attestation.passed:
        return AdmissionDecision(status=ResultStatus.FAIL, rationale="independent verifier rejected run")
    return AdmissionDecision(status=ResultStatus.PASS, rationale="independent verification admitted")
