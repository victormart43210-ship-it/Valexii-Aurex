"""Adversarial attack suite against UER contracts, ledger, runner, and admission."""

import pytest
from pydantic import ValidationError

from aurex.experiments.admission import VerificationAttestation, decide_admission
from aurex.experiments.contracts import AblationSpec, ArmSpec, ExperimentManifest, ResultStatus, VerifierSpec
from aurex.experiments.ledger import EvidenceLedger, LedgerEvent
from aurex.experiments.runner import ExperimentRunner


def make_valid_manifest() -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="exp-attack-001",
        track="benchmark_lab",
        dataset_revision="v1.0",
        dataset_sha256="a" * 64,
        protocol_sha256="b" * 64,
        item_ids=("q1", "q2"),
        baseline=ArmSpec(
            arm_id="baseline-arm",
            provider="openai",
            model="gpt-4o-mini",
            config_sha256="1" * 64,
        ),
        experimental=ArmSpec(
            arm_id="experimental-arm",
            provider="aurex",
            model="aurex-governed-4o",
            config_sha256="2" * 64,
        ),
        verifier=VerifierSpec(
            verifier_id="independent-verifier-01",
            family="symbolic",
            reference_access="blind",
        ),
        dataset_authorized=True,
        contamination_checked=True,
    )


class TestManifestAttacks:
    def test_duplicate_item_ids_rejected(self) -> None:
        with pytest.raises(ValidationError, match="duplicate item IDs"):
            ExperimentManifest(
                experiment_id="exp-dup",
                track="benchmark",
                dataset_revision="v1",
                dataset_sha256="a" * 64,
                protocol_sha256="b" * 64,
                item_ids=("q1", "q1"),
                baseline=ArmSpec(arm_id="b1", provider="p", model="m", config_sha256="1" * 64),
                experimental=ArmSpec(arm_id="e1", provider="p", model="m", config_sha256="2" * 64),
                verifier=VerifierSpec(verifier_id="v1", family="f", reference_access="blind"),
            )

    def test_empty_item_id_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ExperimentManifest(
                experiment_id="exp-empty",
                track="benchmark",
                dataset_revision="v1",
                dataset_sha256="a" * 64,
                protocol_sha256="b" * 64,
                item_ids=("",),
                baseline=ArmSpec(arm_id="b1", provider="p", model="m", config_sha256="1" * 64),
                experimental=ArmSpec(arm_id="e1", provider="p", model="m", config_sha256="2" * 64),
                verifier=VerifierSpec(verifier_id="v1", family="f", reference_access="blind"),
            )

    def test_identical_arms_rejected(self) -> None:
        arm = ArmSpec(arm_id="same-arm", provider="p", model="m", config_sha256="1" * 64)
        with pytest.raises(ValidationError, match="differ"):
            ExperimentManifest(
                experiment_id="exp-same",
                track="benchmark",
                dataset_revision="v1",
                dataset_sha256="a" * 64,
                protocol_sha256="b" * 64,
                item_ids=("q1",),
                baseline=arm,
                experimental=arm,
                verifier=VerifierSpec(verifier_id="v1", family="f", reference_access="blind"),
            )

    def test_malformed_hash_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ArmSpec(arm_id="a1", provider="p", model="m", config_sha256="not-a-64-char-hex")


class TestLedgerAttacks:
    def test_ledger_tampered_payload_detected(self) -> None:
        ledger = EvidenceLedger()
        ledger.append("start", {"k": "v1"})
        ledger.append("step", {"k": "v2"})
        assert ledger.verify() is True

        # Mutate an event in internal storage
        event = ledger._events[0]
        tampered = LedgerEvent(
            sequence=event.sequence,
            event_type=event.event_type,
            payload={"k": "tampered"},
            parent_hash=event.parent_hash,
            event_hash=event.event_hash,
            recorded_at=event.recorded_at,
        )
        ledger._events[0] = tampered
        assert ledger.verify() is False

    def test_ledger_tampered_sequence_detected(self) -> None:
        ledger = EvidenceLedger()
        ledger.append("start", {"k": "v1"})
        ledger.append("step", {"k": "v2"})

        event = ledger._events[1]
        tampered = LedgerEvent(
            sequence=99,
            event_type=event.event_type,
            payload=event.payload,
            parent_hash=event.parent_hash,
            event_hash=event.event_hash,
            recorded_at=event.recorded_at,
        )
        ledger._events[1] = tampered
        assert ledger.verify() is False


class TestRunnerAttacks:
    def test_missing_prompt_results_in_incomplete_run(self) -> None:
        ledger = EvidenceLedger()
        runner = ExperimentRunner(ledger)
        manifest = make_valid_manifest() # requires q1 and q2
        prompts = {"q1": "What is 1+1?"} # missing q2

        report = runner.run(
            manifest=manifest,
            prompts=prompts,
            baseline_solver=lambda p: "2",
            experimental_solver=lambda p: "2",
        )
        assert report.complete is False
        assert len(report.items) == 1

    def test_solver_exception_handling(self) -> None:
        ledger = EvidenceLedger()
        runner = ExperimentRunner(ledger)
        manifest = make_valid_manifest()
        prompts = {"q1": "p1", "q2": "p2"}

        def failing_solver(p: str) -> str:
            if p == "p2":
                raise RuntimeError("Solver exploded!")
            return "ok"

        # The runner should catch solver exceptions, record failure in ledger, and mark run incomplete
        with pytest.raises(RuntimeError):
            runner.run(
                manifest=manifest,
                prompts=prompts,
                baseline_solver=lambda p: "ok",
                experimental_solver=failing_solver,
            )


