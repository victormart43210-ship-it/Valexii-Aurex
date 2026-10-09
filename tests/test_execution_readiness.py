import json
import runpy

import pytest

from aurex.experiments.admission import VerificationAttestation, decide_admission
from aurex.experiments.ledger import EvidenceLedger
from aurex.experiments.runner import ExperimentRunner


def test_unsigned_attestation_never_admits():
    m = runpy.run_path("tests/test_experiment_runner.py")["manifest"]()
    ledger = EvidenceLedger()
    r = ExperimentRunner(ledger).run(m, {"i1": "a", "i2": "b"}, str, str)
    att = VerificationAttestation(
        verifier_id=m.verifier.verifier_id,
        manifest_sha256=r.manifest_sha256,
        run_sha256=r.run_sha256,
        passed=True,
    )
    assert (
        str(decide_admission(m, r.manifest_sha256, r.run_sha256, att, True, True).status)
        == "NOT VERIFIED"
    )


@pytest.mark.parametrize("bad", ["exception", "malformed"])
def test_provider_failure_has_terminal_evidence_without_secrets(bad):
    m = runpy.run_path("tests/test_experiment_runner.py")["manifest"]()
    ledger = EvidenceLedger()

    def solver(prompt):
        if bad == "exception":
            raise RuntimeError("Bearer SYNTHETIC_SECRET")

    r = ExperimentRunner(ledger).run(m, {"i1": "a", "i2": "b"}, solver, str)
    assert not r.complete
    assert ledger.events[-1].event_type == "experiment_completed"
    assert any(e.event_type == "solver_error" for e in ledger.events)
    assert "SYNTHETIC_SECRET" not in json.dumps([e.model_dump(mode="json") for e in ledger.events])


def test_anchored_ledger_detects_suffix_deletion():
    ledger = EvidenceLedger()
    ledger.append("start", {"state": "FAIL"})
    ledger.append("end", {"state": "HOLD"})
    head = ledger.events[-1].event_hash
    count = len(ledger.events)
    assert ledger.verify(expected_head=head, expected_count=count)
    ledger._events.pop()
    assert not ledger.verify(expected_head=head, expected_count=count)
