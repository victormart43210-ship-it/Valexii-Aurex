import json
import os
import sqlite3
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Barrier, Thread

from fastapi.testclient import TestClient

from aurex import api
from aurex import database as d
from aurex.worker import execute_claim


def run():
    out = {}
    with tempfile.TemporaryDirectory() as t:
        db = str(Path(t) / "jobs.db")
        api.DEFAULT_DB_PATH = db
        os.environ["AUREX_SERVICE_TOKEN"] = "s" * 40
        os.environ["AUREX_USER_TOKENS"] = json.dumps({"alice": "a" * 40, "bob": "b" * 40})
        os.environ["AUREX_EXECUTION_ENABLED"] = "true"
        a = {"Authorization": "Bearer " + "a" * 40}
        b = {"Authorization": "Bearer " + "b" * 40}
        d.create_job(db, "race", "local_inference", {"prompt": "test"}, owner_id="alice")
        barrier = Barrier(12)

        def acquire(i):
            barrier.wait()
            return d.claim_job(db, f"w{i}")

        with ThreadPoolExecutor(max_workers=12) as p:
            leases = list(p.map(acquire, range(12)))
        first = next(x for x in leases if x)
        out["single_worker_acquisition"] = sum(x is not None for x in leases) == 1
        with sqlite3.connect(db) as c:
            c.execute("UPDATE jobs SET lease_until=?", (time.time() - 1,))
        second = d.claim_job(db, "new")
        out["stale_worker_fenced"] = not d.finish_job(
            db, "race", first["worker_id"], first["fence"], {"text": "stale"}
        )
        d.finish_job(db, "race", "new", second["fence"], {"text": "genuine fixture"})
        with TestClient(api.app, raise_server_exceptions=False) as client:
            out["cross_owner_http"] = client.get("/v1/jobs/race/result", headers=b).status_code
            out["invalid_auth_http"] = client.get(
                "/v1/jobs", headers={"Authorization": "Bearer wrong"}
            ).status_code
            with sqlite3.connect(db) as c:
                c.execute(
                    "UPDATE jobs SET result_json=? WHERE id=?",
                    (json.dumps({"text": "tampered"}), "race"),
                )
            out["tampered_evidence_http"] = client.get("/v1/jobs/race/evidence", headers=a).json()
            result = client.get("/v1/jobs/race/result", headers=a)
            out["tampered_result_http"] = {"status": result.status_code, "body": result.json()}
            d.register_worker(db, "ready-fixture", model_configured=False)
            os.environ["AUREX_USER_TOKENS"] = "invalid-json"
            out["readiness_invalid_auth_config"] = {
                "ready": client.get("/health/ready").status_code,
                "actual_auth": client.get("/v1/jobs", headers=a).status_code,
            }
        os.environ["AUREX_USER_TOKENS"] = "{}"
        d.create_job(db, "unicode", "local_inference", {"prompt": "test"})
        claim = d.claim_job(db, "unicode-worker")

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                body = json.dumps(
                    {"model": "fixture", "choices": [{"message": {"content": "界" * 15000}}]}
                ).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            try:
                out["unicode_worker_return"] = execute_claim(
                    db,
                    "unicode-worker",
                    claim,
                    f"http://127.0.0.1:{server.server_port}/v1",
                    "fixture",
                )
            except Exception as e:
                out["unicode_worker_exception"] = type(e).__name__ + ": " + str(e)
            out["unicode_worker_state"] = d.get_job(db, "unicode")["state"]
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    run()
