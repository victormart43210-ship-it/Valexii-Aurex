import pytest

from aurex.experiments.contracts import ArmSpec, ExperimentManifest, VerifierSpec
from aurex.experiments.ledger import EvidenceLedger
from aurex.experiments.runner import ExperimentExecutionError, ExperimentRunner
from aurex.experiments.tracks.synthetic import identity_solver


HASH = "a" * 64


def manifest() -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="failure-001",
        track="synthetic",
        dataset_revision="fixture-v1",
        dataset_sha256=HASH,
        protocol_sha256="b" * 64,
        item_ids=("i1",),
        baseline=ArmSpec(
            arm_id="baseline", provider="local", model="identity", config_sha256="c" * 64
        ),
        experimental=ArmSpec(
            arm_id="experimental", provider="local", model="boom", config_sha256="d" * 64
        ),
        verifier=VerifierSpec(
            verifier_id="independent-fixture",
            family="deterministic",
            reference_access="after-freeze",
        ),
        dataset_authorized=True,
        contamination_checked=True,
    )


def exploding_solver() -> object:
    def solve(_: str) -> str:
        raise RuntimeError("provider exploded")

    return solve


def test_solver_failure_is_recorded_and_cannot_look_complete() -> None:
    ledger = EvidenceLedger()

    with pytest.raises(ExperimentExecutionError) as caught:
        ExperimentRunner(ledger).run(
            manifest(), {"i1": "one"}, identity_solver(), exploding_solver()
        )

    assert caught.value.item_id == "i1"
    assert caught.value.arm_id == "experimental"
    assert ledger.verify()
    assert [event.event_type for event in ledger.events] == [
        "experiment_started",
        "item_failed",
        "experiment_failed",
    ]
    assert ledger.events[-1].payload["complete"] is False
    assert ledger.events[-1].payload["error_type"] == "RuntimeError"
    assert "provider exploded" not in str(ledger.events[-1].payload)
