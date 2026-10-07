from aurex.experiments.admission import VerificationAttestation, decide_admission
from aurex.experiments.contracts import ArmSpec, ExperimentManifest, ResultStatus, VerifierSpec
from aurex.experiments.ledger import EvidenceLedger
from aurex.experiments.runner import ExperimentRunner
from aurex.experiments.tracks.synthetic import identity_solver, uppercase_solver

HASH = "a" * 64


def manifest(*, authorized: bool = True, contamination_checked: bool = True) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="synthetic-001",
        track="synthetic",
        dataset_revision="fixture-v1",
        dataset_sha256=HASH,
        protocol_sha256="b" * 64,
        item_ids=("i1", "i2"),
        baseline=ArmSpec(
            arm_id="baseline", provider="local", model="identity", config_sha256="c" * 64
        ),
        experimental=ArmSpec(
            arm_id="experimental", provider="local", model="uppercase", config_sha256="d" * 64
        ),
        verifier=VerifierSpec(
            verifier_id="independent-fixture",
            family="deterministic",
            reference_access="after-freeze",
        ),
        dataset_authorized=authorized,
        contamination_checked=contamination_checked,
    )


def test_run_is_not_verified_without_independent_attestation() -> None:
    m = manifest()
    ledger = EvidenceLedger()
    report = ExperimentRunner(ledger).run(
        m,
        {"i1": "one", "i2": "two"},
        identity_solver(),
        uppercase_solver(),
    )
    decision = decide_admission(
        m, report.manifest_sha256, report.run_sha256, None, ledger.verify(), report.complete
    )
    assert report.complete
    assert ledger.verify()
    assert decision.status is ResultStatus.NOT_VERIFIED


def test_independent_attestation_can_admit_exact_complete_run() -> None:
    m = manifest()
    ledger = EvidenceLedger()
    report = ExperimentRunner(ledger).run(
        m,
        {"i1": "one", "i2": "two"},
        identity_solver(),
        uppercase_solver(),
    )
    attestation = VerificationAttestation(
        verifier_id=m.verifier.verifier_id,
        manifest_sha256=report.manifest_sha256,
        run_sha256=report.run_sha256,
        passed=True,
    )
    decision = decide_admission(
        m, report.manifest_sha256, report.run_sha256, attestation, ledger.verify(), report.complete
    )
    assert decision.status is ResultStatus.PASS


def test_incomplete_run_holds_even_with_attestation() -> None:
    m = manifest()
    ledger = EvidenceLedger()
    report = ExperimentRunner(ledger).run(m, {"i1": "one"}, identity_solver(), uppercase_solver())
    attestation = VerificationAttestation(
        verifier_id=m.verifier.verifier_id,
        manifest_sha256=report.manifest_sha256,
        run_sha256=report.run_sha256,
        passed=True,
    )
    decision = decide_admission(
        m, report.manifest_sha256, report.run_sha256, attestation, ledger.verify(), report.complete
    )
    assert not report.complete
    assert decision.status is ResultStatus.HOLD


def test_authorization_and_contamination_are_fail_closed() -> None:
    for m in (manifest(authorized=False), manifest(contamination_checked=False)):
        ledger = EvidenceLedger()
        report = ExperimentRunner(ledger).run(
            m, {"i1": "one", "i2": "two"}, identity_solver(), uppercase_solver()
        )
        attestation = VerificationAttestation(
            verifier_id=m.verifier.verifier_id,
            manifest_sha256=report.manifest_sha256,
            run_sha256=report.run_sha256,
            passed=True,
        )
        assert (
            decide_admission(
                m,
                report.manifest_sha256,
                report.run_sha256,
                attestation,
                ledger.verify(),
                report.complete,
            ).status
            is ResultStatus.HOLD
        )
