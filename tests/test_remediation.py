"""Adversarial tests for immutable remediation and retest lineage."""

from aurex.experiments.contracts import ResultStatus
from aurex.experiments.remediation import (
    RemediationCase,
    RetestRecord,
    compute_lineage_digest,
)


def test_remediation_lineage_creation_and_preservation() -> None:
    orig_run_sha = "a" * 64
    retest_run_sha = "b" * 64
    retest_manifest_sha = "c" * 64

    case = RemediationCase(
        remediation_id="rem-001",
        original_experiment_id="exp-fail-001",
        original_run_sha256=orig_run_sha,
        original_outcome=ResultStatus.FAIL,
        remediation_reason="Bug in prompt formatting in arm B",
        changes_description="Fixed prompt template escaping",
    )

    digest = compute_lineage_digest(
        original_run_sha256=orig_run_sha,
        remediation_id=case.remediation_id,
        retest_run_sha256=retest_run_sha,
    )

    retest = RetestRecord(
        retest_id="ret-001",
        remediation_id=case.remediation_id,
        retest_experiment_id="exp-retest-001",
        retest_manifest_sha256=retest_manifest_sha,
        retest_run_sha256=retest_run_sha,
        retest_outcome=ResultStatus.PASS,
        verified_independently=True,
        lineage_digest=digest,
    )

    # Historical fail is immutable and distinct from retest
    assert case.original_outcome == ResultStatus.FAIL
    assert case.original_run_sha256 != retest.retest_run_sha256
    assert retest.retest_outcome == ResultStatus.PASS
    assert len(retest.lineage_digest) == 64
