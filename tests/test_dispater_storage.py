"""CCXXI storage guarantees: ephemeral-path rejection, WAL/synchronous, re-init, concurrency, recovery."""

import os
import sqlite3
import threading
from pathlib import Path
from typing import Any

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine

TENANT = "tenant-a"


def _report(job: str = "J1") -> dict[str, Any]:
    data = {
        "tenant_id": TENANT,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": job, "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [
            {"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "100.00"}
        ],
        "invoices": [{"invoice_id": f"I-{job}", "job_id": job, "amount": "150.00", "status": "open"}],
        "payments": [],
    }
    return RevenueLeakageEngine(TENANT).reconcile_records(data)


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "d.db"))
    monkeypatch.delenv("AUREX_DISPATER_REQUIRE_PERSISTENT", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT_NAME", raising=False)


@pytest.mark.parametrize("path", ["/tmp/x/d.db", "/var/tmp/d.db", "/dev/shm/d.db", "/tmp/d.db"])
def test_ephemeral_paths_rejected_when_required(monkeypatch: pytest.MonkeyPatch, path: str) -> None:
    monkeypatch.setenv("AUREX_DISPATER_REQUIRE_PERSISTENT", "1")
    with pytest.raises(dispater_store.StorageUnavailableError):
        dispater_store.validate_storage_mount(path)


def test_symlink_into_tmp_is_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    link = tmp_path / "link"
    link.symlink_to("/tmp")
    monkeypatch.setenv("AUREX_DISPATER_REQUIRE_PERSISTENT", "1")
    with pytest.raises(dispater_store.StorageUnavailableError):
        dispater_store.validate_storage_mount(str(link / "d.db"))


def test_lookalike_directory_is_not_treated_as_tmp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUREX_DISPATER_REQUIRE_PERSISTENT", "1")
    assert not dispater_store._is_ephemeral("/tmpfoo")


def test_railway_runtime_requires_persistence_unless_explicitly_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    assert dispater_store.persistence_required()
    with pytest.raises(dispater_store.StorageUnavailableError):
        dispater_store.validate_storage_mount("/tmp/aurex_dispater.db")
    monkeypatch.setenv("AUREX_DISPATER_REQUIRE_PERSISTENT", "0")
    assert not dispater_store.persistence_required()


def test_connection_is_wal_and_fully_synchronous() -> None:
    conn = dispater_store._connect()
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2  # FULL
    finally:
        conn.close()


def test_replaced_database_file_is_reinitialised(tmp_path: Path) -> None:
    dispater_store.save_run(TENANT, _report())
    for suffix in ("", "-wal", "-shm"):
        Path(str(tmp_path / "d.db") + suffix).unlink(missing_ok=True)
    stored, created = dispater_store.save_run(TENANT, _report())
    assert created
    assert dispater_store.latest_run(TENANT) is not None


def test_restart_recovery_keeps_records() -> None:
    stored, _ = dispater_store.save_run(TENANT, _report())
    assert dispater_store.get_run(TENANT, stored["run_id"]) is not None


@pytest.mark.parametrize("round_no", range(10))
def test_concurrent_writers_all_persist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, round_no: int
) -> None:
    # Fresh database each round: exercises the first-connection schema-creation race.
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / f"r{round_no}.db"))
    errors: list[BaseException] = []

    def work(i: int) -> None:
        try:
            dispater_store.save_run(TENANT, _report(f"J{i}"))
        except BaseException as exc:  # noqa: BLE001 - surfaced via assertion below
            errors.append(exc)

    threads = [threading.Thread(target=work, args=(i,)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(dispater_store.list_runs(TENANT, limit=100)) == 16


def test_duplicate_dataset_is_idempotent() -> None:
    first, created1 = dispater_store.save_run(TENANT, _report())
    second, created2 = dispater_store.save_run(TENANT, _report())
    assert created1 and not created2
    assert first["run_id"] == second["run_id"]


def test_tampered_stored_report_is_detected(tmp_path: Path) -> None:
    stored, _ = dispater_store.save_run(TENANT, _report())
    with sqlite3.connect(tmp_path / "d.db") as conn:
        conn.execute("UPDATE dispater_runs SET report_json = replace(report_json, '150', '151')")
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run(TENANT, stored["run_id"])
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.list_runs(TENANT)


def test_indexed_status_and_dataset_must_match_signed_report(tmp_path: Path) -> None:
    stored, _ = dispater_store.save_run(TENANT, _report())
    with sqlite3.connect(tmp_path / "d.db") as conn:
        conn.execute("UPDATE dispater_runs SET status='TAMPERED'")
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run(TENANT, stored["run_id"])
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.list_runs(TENANT)
    with sqlite3.connect(tmp_path / "d.db") as conn:
        conn.execute("UPDATE dispater_runs SET status='AUDIT_COMPLETE', dataset_sha256='0' * 64")
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.latest_run(TENANT)


def test_corrupt_database_file_fails_loudly_not_silently(tmp_path: Path) -> None:
    (tmp_path / "d.db").write_bytes(b"this is not a sqlite database" * 100)
    with pytest.raises(sqlite3.DatabaseError):
        dispater_store.save_run(TENANT, _report())


def test_backup_and_restore_round_trip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    stored, _ = dispater_store.save_run(TENANT, _report())
    backup = tmp_path / "backup.db"
    with sqlite3.connect(tmp_path / "d.db") as src, sqlite3.connect(backup) as dst:
        src.backup(dst)
    restored = tmp_path / "restored" / "d.db"
    restored.parent.mkdir()
    os.replace(backup, restored)
    monkeypatch.setenv("AUREX_DISPATER_DB", str(restored))
    again = dispater_store.get_run(TENANT, stored["run_id"])
    assert again is not None and again["receipt_sha256"] == stored["receipt_sha256"]
