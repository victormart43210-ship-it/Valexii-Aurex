"""Abrupt-termination durability: SIGKILL mid-write must leave a consistent, verifiable store."""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from aurex import dispater_store

WRITER = """
import sys
from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine
i = 0
while True:
    ds = {"tenant_id":"t","dataset_type":"SYNTHETIC_ONLY","jobs":[{"job_id":f"J{i}","customer_id":"C","service_code":"S","date":"2026-03-01"}],
          "rates":[{"rate_id":"R","customer_id":"C","service_code":"S","start":"2026-01-01","end":"2026-12-31","amount":"10.00"}],
          "invoices":[],"payments":[]}
    dispater_store.save_run("t", RevenueLeakageEngine("t").reconcile_records(ds))
    print(i, flush=True)
    i += 1
"""


def test_sigkill_mid_write_recovers_with_acknowledged_runs_intact(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    db = tmp_path / "crash.db"
    env = {**os.environ, "AUREX_DISPATER_DB": str(db)}
    proc = subprocess.Popen([sys.executable, "-c", WRITER], env=env, stdout=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    acked = 0
    deadline = time.time() + 30
    while acked < 5 and time.time() < deadline:
        if proc.stdout.readline().strip():
            acked += 1
    proc.send_signal(signal.SIGKILL)
    proc.wait()
    assert acked >= 5
    monkeypatch.setenv("AUREX_DISPATER_DB", str(db))
    runs = dispater_store.list_runs("t", limit=200)
    assert len(runs) >= acked  # every acknowledged write survived
    for r in runs:
        assert dispater_store.get_run("t", r["run_id"]) is not None  # each verifies (hash + MAC)
    json.dumps(runs)