class TestAdmissionAttacks:
    def test_missing_attestation_yields_not_verified(self) -> None:
        manifest = make_valid_manifest()
        decision = decide_admission(
            manifest=manifest,
            manifest_sha256="a" * 64,
            run_sha256="b" * 64,
            attestation=None,
            ledger_valid=True,
            run_complete=True,
        )
        assert decision.status == ResultStatus.NOT_VERIFIED

    def test_verifier_identity_mismatch_yields_hold(self) -> None:
        manifest = make_valid_manifest()
        attestation = VerificationAttestation(
            verifier_id="imposter-verifier",
            manifest_sha256="a" * 64,
            run_sha256="b" * 64,
            passed=True,
        )
        decision = decide_admission(
            manifest=manifest,
            manifest_sha256="a" * 64,
            run_sha256="b" * 64,
            attestation=attestation,
            ledger_valid=True,
            run_complete=True,
        )
        assert decision.status == ResultStatus.HOLD
        assert "verifier identity mismatch" in decision.rationale


class TestRunnerExceptionHandling:
    def test_solver_exception_recorded_fail_closed(self) -> None:
        ledger = EvidenceLedger()
        runner = ExperimentRunner(ledger)
        manifest = make_valid_manifest()
        prompts = {"q1": "p1", "q2": "p2"}

        def failing_solver(p: str) -> str:
            if p == "p2":
                raise RuntimeError("Solver exploded!")
            return "ok"

        report = runner.run_fail_safe(
            manifest=manifest,
            prompts=prompts,
            baseline_solver=lambda p: "ok",
            experimental_solver=failing_solver,
        )
        assert report.complete is False
        assert len(report.items) == 1
        # Confirm ledger recorded the solver error
        event_types = [e.event_type for e in ledger.events]
        assert "solver_error" in event_types


class TestVerificationBoundaryAttacks:
    def test_attestation_digest_and_family_mismatch(self) -> None:
        manifest = make_valid_manifest()
        m_sha = "a" * 64
        r_sha = "b" * 64
        att = VerificationAttestation(
            experiment_id=manifest.experiment_id,
            verifier_id=manifest.verifier.verifier_id,
            verifier_family="wrong_family",
            manifest_sha256=m_sha,
            run_sha256=r_sha,
            passed=True,
        )
        decision = decide_admission(
            manifest=manifest,
            manifest_sha256=m_sha,
            run_sha256=r_sha,
            attestation=att,
            ledger_valid=True,
            run_complete=True,
        )
        assert decision.status == ResultStatus.HOLD
        assert "verifier family mismatch" in decision.rationale
        assert len(att.digest()) == 64


class TestAblationsAndSecurity:
    def test_manifest_supports_first_class_ablations(self) -> None:
        manifest = ExperimentManifest(
            experiment_id="exp-abl-01",
            track="benchmark_lab",
            dataset_revision="v1",
            dataset_sha256="a" * 64,
            protocol_sha256="b" * 64,
            item_ids=("q1",),
            baseline=ArmSpec(arm_id="b1", provider="p", model="m", config_sha256="1" * 64),
            experimental=ArmSpec(arm_id="e1", provider="p", model="m", config_sha256="2" * 64),
            verifier=VerifierSpec(verifier_id="v1", family="f", reference_access="blind"),
            ablations=(
                AblationSpec(
                    ablation_id="abl-no-verifier",
                    type="no_independent_verifier",
                    description="Evaluating orchestration model without verifier stage",
                ),
            ),
        )
        assert len(manifest.ablations) == 1
        assert manifest.ablations[0].ablation_id == "abl-no-verifier"


class TestChatGPTAdversarialReconciliation:
    def test_solver_error_payload_sanitized_and_terminal_failed_event(self) -> None:
        ledger = EvidenceLedger()
        runner = ExperimentRunner(ledger)
        manifest = make_valid_manifest()
        prompts = {"q1": "p1"}

        def sensitive_failing_solver(p: str) -> str:
            raise RuntimeError("https://secret-api-key:bearer12345@internal.domain/v1")

        report = runner.run_fail_safe(
            manifest=manifest,
            prompts=prompts,
            baseline_solver=lambda p: "ok",
            experimental_solver=sensitive_failing_solver,
        )

        assert report.complete is False
        error_events = [e for e in ledger.events if e.event_type == "solver_error"]
        assert len(error_events) == 1
        err_payload = str(error_events[0].payload)
        assert "bearer12345" not in err_payload
        assert "secret-api-key" not in err_payload
