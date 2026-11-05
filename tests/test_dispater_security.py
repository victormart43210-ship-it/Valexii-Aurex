"""Adversarial tests: tenant authorization, durability, integrity, engine correctness."""

import hashlib
import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aurex import dispater_store
from aurex.api import app
from aurex.dispater_intelligence import (
    InvalidSnapshot,
    RevenueLeakageEngine,
    report_to_csv,
    verify_receipt,
)

TOKEN_A = "a" * 32
TOKEN_B = "b" * 32
TOKEN_NONE = "c" * 32


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _sha(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    grants = {_sha(TOKEN_A): ["tenant-a"], _sha(TOKEN_B): ["tenant-b"], _sha(TOKEN_NONE): []}
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps(grants))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "d.db"))
    return TestClient(app, raise_server_exceptions=False)


def dataset(tenant: str, **over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "tenant_id": tenant,
        "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [
            {"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01", "end": "2026-12-31", "amount": "100.00"}
        ],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": "150.00", "status": "open"}],
        "payments": [],
    }
    base.update(over)
    return base


def run(tenant: str, **over: Any) -> dict[str, Any]:
    return RevenueLeakageEngine(tenant).reconcile_records(dataset(tenant, **over))


def codes(report: dict[str, Any]) -> list[str]:
    return [f["code"] for f in report["findings"]]


# ---- engine correctness ----------------------------------------------------


def test_rate_mismatch_classified_overbilling_not_recovery() -> None:
    r = run("t")
    assert codes(r) == ["RATE_MISMATCH"]
    fs = r["financial_summary"]
    assert fs["potential_overbilling_usd"] == "50.00"
    assert fs["potential_underbilling_usd"] == "0.00"
    assert fs["confirmed_recovery_usd"] == "0.00"
    assert fs["human_confirmed_discrepancy_usd"] == "0.00"


def test_underbilling_and_unbilled_are_underbilling() -> None:
    r = run("t", invoices=[{"invoice_id": "I1", "job_id": "J1", "amount": "80.00", "status": "open"}])
    assert r["financial_summary"]["potential_underbilling_usd"] == "20.00"
    r = run("t", invoices=[])
    assert codes(r) == ["UNBILLED_JOB"]
    assert r["financial_summary"]["potential_underbilling_usd"] == "100.00"


def test_clean_control_has_no_findings() -> None:
    r = run("t", invoices=[{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "open"}])
    assert r["findings"] == []
    assert r["financial_summary"]["identified_exposure_usd"] == "0.00"


def test_partial_payment_and_overpayment_and_paid_shortfall() -> None:
    inv = lambda status: [{"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": status}]  # noqa: E731
    pay = lambda amt: [{"payment_id": "P1", "invoice_id": "I1", "amount": amt}]  # noqa: E731
    assert codes(run("t", invoices=inv("open"), payments=pay("40.00"))) == ["PARTIAL_PAYMENT"]
    assert codes(run("t", invoices=inv("open"), payments=pay("120.00"))) == ["OVERPAYMENT"]
    assert codes(run("t", invoices=inv("paid"), payments=pay("60.00"))) == ["PAID_STATUS_UNRECONCILED"]
    assert codes(run("t", invoices=inv("open"), payments=[])) == []


def test_duplicate_invoices_orphans_and_missing_rate() -> None:
    dup = [
        {"invoice_id": "I1", "job_id": "J1", "amount": "100.00", "status": "open"},
        {"invoice_id": "I2", "job_id": "J1", "amount": "100.00", "status": "open"},
        {"invoice_id": "I3", "job_id": "NOPE", "amount": "10.00", "status": "open"},
    ]
    r = run("t", invoices=dup, payments=[{"payment_id": "P1", "invoice_id": "NOPE", "amount": "5.00"}])
    assert set(codes(r)) == {"MULTIPLE_INVOICES", "ORPHAN_INVOICE", "ORPHAN_PAYMENT"}
    assert r["findings"][0]["severity"] == "CRITICAL"  # severity ordering
    r = run("t", rates=[])
    assert "RATE_UNVERIFIED" in codes(r)


