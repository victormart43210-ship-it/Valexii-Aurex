"""CCLII controls: anchor key separation, at-rest envelope, lifecycle, and egress."""

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aurex import dispater_store
from aurex.api import app
from aurex.customer_sovereignty import SovereigntyError
from aurex.dispater_anchor import EXTERNAL_ANCHOR, anchor_agrees
from aurex.dispater_at_rest import protect_text, reveal_text
from aurex.dispater_ingest import ingest_source
from aurex.dispater_lifecycle import authorization_decision
from aurex.dispater_monitor import persist_increment
from aurex.egress import connector_destination_allowed
from aurex.web_adapter import WebsiteAdapter

TOKEN_A = "a" * 32


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _dataset() -> dict[str, object]:
    return {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S", "date": "2026-03-01"}],
        "rates": [],
        "invoices": [],
        "payments": [],
    }


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    digest = hashlib.sha256(TOKEN_A.encode()).hexdigest()
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps({digest: ["tenant-a"]}))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "d.db"))
    return TestClient(app, raise_server_exceptions=False)


def test_received_bytes_are_labeled_separately_from_source_identity() -> None:
    raw = b"jobs,job_id,customer_id,service_code,date\njobs,J1,C1,S,2026-03-01\n"
    batch = ingest_source("tenant-a", "jobs.csv", raw, kind="csv")
    assert batch["source_sha256"] == hashlib.sha256(raw).hexdigest()
    assert batch["byte_length"] == len(raw)
    assert batch["source_bytes_status"] == "VERIFIED_RECEIVED_BYTES"
    assert batch["source_identity"] == "UNVERIFIED"


def test_replaying_an_older_source_does_not_move_the_anchor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "chain.db"))
    first = _dataset()
    persist_increment("tenant-a", first, {"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY"}, "aa" * 32)
    second = {
        "tenant_id": "tenant-a",
        "dataset_type": "SYNTHETIC_ONLY",
        "invoices": [{"invoice_id": "I2", "job_id": "MISSING", "amount": "2.00", "status": "open"}],
    }
    persist_increment("tenant-a", first, second, "bb" * 32)
    assert dispater_store.verify_monitor_chain("tenant-a")
    persist_increment("tenant-a", first, {"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY"}, "aa" * 32)
    assert dispater_store.verify_monitor_chain("tenant-a")


def test_anchor_rejects_a_receipt_key_and_a_deleted_sidecar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "chain.db"))
    persist_increment("tenant-a", _dataset(), {"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY"}, "ab" * 32)
    assert dispater_store.verify_monitor_chain("tenant-a")
    assert EXTERNAL_ANCHOR == "NOT_VERIFIED"
    events = dispater_store.list_monitor_events("tenant-a")
    anchor = json.loads((tmp_path / "chain.db.anchor.json").read_text())
    anchor["tenant-a"]["mac"] = "ab" * 32
    (tmp_path / "chain.db.anchor.json").write_text(json.dumps(anchor))
    assert anchor_agrees("tenant-a", events) is False
    assert dispater_store.verify_monitor_chain("tenant-a") is False


def test_deleting_the_anchor_file_fails_and_deleting_both_is_not_detectable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "chain.db"))
    persist_increment("tenant-a", _dataset(), {"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY"}, "cd" * 32)
    (tmp_path / "chain.db.anchor.json").unlink()
    assert dispater_store.verify_monitor_chain("tenant-a") is False
    persist_increment("tenant-a", _dataset(), {"tenant_id": "tenant-a", "dataset_type": "SYNTHETIC_ONLY"}, "ef" * 32)
    # The second call is idempotent on the same source digest, so write a new addition.
    persist_increment(
        "tenant-a",
        _dataset(),
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "invoices": [{"invoice_id": "I9", "job_id": "MISSING", "amount": "1.00", "status": "open"}],
        },
        "11" * 32,
    )
    for name in ("chain.db.anchor.json", "chain.db.monitor-head.json"):
        path = tmp_path / name
        if path.exists():
            path.unlink()
    connection = __import__("sqlite3").connect(tmp_path / "chain.db")
    connection.execute("DELETE FROM dispater_monitor_events")
    connection.commit()
    connection.close()
    assert dispater_store.verify_monitor_chain("tenant-a") is True


