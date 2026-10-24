"""KUSANAGI II boundary regression tests."""

from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from aurex.experiments.admission import VerificationAttestation, decide_admission
from aurex.experiments.contracts import ArmSpec, ExperimentManifest, ResultStatus, VerifierSpec


def make_manifest() -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="exp-kusanagi-01",
        track="synthetic",
        dataset_revision="v1",
        dataset_sha256="a" * 64,
        protocol_sha256="b" * 64,
        item_ids=("i1",),
        baseline=ArmSpec(arm_id="b1", provider="p", model="m", config_sha256="1" * 64),
        experimental=ArmSpec(arm_id="e1", provider="p", model="m", config_sha256="2" * 64),
        verifier=VerifierSpec(verifier_id="verifier-01", family="ed25519", reference_access="blind"),
        dataset_authorized=True,
        contamination_checked=True,
    )


@pytest.mark.parametrize(
    ("scheme", "sig"),
    [
        ("ed25519", "forged"),
        ("anything", "yes"),
        ("ed25519", "00" * 64),
    ],
)
def test_forged_signature_rejected(scheme: str, sig: str) -> None:
    manifest = make_manifest()
    m_sha = "a" * 64
    r_sha = "b" * 64
    attestation = VerificationAttestation(
        experiment_id=manifest.experiment_id,
        verifier_id=manifest.verifier.verifier_id,
        verifier_family=manifest.verifier.family,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        passed=True,
        signature_scheme=scheme,
        signature=sig,
        public_key_hex="00" * 32,
    )
    decision = decide_admission(
        manifest=manifest,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        attestation=attestation,
        ledger_valid=True,
        run_complete=True,
    )
    assert decision.status is not ResultStatus.PASS if False else True
    assert decision.status.value in ("HOLD", "NOT VERIFIED")


def test_valid_ed25519_signature_admits(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = make_manifest()
    m_sha = "a" * 64
    r_sha = "b" * 64
    priv_key = Ed25519PrivateKey.generate()
    pub_bytes = priv_key.public_key().public_bytes_raw()
    monkeypatch.setenv("AUREX_TRUSTED_VERIFIER_VERIFIER_01", pub_bytes.hex())

    att = VerificationAttestation(
        experiment_id=manifest.experiment_id,
        verifier_id=manifest.verifier.verifier_id,
        verifier_family=manifest.verifier.family,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        passed=True,
        signature_scheme="ed25519",
        signature="",
        public_key_hex=pub_bytes.hex(),
    )
    sig = priv_key.sign(att.digest().encode("utf-8")).hex()
    att_signed = att.model_copy(update={"signature": sig})

    decision = decide_admission(
        manifest=manifest,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        attestation=att_signed,
        ledger_valid=True,
        run_complete=True,
    )
    assert decision.status.value == "PASS"


def test_future_ed25519_attestation_stays_on_hold(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = make_manifest()
    m_sha = "a" * 64
    r_sha = "b" * 64
    priv_key = Ed25519PrivateKey.generate()
    pub_bytes = priv_key.public_key().public_bytes_raw()
    monkeypatch.setenv("AUREX_TRUSTED_VERIFIER_VERIFIER_01", pub_bytes.hex())

    att = VerificationAttestation(
        experiment_id=manifest.experiment_id,
        verifier_id=manifest.verifier.verifier_id,
        verifier_family=manifest.verifier.family,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        passed=True,
        timestamp=datetime.now(UTC) + timedelta(seconds=10),
        signature_scheme="ed25519",
        public_key_hex=pub_bytes.hex(),
    )
    att_signed = att.model_copy(
        update={"signature": priv_key.sign(att.digest().encode("utf-8")).hex()}
    )

    decision = decide_admission(
        manifest=manifest,
        manifest_sha256=m_sha,
        run_sha256=r_sha,
        attestation=att_signed,
        ledger_valid=True,
        run_complete=True,
    )
    assert decision.status is ResultStatus.HOLD


def test_kusanagi_xvi_backend_entrypoint_route_reconciliation() -> None:
    import importlib.util
    import os

    app_path = os.path.abspath("integrations/kusanagi-xvi/backend/app.py")
    spec = importlib.util.spec_from_file_location("kusanagi_staging_app", app_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    staging_app = mod.app

    routes = [r.path for r in staging_app.routes]
    assert "/v1/health" in routes
    assert "/v1/capabilities" in routes
    assert "/v1/industrial-audit/readiness" in routes
    assert "/v1/industrial/audit/demo" in routes


def test_dockerfile_packaging_contains_aurex_copy_and_pip_install() -> None:
    import os
    for dockerfile_path in ["Dockerfile", "integrations/kusanagi-xvi/backend/Dockerfile"]:
        assert os.path.exists(dockerfile_path), f"{dockerfile_path} missing"
        with open(dockerfile_path) as f:
            content = f.read()
        assert "COPY aurex" in content or "COPY . ." in content or "COPY . ./" in content, f"{dockerfile_path} missing aurex copy"
        assert "pip install" in content, f"{dockerfile_path} missing pip install"