def test_conflicting_rates_flagged_unverified() -> None:
    d = dataset("t")
    d["rates"].append({**d["rates"][0], "rate_id": "R2", "amount": "90.00"})
    r = RevenueLeakageEngine("t").reconcile_records(d)
    assert codes(r) == ["AMBIGUOUS_RATE"]


@pytest.mark.parametrize(
    "bad",
    ["1e3", "-5.00", "10.999", "NaN", "", "1" * 12, "$5"],
)
def test_malformed_money_rejected(bad: str) -> None:
    with pytest.raises(InvalidSnapshot):
        run("t", invoices=[{"invoice_id": "I1", "job_id": "J1", "amount": bad, "status": "open"}])


def test_oversized_field_rejected() -> None:
    d = dataset("t")
    d["jobs"][0]["job_id"] = "x" * 1000
    with pytest.raises(InvalidSnapshot):
        RevenueLeakageEngine("t").reconcile_records(d)


def test_repeatable_results() -> None:
    assert run("t") == run("t")


def test_csv_export_neutralizes_formulas() -> None:
    r = run("t", invoices=[{"invoice_id": "=CMD()", "job_id": "J1", "amount": "150.00", "status": "open"}])
    assert "'=CMD()" in report_to_csv(r)
    assert all(not c.startswith("=") for line in report_to_csv(r).splitlines() for c in line.split(","))


# ---- authorization ---------------------------------------------------------


def test_unauthenticated_and_bad_token(client: TestClient) -> None:
    assert client.get("/v1/dispater/dashboard?tenant_id=tenant-a").status_code == 401
    assert client.get("/v1/dispater/dashboard?tenant_id=tenant-a", headers=_h("z" * 32)).status_code == 401


def test_missing_configuration_fails_closed(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.delenv("AUREX_DISPATER_TENANT_GRANTS")
    r = client.get("/v1/dispater/dashboard?tenant_id=tenant-a", headers=_h(TOKEN_A))
    assert r.status_code == 503
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", "{not json")
    assert client.get("/v1/dispater/dashboard?tenant_id=tenant-a", headers=_h(TOKEN_A)).status_code == 503


def test_shared_service_token_grants_nothing(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "s" * 32)
    assert client.get("/v1/dispater/dashboard?tenant_id=tenant-a", headers=_h("s" * 32)).status_code == 401


def test_cross_tenant_read_and_overwrite_blocked(client: TestClient) -> None:
    ra = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A))
    assert ra.status_code == 200
    run_id = ra.json()["run_id"]

    # B cannot read A through any endpoint
    for path in (
        "/v1/dispater/findings?tenant_id=tenant-a",
        "/v1/dispater/dashboard?tenant_id=tenant-a",
        "/v1/dispater/runs?tenant_id=tenant-a",
        f"/v1/dispater/runs/{run_id}?tenant_id=tenant-a",
        f"/v1/dispater/runs/{run_id}/export?tenant_id=tenant-a",
    ):
        assert client.get(path, headers=_h(TOKEN_B)).status_code == 403, path
    # B cannot guess A's run under B's own tenant (uniform 404)
    assert client.get(f"/v1/dispater/runs/{run_id}?tenant_id=tenant-b", headers=_h(TOKEN_B)).status_code == 404
    # Nonexistent and existing tenants give the same denial
    assert client.get("/v1/dispater/findings?tenant_id=ghost", headers=_h(TOKEN_B)).status_code == 403
    # B cannot write into A, and cannot overwrite via body tenant_id
    assert client.post("/v1/dispater/reconciliation", json=dataset("tenant-a", invoices=[]), headers=_h(TOKEN_B)).status_code == 403
    assert client.get("/v1/dispater/findings?tenant_id=tenant-a", headers=_h(TOKEN_A)).json()["run_id"] == run_id
    # Principal with empty grants is denied everywhere
    assert client.get("/v1/dispater/findings?tenant_id=tenant-a", headers=_h(TOKEN_NONE)).status_code == 403


def test_tenant_data_is_isolated_between_valid_tenants(client: TestClient) -> None:
    client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A))
    r = client.get("/v1/dispater/findings?tenant_id=tenant-b", headers=_h(TOKEN_B)).json()
    assert r["status"] == "NO_AUDIT_RUN" and r["count"] == 0


