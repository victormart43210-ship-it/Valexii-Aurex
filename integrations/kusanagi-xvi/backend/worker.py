"""One-shot bounded offline worker, isolated from HTTP and without AI calls."""
from __future__ import annotations
import argparse
import json
import os
import socket
import time
try:
    from . import store
except ImportError:
    import store


def once(worker_id: str | None = None, db_path: str | None = None) -> dict[str, object]:
    path = db_path or store.path_from_env()
    if os.getenv("AUREX_ENABLE_OFFLINE_LAB", "").lower() != "true":
        return {"status":"HOLD", "reason":"offline lab disabled"}
    store.initialize(path)
    worker_id = worker_id or f"local-{os.getpid()}"
    store.heartbeat(path,worker_id)
    claimed=store.claim(path,worker_id)
    if not claimed:
        return {"status":"IDLE", "worker":"present", "authority":"NONE"}
    result=store.finalize(path,claimed,worker_id)
    return {"status":"EXECUTED", "jobId":result["id"], "jobState":result["state"],
            "independentVerification":"NOT VERIFIED", "authority":"NONE"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["once","loop"])
    p.add_argument("--interval",type=int,default=10)
    args=p.parse_args()
    if args.mode=="once":
        print(json.dumps(once(),sort_keys=True))
    else:
        if args.interval < 2 or args.interval > 60:
            p.error("interval must be between 2 and 60 seconds")
        while True:
            print(json.dumps(once(),sort_keys=True),flush=True)
            time.sleep(args.interval)

if __name__=="__main__":
    main()
