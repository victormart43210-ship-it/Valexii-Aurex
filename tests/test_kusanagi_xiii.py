"""Adversarial regressions against real API, SQLite, and admission boundaries."""

from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from test_kusanagi_repairs import make_manifest

from aurex import api
from aurex.database import create_job, get_job, list_evidence, update_job_state
from aurex.experiments.admission import VerificationAttestation, decide_admission


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "x" * 32)
    monkeypatch.delenv("AUREX_ADMIN_TOKEN", raising=False)
    monkeypatch.setattr(api, "DEFAULT_DB_PATH", str(tmp_path / "jobs.db"))
    return TestClient(api.app)


AUTH = {"Authorization": "Bearer " + "x" * 32}


def test_health_requires_authentication(client):
    assert client.get("/v1/health").status_code == 401
    assert client.get("/v1/health", headers=AUTH).status_code == 200


def test_missing_worker_cannot_generate_success_evidence(client):
    response = client.post("/v1/jobs", headers=AUTH, json={
        "kind": "regression_scan", "params": {}, "maxCostUsd": 0,
    })
    assert response.status_code == 503
    assert list_evidence(api.DEFAULT_DB_PATH) == []
    assert all(not c["available"] for c in client.get("/v1/capabilities", headers=AUTH).json()["capabilities"])


@pytest.mark.parametrize("params", [{"nested": {"shell": "anything"}}, {"long": "x" * 257}, {"a" * 33: 1}, {"a" + chr(97+i): 1 for i in range(17)}])
def test_job_params_reject_unbounded_or_nested_values(client, params):
    assert client.post("/v1/jobs", headers=AUTH, json={"kind": "regression_scan", "params": params, "maxCostUsd": 0}).status_code == 422


def test_oversized_body_is_rejected_before_job_execution(client):
    assert client.post("/v1/jobs", headers={**AUTH, "Content-Type": "application/json"}, content='{"padding":"' + "x" * 20000 + '"}').status_code == 413


def test_terminal_job_cannot_restart_or_lose_result(tmp_path):
    db = str(tmp_path / "jobs.db")
    create_job(db, "one", "regression_scan", {})
    update_job_state(db, "one", "running")
    update_job_state(db, "one", "succeeded", {"evidence_id": "ev-one"})
    with pytest.raises(ValueError):
        update_job_state(db, "one", "running")
    assert get_job(db, "one")["result"] == {"evidence_id": "ev-one"}


def test_unknown_transition_is_rejected(tmp_path):
    db = str(tmp_path / "jobs.db")
    create_job(db, "one", "regression_scan", {})
    with pytest.raises(ValueError):
        update_job_state(db, "one", "invented")


def signed_attestation(timestamp=None):
    key = Ed25519PrivateKey.generate()
    manifest = make_manifest()
    att = VerificationAttestation(experiment_id=manifest.experiment_id,
        verifier_id=manifest.verifier.verifier_id, verifier_family=manifest.verifier.family,
        manifest_sha256="a" * 64, run_sha256="b" * 64, passed=True,
        signature_scheme="ed25519", public_key_hex=key.public_key().public_bytes_raw().hex(),
        timestamp=timestamp or datetime.now(UTC))
    return manifest, att.model_copy(update={"signature": key.sign(att.digest().encode()).hex()})


def test_self_supplied_signing_key_cannot_establish_independence():
    manifest, att = signed_attestation()
    assert decide_admission(manifest, "a" * 64, "b" * 64, att, True, True).status.value != "PASS"


def test_timestamp_is_bound_to_signature():
    _, att = signed_attestation()
    assert not att.model_copy(update={"timestamp": att.timestamp + timedelta(days=1)}).verify_signature()


def test_operator_trust_can_be_revoked():
    manifest, att = signed_attestation()
    assert decide_admission(manifest, "a" * 64, "b" * 64, att, True, True,
        {att.verifier_id: att.public_key_hex}).status.value == "PASS"
    assert decide_admission(manifest, "a" * 64, "b" * 64, att, True, True,
        {}).status.value == "HOLD"


@pytest.mark.parametrize("delta", [-600, 600])
def test_stale_or_future_trusted_signature_is_not_admitted(delta):
    manifest, att = signed_attestation(datetime.now(UTC) + timedelta(seconds=delta))
    assert decide_admission(manifest, "a" * 64, "b" * 64, att, True, True,
        {att.verifier_id: att.public_key_hex}).status.value == "HOLD"
