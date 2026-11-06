"""Receipt v2: signed run identity/time, legacy compatibility, substitution and downgrade attacks."""

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine
from aurex.dispater_receipt import receipt_version, sign_report, sign_report_v2, verify_mac

KEY1 = "11" * 32
KEY2 = "22" * 32


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"k1": KEY1, "k2": KEY2}))
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "k1")
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "v2.db"))


def report(tenant: str = "tenant-a", amount: str = "150.00") -> dict[str, Any]:
    data: dict[str, Any] = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01",
                   "end": "2026-12-31", "amount": "100.00"}],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": amount, "status": "open"}],
        "payments": [],
    }
    return RevenueLeakageEngine(tenant).reconcile_records(data)


def test_new_runs_are_v2_and_fully_authenticated() -> None:
    stored, _ = dispater_store.save_run("tenant-a", report())
    assert receipt_version(stored) == 2 and verify_mac(stored)
    assert "unauthenticated_fields" not in stored


def test_modified_run_id_or_timestamp_fails() -> None:
    stored, _ = dispater_store.save_run("tenant-a", report())
    assert not verify_mac({**stored, "run_id": "run-" + "0" * 32})
    assert not verify_mac({**stored, "created_at": "2020-01-01T00:00:00+00:00"})


def test_downgrade_to_legacy_marker_fails() -> None:
    stored, _ = dispater_store.save_run("tenant-a", report())
    legacy_like = {**stored, "receipt_auth": {"alg": "HMAC-SHA256", "kid": "k1"}}
    assert not verify_mac(legacy_like)


def test_cross_run_substitution_rejected_by_store(tmp_path: Path) -> None:
    a, _ = dispater_store.save_run("tenant-a", report(amount="150.00"))
    b, _ = dispater_store.save_run("tenant-a", report(amount="175.00"))
    conn = sqlite3.connect(tmp_path / "v2.db")
    # Put run A's perfectly valid signed report into run B's row.
    conn.execute("UPDATE dispater_runs SET report_json=?, receipt_sha256=? WHERE run_id=?",
                 (json.dumps(a, sort_keys=True), a["receipt_sha256"], b["run_id"]))
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run("tenant-a", b["run_id"])


def test_row_timestamp_edit_rejected(tmp_path: Path) -> None:
    a, _ = dispater_store.save_run("tenant-a", report())
    conn = sqlite3.connect(tmp_path / "v2.db")
    conn.execute("UPDATE dispater_runs SET created_at='2020-01-01T00:00:00+00:00'")
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run("tenant-a", a["run_id"])


def test_cross_tenant_receipt_reuse_rejected(tmp_path: Path) -> None:
    a, _ = dispater_store.save_run("tenant-a", report())
    conn = sqlite3.connect(tmp_path / "v2.db")
    conn.execute("UPDATE dispater_runs SET tenant_id='tenant-b'")
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run("tenant-b", a["run_id"])


def _insert_legacy(tmp_path: Path, tenant: str = "tenant-a") -> str:
    """Write a row exactly as the pre-v2 code did."""
    legacy = sign_report(report(tenant))
    run_id = "run-" + "a" * 32
    with dispater_store._connect() as conn:
        conn.execute("INSERT INTO dispater_runs VALUES (?,?,?,?,?,?,?,?)",
                     (run_id, tenant, legacy["dataset_sha256"], legacy["receipt_sha256"], legacy["status"],
                      "2026-11-01T00:00:00+00:00", json.dumps(legacy, sort_keys=True), "[]"))
    return run_id


def test_legacy_receipts_still_verify_but_metadata_is_untrusted(tmp_path: Path) -> None:
    run_id = _insert_legacy(tmp_path)
    got = dispater_store.get_run("tenant-a", run_id)
    assert got is not None and receipt_version(got) == 1
    assert got["unauthenticated_fields"] == ["run_id", "created_at"]


def test_legacy_body_tamper_still_detected(tmp_path: Path) -> None:
    run_id = _insert_legacy(tmp_path)
    conn = sqlite3.connect(tmp_path / "v2.db")
    rpt = json.loads(conn.execute("SELECT report_json FROM dispater_runs").fetchone()[0])
    rpt["status"] = "X"
    conn.execute("UPDATE dispater_runs SET report_json=?", (json.dumps(rpt),))
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run("tenant-a", run_id)


def test_key_rotation_and_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    stored, _ = dispater_store.save_run("tenant-a", report())
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "k2")
    assert verify_mac(stored)  # old kid still verifies after rotation
    newer = sign_report_v2(report("tenant-a"), run_id="run-" + "b" * 32, created_at="2026-11-06T00:00:00+00:00")
    assert newer["receipt_auth"]["kid"] == "k2" and verify_mac(newer)
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"k2": KEY2}))
    assert not verify_mac(stored)  # k1 retired: fail closed
    monkeypatch.delenv("AUREX_DISPATER_RECEIPT_KEYS")
    assert not verify_mac(newer)
