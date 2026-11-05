"""Adversarial tests: keyed receipt authenticity (forgery, tenant swap, keys, legacy)."""

import json
import secrets
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from aurex import dispater_store
from aurex.dispater_intelligence import RevenueLeakageEngine, digest
from aurex.dispater_receipt import ReceiptKeyError, sign_report, verify_mac


def _dataset(tenant: str) -> dict[str, Any]:
    return {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "100.00"}],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "open"}],
        "payments": [],
    }


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "r.db"
    monkeypatch.setenv("AUREX_DISPATER_DB", str(path))
    return path


def _report(tenant: str = "tenant-a") -> dict[str, Any]:
    return RevenueLeakageEngine(tenant).reconcile_records(_dataset(tenant))


def _rewrite(db: Path, mutate: Any, recompute_sha: bool = True) -> None:
    conn = sqlite3.connect(db)
    raw = conn.execute("SELECT report_json FROM dispater_runs").fetchone()[0]
    rep = json.loads(raw)
    mutate(rep)
    if recompute_sha:  # attacker with DB write access recomputes the unkeyed hash
        body = {k: v for k, v in rep.items() if k not in ("receipt_sha256", "receipt_auth", "receipt_mac")}
        rep["receipt_sha256"] = digest(body)
        conn.execute("UPDATE dispater_runs SET receipt_sha256=?", (rep["receipt_sha256"],))
    conn.execute("UPDATE dispater_runs SET report_json=?", (json.dumps(rep),))
    conn.commit()
    conn.close()


def test_roundtrip_signed(db: Path) -> None:
    stored, created = dispater_store.save_run("tenant-a", _report())
    assert created
    assert verify_mac({k: v for k, v in stored.items() if k not in ("run_id", "created_at")})
    assert stored["receipt_auth"]["alg"] == "HMAC-SHA256"
    assert dispater_store.latest_run("tenant-a") is not None


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["financial_summary"].update(identified_exposure_usd="0.00"),
        lambda r: r["findings"][0].update(exposure_usd="1.00"),
        lambda r: r["findings"][0]["evidence"][0].update(record_sha256="0" * 64),
        lambda r: r.update(tenant_id="tenant-b"),
    ],
    ids=["amount", "finding-amount", "source-digest", "tenant"],
)
def test_forged_report_with_recomputed_unkeyed_hash_rejected(db: Path, mutate: Any) -> None:
    dispater_store.save_run("tenant-a", _report())
    _rewrite(db, mutate)
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.latest_run("tenant-a")


def test_stripped_signature_and_unsigned_legacy_rejected(db: Path) -> None:
    dispater_store.save_run("tenant-a", _report())
    _rewrite(db, lambda r: (r.pop("receipt_mac"), r.pop("receipt_auth")))
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.latest_run("tenant-a")


def test_legacy_unsigned_row_not_promoted_by_idempotent_resubmit(db: Path) -> None:
    dispater_store.save_run("tenant-a", _report())
    _rewrite(db, lambda r: (r.pop("receipt_mac"), r.pop("receipt_auth")), recompute_sha=False)
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.save_run("tenant-a", _report())


def test_cross_tenant_substitution_rejected(db: Path) -> None:
    dispater_store.save_run("tenant-a", _report("tenant-a"))
    conn = sqlite3.connect(db)
    conn.execute("UPDATE dispater_runs SET tenant_id='tenant-b'")
    conn.commit()
    conn.close()
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.latest_run("tenant-b")


def test_field_order_does_not_matter_but_content_does() -> None:
    signed = sign_report(_report())
    reordered = dict(reversed(list(signed.items())))
    assert verify_mac(reordered)
    reordered["tenant_id"] = "tenant-x"
    assert not verify_mac(reordered)


def test_unknown_kid_and_wrong_alg_rejected() -> None:
    signed = sign_report(_report())
    assert not verify_mac({**signed, "receipt_auth": {"alg": "HMAC-SHA256", "kid": "nope"}})
    assert not verify_mac({**signed, "receipt_auth": {"alg": "none", "kid": "test-k1"}})
    assert not verify_mac({**signed, "receipt_mac": 123})


def test_verification_without_key_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    signed = sign_report(_report())
    monkeypatch.delenv("AUREX_DISPATER_RECEIPT_KEYS")
    assert not verify_mac(signed)
    with pytest.raises(ReceiptKeyError):
        sign_report(_report())


def test_short_or_malformed_key_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    for bad in (json.dumps({"test-k1": "ab" * 8}), "not-json", json.dumps({"test-k1": "zz"})):
        monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", bad)
        with pytest.raises(ReceiptKeyError):
            sign_report(_report())


def test_wrong_key_cannot_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    signed = sign_report(_report())
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"test-k1": secrets.token_hex(32)}))
    assert not verify_mac(signed)


def test_key_rotation_old_receipts_verify_new_receipts_use_new_kid(monkeypatch: pytest.MonkeyPatch) -> None:
    old_key = secrets.token_hex(32)
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"k1": old_key}))
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "k1")
    old = sign_report(_report())
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"k1": old_key, "k2": secrets.token_hex(32)}))
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_ACTIVE_KID", "k2")
    new = sign_report(_report())
    assert verify_mac(old) and verify_mac(new) and new["receipt_auth"]["kid"] == "k2"
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"k2": secrets.token_hex(32)}))
    assert not verify_mac(old)  # retiring a key invalidates its receipts


def test_save_without_key_fails_closed_and_writes_nothing(db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUREX_DISPATER_RECEIPT_KEYS")
    with pytest.raises(ReceiptKeyError):
        dispater_store.save_run("tenant-a", _report())
    assert not db.exists() or dispater_store.list_runs("tenant-a") == []


def test_replayed_submission_is_idempotent_no_duplicate_effect(db: Path) -> None:
    first, c1 = dispater_store.save_run("tenant-a", _report())
    second, c2 = dispater_store.save_run("tenant-a", _report())
    assert c1 and not c2 and first["run_id"] == second["run_id"]
    assert len(dispater_store.list_runs("tenant-a")) == 1
