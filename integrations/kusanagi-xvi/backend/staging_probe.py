"""Opt-in restart persistence proof for Railway *staging* only.

One fixed, zero-cost local SQLite round-trip, no network, model, customer data
or payment. It runs before the observer/API/worker processes start so that the
first and subsequent boots use the same deterministic idempotency key.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from . import store

_IDEMPOTENCY_KEY = "staging-persistence-lab-v1"
_PARAMS = {"probe": "sqlite_roundtrip_v1"}
_EXPECTED_SHA = hashlib.sha256(b"aurex-offline-roundtrip-v1").hexdigest()


def permitted(environ: dict[str, str]) -> bool:
    return (
        environ.get("RAILWAY_ENVIRONMENT_NAME") == "aurex-staging"
        and environ.get("AUREX_STAGING_PERSISTENCE_PROBE") == "true"
        and environ.get("AUREX_REQUIRED_VOLUME") == "true"
        and environ.get("AUREX_LLM_ENABLED", "false") == "false"
        and environ.get("AUREX_LLM_ALLOW_BILLING", "false") == "false"
    )


def run(path: str, environ: dict[str, str] | None = None) -> dict[str, Any]:
    env = dict(os.environ) if environ is None else environ
    if not permitted(env):
        raise ValueError("Staging persistence probe requires explicit isolated staging gates")
    store.initialize(path)
    with store.connect(path) as conn:
        prior = conn.execute(
            "SELECT id,state FROM jobs WHERE idempotency_key=?", (_IDEMPOTENCY_KEY,)
        ).fetchone()
    prior_found = prior is not None
    job = store.create_job(path, "regression_scan", _PARAMS, _IDEMPOTENCY_KEY)
    if job["state"] == "queued":
        claimed = store.claim(path, "staging-boot-persistence-proof")
        if not claimed or claimed["id"] != job["id"]:
            raise RuntimeError("Staging proof job was not exclusively claimed")
        job = store.finalize(path, claimed, "staging-boot-persistence-proof")
    if job["state"] != "succeeded":
        raise RuntimeError("Staging persisted job is not completed")
    with store.connect(path) as conn:
        evidence = conn.execute(
            "SELECT sha256,kind,summary FROM evidence WHERE job_id=?",
            (job["id"],),
        ).fetchone()
        result = conn.execute(
            "SELECT result_json,lease_token FROM jobs WHERE id=?",
            (job["id"],),
        ).fetchone()
    if (not evidence or evidence["sha256"] != _EXPECTED_SHA
            or evidence["kind"] != "offline_probe"
            or not result or result["lease_token"] is not None
            or json.loads(result["result_json"]) != {
                "sha256": _EXPECTED_SHA,
                "independentVerification": "NOT VERIFIED",
            }):
        raise RuntimeError("Staging persistent evidence failed integrity check")
    return {
        "status": "STAGING_PERSISTENCE_CHECK_PASS",
        "previousBootRecordPresent": prior_found,
        "observationCount": 1,
        "evidenceDigestMatched": True,
        "authority": "NONE",
        "verification": "NOT VERIFIED",
        "paidInference": "DISABLED",
    }
