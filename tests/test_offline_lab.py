from aurex.database import create_job
from aurex.offline_lab import claim_job_for_worker, finalize_probe


def test_offline_lab_worker_claim_and_finalize_probe(tmp_path) -> None:
    db_file = str(tmp_path / "offline_lab_test.db")
    job = create_job(db_file, "job-lab-001", "regression_scan", {"test": True})
    assert job["state"] == "queued"

    claimed = claim_job_for_worker(db_file, "worker-node-x")
    assert claimed is not None
    assert claimed["state"] == "running"

    inp_b = b"test input"
    out_b = b"test output"
    finalized = finalize_probe(
        db_path=db_file,
        job_id="job-lab-001",
        worker_id="worker-node-x",
        params={"test": True},
        input_bytes=inp_b,
        output_bytes=out_b,
    )
    assert finalized["state"] == "succeeded"
    assert "evidence_id" in finalized["result"]
