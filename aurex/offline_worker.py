"""Detached, zero-provider canonical worker using existing fencing and evidence."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import time

from aurex.database import DEFAULT_DB_PATH, get_db
from aurex.fenced_worker import claim_job, fail_job, finalize_job
from aurex.offline_probes import execute_probe


def run_once(db_path: str, worker_id: str) -> bool:
    """Execute at most one eligible job; stale owners never finalize or fail it."""
    if os.environ.get("AUREX_ENABLE_OFFLINE_LAB") != "1":
        raise ValueError("Offline execution disabled")
    conn = get_db(db_path)
    try:
        rows = conn.execute(
            "SELECT id FROM jobs WHERE state IN ('queued', 'running') "
            "ORDER BY created_at, id LIMIT 100"
        ).fetchall()
    finally:
        conn.close()
    for row in rows:
        claimed = claim_job(db_path, str(row["id"]), worker_id)
        if claimed is None:
            continue
        token = str(claimed["lease_token"])
        generation = int(claimed["lease_generation"])
        try:
            params = json.loads(claimed["params_json"])
            if claimed["kind"] != "regression_scan":
                raise ValueError("Unsupported kind")
            if params == {"probe": "synthetic_field_audit_v1"}:
                if os.environ.get("AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT") != "1":
                    raise ValueError("Synthetic execution disabled")
            elif params != {"probe": "sqlite_roundtrip_v1"}:
                raise ValueError("Unsupported probe")
            observation = execute_probe(params)
            digest = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
            finalize_job(db_path, str(row["id"]), worker_id, token, generation,
                         observation, digest, f"ev-{secrets.token_hex(12)}")
        except Exception:
            fail_job(db_path, str(row["id"]), worker_id, token, generation)
        return True
    return False


def main() -> None:
    worker_id = f"offline-{secrets.token_hex(12)}"
    while True:
        if not run_once(DEFAULT_DB_PATH, worker_id):
            time.sleep(1)


if __name__ == "__main__":
    main()
