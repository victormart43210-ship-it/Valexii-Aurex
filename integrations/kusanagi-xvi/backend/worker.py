"""Bounded opt-in Unix worker: one SQLite roundtrip per fenced lease.

No shell execution, external network, model calls, customer records or payment.
All failed claimed tasks are atomically demoted; stale workers cannot revive jobs.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sqlite3
import time

from . import store


def once(worker_id: str | None = None, db_path: str | None = None) -> dict[str, object]:
    if os.getenv("AUREX_ENABLE_OFFLINE_LAB") != "true":
        return {"status": "HOLD", "reason": "OFFLINE_LAB_DISABLED", "authority": "NONE"}
    path = db_path or store.path_from_env()
    store.initialize(path)
    identity = worker_id or f"unix-{os.getpid()}-{secrets.token_hex(6)}"
    store.heartbeat(path, identity)
    claimed = store.claim(path, identity)
    if not claimed:
        return {"status": "IDLE", "worker": "present", "authority": "NONE"}

    try:
        result = store.finalize(path, claimed, identity)
    except (ValueError, RuntimeError, sqlite3.Error, TypeError, KeyError):
        # A real storage error in fail_claim must propagate and terminate the
        # worker; the supervisor then restarts the whole service fail-closed.
        failed = store.fail_claim(path, claimed, identity)
        return {
            "status": "FAILED" if failed else "HOLD",
            "jobState": "failed" if failed else "LEASE_NOT_OWNED",
            "authority": "NONE",
            "independentVerification": "NOT VERIFIED",
        }
    return {
        "status": "EXECUTED",
        "jobId": result["id"],
        "jobState": result["state"],
        "independentVerification": "NOT VERIFIED",
        "authority": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Default-off deterministic SQLite lab worker")
    parser.add_argument("mode", choices=("once", "loop"))
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()
    if args.interval < 2 or args.interval > 60:
        parser.error("interval must be 2..60 seconds")
    # Stable identity across a Unix worker process's lifetime, distinct across
    # restarts even if the PID is recycled.
    identity = f"unix-{os.getpid()}-{secrets.token_hex(6)}"
    if args.mode == "once":
        print(json.dumps(once(worker_id=identity), sort_keys=True))
        return
    while True:
        print(json.dumps(once(worker_id=identity), sort_keys=True), flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
