from datetime import UTC, datetime

from aurex.scientific_evidence import (
    build_intoto_statement,
    build_scientific_manifest,
    verify_scientific_manifest,
)


def test_scientific_manifest_build_and_verify() -> None:
    now = datetime.now(UTC)
    input_b = b"input prompt payload"
    output_b = b"worker result payload"
    commit = "a" * 40

    manifest = build_scientific_manifest(
        job_id="job-1234",
        source_commit=commit,
        worker_id="worker-node-1",
        environment_digest="env-sha256-digest",
        input_bytes=input_b,
        output_bytes=output_b,
        evaluation_result="PASS",
        started_at=now,
        completed_at=now,
        evidence_id="ev-9999",
        verification_status="VERIFIED",
        authority_granted=False,
    )

    assert manifest.job_id == "job-1234"
    assert manifest.evaluation_result == "PASS"
    assert verify_scientific_manifest(manifest, input_b, output_b) is True
    assert verify_scientific_manifest(manifest, b"corrupted input", output_b) is False
    assert verify_scientific_manifest(manifest, input_b, b"corrupted output") is False


def test_intoto_statement_structure() -> None:
    now = datetime.now(UTC)
    manifest = build_scientific_manifest(
        job_id="job-5678",
        source_commit="b" * 40,
        worker_id="worker-node-2",
        environment_digest="env-digest-2",
        input_bytes=b"inp",
        output_bytes=b"out",
        evaluation_result="PASS",
        started_at=now,
        completed_at=now,
        evidence_id="ev-8888",
    )

    stmt = build_intoto_statement(manifest)
    assert stmt.type == "https://in-toto.io/Statement/v0.1"
    assert stmt.subject[0].name == "aurex-job-job-5678"
    assert stmt.predicate["job_id"] == "job-5678"
    assert stmt.predicate["verification_status"] == "NOT VERIFIED"
