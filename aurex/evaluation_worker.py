"""Explicitly invoked, zero-cost local evaluation worker.

This is not an HTTP worker registration. It cannot grant authority or call
paid providers. Caller supplies a trusted local responder and database path.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Callable
from uuid import uuid4

from aurex.database import create_job, record_evidence, update_job_state
from aurex.international_eval import Case, run_cases


def execute_local_regression(
    db_path: str,
    cases: tuple[Case, ...],
    responder: Callable[[str], str],
    *,
    max_cases: int = 20,
) -> dict[str, object]:
    """Persist a bounded job, observations, and explicitly unverified evidence.

    A responder is provided by the caller; this function does not create an
    agent, contact a model provider, or accept a browser-supplied executable.
    """
    if not 1 <= max_cases <= 100 or len(cases) > max_cases:
        raise ValueError("Case count exceeds configured limit")
    if not cases or any(len(case.prompt) > 4096 for case in cases):
        raise ValueError("Empty or oversized evaluation")
    job_id = str(uuid4())
    create_job(
        db_path,
        job_id,
        "regression_scan",
        {"case_ids": [case.id for case in cases]},
        reservation_usd=0.0,
        worker_id="explicit-local-evaluation",
    )
    if update_job_state(db_path, job_id, "running") is None:
        raise RuntimeError("Unable to acquire job")
    try:
        observations = run_cases(cases, responder, max_cases=max_cases)
        payload = {
            "job_id": job_id,
            "observations": [asdict(item) for item in observations],
            "verification_status": "UNVERIFIED",
            "authority": "NONE",
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(canonical).hexdigest()
        evidence_id = str(uuid4())
        record_evidence(
            db_path,
            evidence_id,
            "regression_scan",
            "local_evaluation",
            digest,
            "Local evaluation observations; independent verification not performed",
            source_ref=f"job:{job_id}",
            integrity_status="UNKNOWN",
            verification_status="UNVERIFIED",
        )
        if update_job_state(
            db_path,
            job_id,
            "succeeded",
            result=payload,
            evidence_id=evidence_id,
        ) is None:
            raise RuntimeError("Unable to complete job")
        return {"job_id": job_id, "evidence_id": evidence_id, "result": payload}
    except Exception as exc:
        update_job_state(
            db_path,
            job_id,
            "failed",
            error={"kind": type(exc).__name__},
        )
        raise
