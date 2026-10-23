"""Exercise the actual Railway entrypoint in a clean Python process."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PARENT = ROOT / "integrations" / "kusanagi-xvi"


def test_actual_entrypoint_financial_receipt_and_restart(tmp_path):
    env = {k: v for k, v in os.environ.items() if k not in (
        "AUREX_ADMIN_TOKEN", "ALL_PROXY", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY")}
    env.update(PYTHONPATH=f"{ROOT}:{BACKEND_PARENT}", AUREX_SERVICE_TOKEN="x" * 40,
               AUREX_DB_PATH=str(tmp_path / "canonical.sqlite3"),
               AUREX_CANONICAL_STAGING="1", RAILWAY_ENVIRONMENT_NAME="aurex-staging",
               AUREX_ENABLE_OFFLINE_LAB="1", AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT="1",
               AUREX_JOB_EXECUTION_MODE="queued", AUREX_LLM_ENABLED="false",
               AUREX_LLM_ALLOW_BILLING="false")
    script = '''
import json, os
from fastapi.testclient import TestClient
from backend.app import app
from aurex.offline_worker import run_once
from scripts.cxxxi_receipt_verify import verify_receipt
headers={"Authorization":"Bearer "+"x"*40,"Idempotency-Key":"cxxxii-fixed-fixture-001"}
with TestClient(app) as client:
    assert client.get("/v1/health").status_code == 401
    body={"kind":"regression_scan","params":{"probe":"synthetic_field_audit_v1"},"maxCostUsd":0}
    response=client.post("/v1/jobs",headers=headers,json=body)
    assert response.status_code==200, response.text
    job=response.json()
    if job["state"]=="queued":
        assert run_once(os.environ["AUREX_DB_PATH"],"actual-entrypoint-worker")
    receipt=client.get("/v1/jobs/"+job["id"]+"/receipt",headers=headers)
    assert receipt.status_code==200, receipt.text
    checked=verify_receipt(receipt.json(),expected_job_id=job["id"])
    assert checked["digest_consistency"]=="PASS"
    assert receipt.json()["observation"]["exact_case_matches"]==100
    print(json.dumps(receipt.json(),sort_keys=True))
'''
    first = subprocess.run([sys.executable, "-c", script], env=env, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    second = subprocess.run([sys.executable, "-c", script], env=env, text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout


def test_legacy_schema_rejected_without_mutation(tmp_path):
    import hashlib
    import sqlite3

    import pytest

    from aurex.staging_runtime import initialize_canonical

    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE jobs(id TEXT PRIMARY KEY, params TEXT)")
        conn.execute("INSERT INTO jobs VALUES('old', '{}')")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="Legacy jobs"):
        initialize_canonical(str(path))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_staging_configuration_refuses_production_and_paid_execution(tmp_path):
    import pytest

    from aurex.staging_runtime import validate_environment

    env = dict(RAILWAY_ENVIRONMENT_NAME="aurex-staging", AUREX_JOB_EXECUTION_MODE="queued",
               AUREX_ENABLE_OFFLINE_LAB="1", AUREX_SERVICE_TOKEN="x" * 40,
               AUREX_DB_PATH=str(tmp_path / "fresh.sqlite3"))
    assert validate_environment(env) == env["AUREX_DB_PATH"]
    for key, value in (("RAILWAY_ENVIRONMENT_NAME", "production"),
                       ("AUREX_LLM_ENABLED", "true"), ("AUREX_LLM_ALLOW_BILLING", "true"),
                       ("AUREX_OBSERVER_ENABLED", "true"), ("AUREX_JOB_EXECUTION_MODE", "inline"),
                       ("AUREX_DB_PATH", "/data/aurex.sqlite3"), ("AUREX_SERVICE_TOKEN", "")):
        with pytest.raises(ValueError):
            validate_environment({**env, key: value})


def test_supervised_http_worker_persistence_and_child_failure(tmp_path):
    import json
    import signal
    import socket
    import time

    import httpx

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ)
    for key in ("AUREX_ADMIN_TOKEN", "RAILWAY_PROJECT_ID"):
        env.pop(key, None)
    env.update(PYTHONPATH=f"{ROOT}:{BACKEND_PARENT}", AUREX_SERVICE_TOKEN="z" * 40,
               AUREX_DB_PATH=str(tmp_path / "supervised.sqlite3"), PORT=str(port),
               AUREX_CANONICAL_STAGING="1", RAILWAY_ENVIRONMENT_NAME="aurex-staging",
               AUREX_ENABLE_OFFLINE_LAB="1", AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT="1",
               AUREX_JOB_EXECUTION_MODE="queued", AUREX_LLM_ENABLED="false",
               AUREX_LLM_ALLOW_BILLING="false", AUREX_OBSERVER_ENABLED="false",
               AUREX_REQUIRED_VOLUME="false", AUREX_STAGING_PERSISTENCE_PROBE="false")
    headers = {"Authorization": "Bearer " + "z" * 40, "Idempotency-Key": "supervised-financial-001"}
    saved = None
    for restart in range(2):
        with (tmp_path / f"supervisor-{restart}.log").open("w") as log:
            # Test-only launcher records the child handle without requiring /proc.
            launcher = (
                "import subprocess,runpy,pathlib;"
                "original=subprocess.Popen\n"
                "def record(*args,**kwargs):\n"
                " p=original(*args,**kwargs)\n"
                f" if 'aurex.offline_worker' in args[0]: pathlib.Path({str(tmp_path / 'worker.pid')!r}).write_text(str(p.pid))\n"
                " return p\n"
                "subprocess.Popen=record\n"
                "runpy.run_module('backend.supervisor',run_name='__main__')"
            )
            proc = subprocess.Popen([sys.executable, "-c", launcher],
                                    env=env, stdout=log, stderr=log)
            try:
                with httpx.Client(base_url=f"http://127.0.0.1:{port}", trust_env=False,
                                  timeout=2, headers=headers) as client:
                    deadline = time.monotonic() + 12
                    while True:
                        assert proc.poll() is None, (tmp_path / f"supervisor-{restart}.log").read_text()
                        try:
                            if client.get("/v1/health").status_code == 200:
                                break
                        except httpx.TransportError:
                            pass
                        assert time.monotonic() < deadline
                        time.sleep(.1)
                    response = client.post("/v1/jobs", json={"kind": "regression_scan",
                        "params": {"probe": "synthetic_field_audit_v1"}, "maxCostUsd": 0})
                    assert response.status_code == 200, response.text
                    job_id = response.json()["id"]
                    while True:
                        receipt = client.get(f"/v1/jobs/{job_id}/receipt")
                        if receipt.status_code == 200:
                            break
                        assert receipt.status_code == 409, receipt.text
                        assert time.monotonic() < deadline
                        time.sleep(.1)
                    data = receipt.json()
                    assert data["observation"]["exact_case_matches"] == 100
                    from scripts.cxxxi_receipt_verify import verify_receipt
                    assert verify_receipt(data, expected_job_id=job_id)["digest_consistency"] == "PASS"
                    if saved is not None:
                        assert data == saved
                    saved = data
                    if restart:
                        worker_pid = int((tmp_path / "worker.pid").read_text())
                        os.kill(worker_pid, signal.SIGKILL)
                        assert proc.wait(timeout=12) == 1
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=12)
    (tmp_path / "receipt.json").write_text(json.dumps(saved, sort_keys=True))
