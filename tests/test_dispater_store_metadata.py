"""Synthetic adversarial coverage for authenticated storage metadata and read views."""

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine, verify_receipt
from aurex.dispater_receipt import verify_mac


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "metadata.db"
    monkeypatch.setenv("AUREX_DISPATER_DB", str(path))
    monkeypatch.setenv("AUREX_DISPATER_REQUIRE_PERSISTENT", "0")
    return path


def _report(job: str = "J1") -> dict[str, Any]:
    return RevenueLeakageEngine("tenant-a").reconcile_records({
        "tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": job, "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01",
                   "end": "2026-12-31", "amount": "100.00"}],
        "invoices": [{"invoice_id": f"I-{job}", "job_id": job, "amount": "150.00", "status": "open"}],
        "payments": [],
    })


@pytest.mark.parametrize("field,value", [
    ("dataset_sha256", "0" * 64), ("status", "FORGED"),
    ("run_id", "run-forged"), ("created_at", "2099-01-01T00:00:00+00:00"),
    ("tenant_id", "tenant-b"), ("receipt_sha256", "0" * 64),
])
def test_metadata_edits_fail_closed(db: Path, field: str, value: str) -> None:
    saved, _ = dispater_store.save_run("tenant-a", _report())
    with sqlite3.connect(db) as conn:
        conn.execute(f"UPDATE dispater_runs SET {field}=?", (value,))
    tenant = value if field == "tenant_id" else "tenant-a"
    run = value if field == "run_id" else saved["run_id"]
    for read in (
        lambda: dispater_store.get_run(tenant, run),
        lambda: dispater_store.latest_run(tenant),
        lambda: dispater_store.list_runs(tenant),
        lambda: dispater_store.finding_history(tenant, saved["findings"][0]["finding_id"]),
    ):
        with pytest.raises(dispater_store.IntegrityError):
            read()


@pytest.mark.parametrize("target,new_time", [(0, "2099-01-01T00:00:00+00:00"), (1, "1900-01-01T00:00:00+00:00")])
def test_latest_and_limited_list_verify_before_selecting(db: Path, target: int, new_time: str) -> None:
    runs = [dispater_store.save_run("tenant-a", _report(job))[0] for job in ("J1", "J2")]
    assert dispater_store.latest_run("tenant-a") == runs[1]
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE dispater_runs SET created_at=? WHERE run_id=?", (new_time, runs[target]["run_id"]))
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.latest_run("tenant-a")
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.list_runs("tenant-a", limit=1)


@pytest.mark.parametrize("mutation", ["edit", "delete", "insert"])
def test_history_uses_report_not_mutable_finding_cache(db: Path, mutation: str) -> None:
    saved, _ = dispater_store.save_run("tenant-a", _report())
    finding = saved["findings"][0]
    expected = [{"run_id": saved["run_id"], **{key: finding[key] for key in (
        "finding_sha256", "severity", "exposure_usd"
    )}}]
    with sqlite3.connect(db) as conn:
        if mutation == "edit":
            conn.execute("UPDATE dispater_findings SET exposure_usd='999999', severity='FORGED', finding_sha256='forged'")
        elif mutation == "delete":
            conn.execute("DELETE FROM dispater_findings")
        else:
            conn.execute("INSERT INTO dispater_findings VALUES (?,?,?,?,?,?,?)",
                         (saved["run_id"], "tenant-a", "fake-finding", "fake-hash", "FAKE", "CRITICAL", "999999"))
    assert dispater_store.finding_history("tenant-a", finding["finding_id"]) == expected
    assert dispater_store.finding_history("tenant-a", "fake-finding") == []
    assert dispater_store.finding_history("tenant-b", finding["finding_id"]) == []


@pytest.mark.parametrize("legacy", [True, False])
def test_missing_or_forged_storage_receipt_rejected(db: Path, legacy: bool) -> None:
    report = _report()
    dispater_store.save_run("tenant-a", report)
    with sqlite3.connect(db) as conn:
        envelope = json.loads(conn.execute("SELECT source_refs_json FROM dispater_runs").fetchone()[0])
        if legacy:
            envelope = envelope["source_refs"]
        else:
            envelope["storage_receipt"]["created_at"] = "2099-01-01T00:00:00+00:00"
            conn.execute("UPDATE dispater_runs SET created_at=?", (envelope["storage_receipt"]["created_at"],))
        conn.execute("UPDATE dispater_runs SET source_refs_json=?", (json.dumps(envelope),))
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.save_run("tenant-a", report)
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.list_runs("tenant-a")


def test_engine_receipt_and_public_contract_unchanged(db: Path) -> None:
    original = _report()
    saved, created = dispater_store.save_run("tenant-a", original)
    assert created
    body = {key: value for key, value in saved.items() if key not in ("run_id", "created_at")}
    assert verify_receipt(body) and verify_mac(body)
    assert body["receipt_sha256"] == original["receipt_sha256"]
    assert dispater_store.save_run("tenant-a", original) == (saved, False)
    fields = ("run_id", "dataset_sha256", "receipt_sha256", "status", "created_at")
    assert dispater_store.list_runs("tenant-a") == [{key: saved[key] for key in fields}]