def test_invalid_tenant_and_synthetic_gate(client: TestClient) -> None:
    assert client.get("/v1/dispater/findings?tenant_id=../x", headers=_h(TOKEN_A)).status_code == 422
    bad = dataset("tenant-a", dataset_type="LIVE")
    assert client.post("/v1/dispater/reconciliation", json=bad, headers=_h(TOKEN_A)).status_code == 422


def test_row_limit_and_body_limit(client: TestClient) -> None:
    big = dataset("tenant-a", payments=[{"payment_id": str(i), "invoice_id": "I1", "amount": "1.00"} for i in range(2001)])
    assert client.post("/v1/dispater/reconciliation", json=big, headers=_h(TOKEN_A)).status_code == 422
    h = {**_h(TOKEN_A), "Content-Length": str(10**9)}
    assert client.post("/v1/dispater/reconciliation", content=b"{}", headers=h).status_code in (413, 400)


# ---- persistence, idempotency, integrity ----------------------------------


def test_idempotent_replay(client: TestClient) -> None:
    a = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A)).json()
    b = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A)).json()
    assert a["run_id"] == b["run_id"]
    runs = client.get("/v1/dispater/runs?tenant_id=tenant-a", headers=_h(TOKEN_A)).json()
    assert runs["count"] == 1


def test_restart_recovery(client: TestClient) -> None:
    run_id = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A)).json()["run_id"]
    dispater_store._initialized.clear()  # simulate a fresh process
    r = client.get("/v1/dispater/findings?tenant_id=tenant-a", headers=_h(TOKEN_A)).json()
    assert r["run_id"] == run_id and r["count"] == 1
    assert dispater_store.finding_history("tenant-a", r["findings"][0]["finding_id"])[0]["run_id"] == run_id


def test_evidence_tampering_detected_and_not_leaked(client: TestClient, tmp_path: Path) -> None:
    run_id = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A)).json()["run_id"]
    conn = sqlite3.connect(tmp_path / "d.db")
    row = conn.execute("SELECT report_json FROM dispater_runs").fetchone()
    forged = json.loads(row[0])
    forged["financial_summary"]["identified_exposure_usd"] = "0.00"
    conn.execute("UPDATE dispater_runs SET report_json=?", (json.dumps(forged),))
    conn.commit()
    conn.close()
    res = client.get(f"/v1/dispater/runs/{run_id}?tenant_id=tenant-a", headers=_h(TOKEN_A))
    assert res.status_code == 500
    assert res.json() == {"detail": "Internal DISPATER error"}
    assert not verify_receipt(forged)


def test_report_integrity_and_export(client: TestClient) -> None:
    rep = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A)).json()
    body = {k: v for k, v in rep.items() if k not in ("run_id", "created_at")}
    assert verify_receipt(body)
    tampered = deepcopy(body)
    tampered["findings"][0]["exposure_usd"] = "0.00"
    assert not verify_receipt(tampered)
    csv = client.get(f"/v1/dispater/runs/{rep['run_id']}/export?tenant_id=tenant-a&format=csv", headers=_h(TOKEN_A))
    assert csv.status_code == 200 and csv.text.startswith("finding_id,")


def test_unexpected_errors_are_sanitized(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    def boom(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("secret /var/db path")

    monkeypatch.setattr(dispater_store, "save_run", boom)
    r = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A))
    assert r.status_code == 500 and "secret" not in r.text


def test_purge_is_tenant_scoped(client: TestClient) -> None:
    client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=_h(TOKEN_A))
    client.post("/v1/dispater/reconciliation", json=dataset("tenant-b"), headers=_h(TOKEN_B))
    assert dispater_store.purge_tenant("tenant-a") == 1
    assert client.get("/v1/dispater/runs?tenant_id=tenant-b", headers=_h(TOKEN_B)).json()["count"] == 1


def test_financial_authority_remains_disabled(client: TestClient) -> None:
    d = client.get("/v1/dispater/dashboard?tenant_id=tenant-a", headers=_h(TOKEN_A)).json()
    assert d["system_state"] == {
        "production_release": "HOLD",
        "financial_authority": "NONE",
        "external_paid_inference": "OFF",
    }
    assert d["confirmed_recovery_usd"] == "0.00"
