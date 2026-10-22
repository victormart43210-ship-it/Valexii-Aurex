"""Read-only, authenticated job-to-evidence receipts for bounded AUREX probes.

A stored hash proves local byte consistency, NOT independent factual accuracy.
No model output, customer file or external spend is admitted by this module.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any

from aurex.database import get_db, get_job

_JOB_ID = re.compile(r"job-[0-9a-f]{24}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SQLITE_FIELDS = frozenset({"probe", "executed", "passed", "sha256", "verification"})
_FIELD_FIELDS = frozenset({
    "probe", "synthetic", "suite_sha256", "case_count",
    "exact_case_matches", "finding_labels", "false_positive_flags",
    "false_negative_flags", "result", "independent_verification",
    "real_document_accuracy", "authority", "effect", "production_release",
})


def _bounded_observation(observation: object) -> dict[str, Any]:
    """Refuse arbitrary data even if an upstream job has been corrupted."""
    if not isinstance(observation, dict) or len(observation) > 20:
        raise ValueError("Observation shape unavailable")
    if observation.get("probe") == "sqlite_roundtrip_v1":
        if set(observation) != _SQLITE_FIELDS:
            raise ValueError("Unexpected probe fields")
        if (observation.get("executed") is not True
                or observation.get("passed") is not True
                or observation.get("verification") != "NOT VERIFIED"
                or not isinstance(observation.get("sha256"), str)
                or not _SHA256.fullmatch(observation["sha256"])):
            raise ValueError("Probe report invalid")
    elif observation.get("probe") == "synthetic_field_audit_v1":
        if set(observation) != _FIELD_FIELDS:
            raise ValueError("Unexpected synthetic report fields")
        if (observation.get("synthetic") is not True
                or observation.get("independent_verification") != "NOT_VERIFIED"
                or observation.get("real_document_accuracy") != "NOT_MEASURED"
                or observation.get("authority") != "HOLD"
                or observation.get("effect") != "NONE"
                or observation.get("production_release") != "HOLD"
                or not isinstance(observation.get("suite_sha256"), str)
                or not _SHA256.fullmatch(observation["suite_sha256"])):
            raise ValueError("Synthetic report not admissible")
        for name in ("case_count", "exact_case_matches", "finding_labels",
                     "false_positive_flags", "false_negative_flags"):
            if type(observation.get(name)) is not int or not 0 <= observation[name] <= 100:
                raise ValueError("Synthetic count invalid")
        if (observation["case_count"] != 100
                or observation["exact_case_matches"] > observation["case_count"]
                or observation.get("result") not in ("PASS", "HOLD", "FAIL")):
            raise ValueError("Synthetic report inconsistent")
    else:
        raise ValueError("Unsupported probe type")
    return observation


def read_pipeline_receipt(db_path: str, job_id: str) -> dict[str, Any] | None:
    """Return owner-readable evidence when the DB job and digest agree.

    Missing returns None; any corrupted, uncommitted or unsupported result is
    rejected. This never returns a success authority assertion.
    """
    if not _JOB_ID.fullmatch(job_id):
        raise ValueError("Invalid job identifier")
    job = get_job(db_path, job_id)
    if job is None:
        return None
    if job["state"] != "succeeded":
        raise ValueError("Job has no completed receipt")
    result = job.get("result")
    if (not isinstance(result, dict)
            or set(result) != {"observation", "evidence_id"}
            or not isinstance(job.get("evidence_id"), str)
            or result.get("evidence_id") != job["evidence_id"]):
        raise ValueError("Missing or mismatched evidence reference")
    observation = _bounded_observation(result["observation"])
    if job.get("params") != {"probe": observation["probe"]}:
        raise ValueError("Probe/params mismatch")
    digest = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
    conn = get_db(db_path)
    try:
        ev = conn.execute(
            "SELECT capability_id,kind,sha256,integrity_status,verification_status "
            "FROM evidence_records WHERE id=?", (job["evidence_id"],)
        ).fetchone()
    finally:
        conn.close()
    if (ev is None or ev["capability_id"] != "regression_scan"
            or ev["kind"] != "offline_probe" or ev["integrity_status"] != "RECORDED"
            or ev["verification_status"] != "UNVERIFIED"
            or not hmac.compare_digest(str(ev["sha256"]), digest)):
        raise ValueError("Evidence digest or provenance mismatch")
    return {
        "jobId": job_id,
        "state": "succeeded",
        "evidenceId": job["evidence_id"],
        "sha256": digest,
        "observation": observation,
        "integrity": "RECORDED",
        "verification": "NOT VERIFIED",
        "authority": "NONE",
        "release": "HOLD",
    }
