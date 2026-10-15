"""Real local API/worker failure-path smoke; never a Qwen success demonstration."""

import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        token = secrets.token_hex(32)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        # Hold an unlistening loopback port so this test cannot reach a real model.
        unavailable = socket.socket()
        unavailable.bind(("127.0.0.1", 0))
        model_port = unavailable.getsockname()[1]
        env = {
            **os.environ,
            "AUREX_SERVICE_TOKEN": token,
            "AUREX_DB_PATH": str(Path(directory) / "jobs.db"),
            "AUREX_EXECUTION_ENABLED": "true",
            "AUREX_LOCAL_MODEL": "unavailable-test-target",
            "AUREX_LOCAL_MODEL_URL": f"http://127.0.0.1:{model_port}/v1",
        }
        env.pop("AUREX_ADMIN_TOKEN", None)
        env.pop("AUREX_USER_TOKENS", None)
        processes = []

        def call(path, data=None, authenticated=True):
            req = Request(
                f"http://127.0.0.1:{port}" + path,
                data=None if data is None else json.dumps(data).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Idempotency-Key": "smoke",
                    **({"Authorization": "Bearer " + token} if authenticated else {}),
                },
            )
            try:
                with urlopen(req, timeout=2) as r:
                    return r.status, json.load(r)
            except HTTPError as e:
                return e.code, json.load(e)

        try:
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        "aurex.api:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            for _ in range(50):
                try:
                    if call("/health/live", authenticated=False)[0] == 200:
                        break
                except OSError:
                    pass
                time.sleep(0.1)
            report = {
                "test": "real-process API/worker unavailable-model path",
                "startup": call("/health/live", authenticated=False)[0],
                "unauthenticated": call("/v1/jobs", authenticated=False)[0],
                "ready_without_worker": call("/health/ready", authenticated=False)[0],
            }
            processes.append(
                subprocess.Popen(
                    [sys.executable, "-m", "aurex.worker"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            for _ in range(50):
                if call("/health/ready", authenticated=False)[0] == 200:
                    break
                time.sleep(0.1)
            code, job = call(
                "/v1/jobs",
                {
                    "kind": "local_inference",
                    "params": {
                        "prompt": "Analyze historical security observation versus current security authority."
                    },
                },
            )
            assert code == 200, (code, job)
            for _ in range(100):
                _, current = call("/v1/jobs/" + job["id"])
                if current["state"] in ("failed", "expired"):
                    break
                time.sleep(0.1)
            report.update(
                job_id=job["id"],
                job_state=current["state"],
                result=call("/v1/jobs/" + job["id"] + "/result")[1],
                evidence=call("/v1/jobs/" + job["id"] + "/evidence")[1],
                native_qwen="NOT VERIFIED",
            )
            assert report["unauthenticated"] == 401
            assert report["ready_without_worker"] == 503
            assert current["state"] == "failed"
            assert report["result"]["result"] is None
            assert report["evidence"]["evidence"] == []
            print(json.dumps(report, indent=2))
        finally:
            for p in processes:
                p.terminate()
            for p in processes:
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
            unavailable.close()


if __name__ == "__main__":
    main()