def test_report_blob_is_ciphertext_when_a_data_key_is_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = "22" * 32
    monkeypatch.setenv("AUREX_DISPATER_DATA_KEYS", json.dumps({"data-k1": key}))
    monkeypatch.setenv("AUREX_DISPATER_DATA_ACTIVE_KID", "data-k1")
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "enc.db"))
    stored = protect_text('{"schema":"dispater"}')
    assert "dispater" not in stored
    assert reveal_text(stored) == '{"schema":"dispater"}'
    from aurex.dispater_intelligence import RevenueLeakageEngine

    report = RevenueLeakageEngine("tenant-a").reconcile_records(
        {
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [],
            "rates": [],
            "invoices": [],
            "payments": [],
        }
    )
    saved, _created = dispater_store.save_run("tenant-a", report)
    assert saved["financial_summary"]["confirmed_recovery_usd"] == "0.00"
    connection = __import__("sqlite3").connect(tmp_path / "enc.db")
    raw = connection.execute("SELECT report_json FROM dispater_runs").fetchone()[0]
    connection.close()
    assert "confirmed_recovery_usd" not in raw
    monkeypatch.setenv("AUREX_DISPATER_DATA_KEYS", json.dumps({"data-k1": "33" * 32}))
    with pytest.raises(dispater_store.IntegrityError):
        dispater_store.get_run("tenant-a", saved["run_id"])


def test_deletion_request_does_not_delete_and_approval_stays_unverified(client: TestClient) -> None:
    created = client.post(
        "/v1/dispater/reconciliation",
        headers=_headers(TOKEN_A),
        json={
            "tenant_id": "tenant-a",
            "dataset_type": "SYNTHETIC_ONLY",
            "jobs": [],
            "invoices": [],
            "rates": [],
            "payments": [],
        },
    )
    assert created.status_code == 200
    requested = client.post(
        "/v1/dispater/lifecycle/deletion-request",
        headers=_headers(TOKEN_A),
        json={"tenant_id": "tenant-a"},
    )
    assert requested.status_code == 200
    body = requested.json()
    assert body["deletion"] == "NOT_EXECUTED"
    assert body["effect"] == "NONE"
    assert client.get("/v1/dispater/runs?tenant_id=tenant-a", headers=_headers(TOKEN_A)).json()["count"] == 1
    decision = authorization_decision(
        {
            "tenant_id": "tenant-a",
            "actor_id": "person-1",
            "action": "SYNTHETIC_AUDIT_READ",
            "scope": "tenant-a:rows",
            "expires_at": "2026-12-01T00:00:00+00:00",
        }
    )
    assert decision["verification"] == "UNVERIFIED"
    assert decision["effect"] == "NONE"
    assert decision["reason"] == "NO_IDENTITY_PROVIDER"


def test_empty_data_keys_are_not_described_as_encryption(monkeypatch: pytest.MonkeyPatch) -> None:
    from aurex.dispater_at_rest import encryption_status

    monkeypatch.setenv("AUREX_DISPATER_DATA_KEYS", "{}")
    assert encryption_status() == "NOT_CONFIGURED"


def test_the_anchor_key_cannot_reuse_the_receipt_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from aurex.dispater_anchor import AnchorKeyError, require_configured

    shared = "ab" * 32
    monkeypatch.setenv("AUREX_DISPATER_RECEIPT_KEYS", json.dumps({"test-k1": shared}))
    monkeypatch.setenv("AUREX_DISPATER_ANCHOR_KEYS", json.dumps({"anchor-k1": shared}))
    monkeypatch.setenv("AUREX_DISPATER_ANCHOR_ACTIVE_KID", "anchor-k1")
    with pytest.raises(AnchorKeyError):
        require_configured()


def test_unlisted_connector_destination_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUREX_EGRESS_ALLOWLIST", raising=False)
    assert connector_destination_allowed("https://exfil.example.invalid/v1") is False
    adapter = WebsiteAdapter("https://exfil.example.invalid")
    with pytest.raises(SovereigntyError):
        adapter.create_job({"kind": "regression_scan"})
    monkeypatch.setenv("AUREX_EGRESS_ALLOWLIST", "example.local")
    allowed = WebsiteAdapter("http://example.local")
    allowed.base_url = "http://127.0.0.1:9"
    with pytest.raises(SovereigntyError):
        allowed.create_job({"kind": "regression_scan"})
