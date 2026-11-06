"""Kernel enforcement through the API: recovery claims, evidence independence, quarantine."""

import hashlib
import json
import sqlite3
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aurex import dispater_claims
from aurex.api import app
from aurex.evidence_kernel import Outcome

TA, TB = "a" * 32, "b" * 32


def H(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def sha(tok: str) -> str:
    return hashlib.sha256(tok.encode()).hexdigest()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("AUREX_DISPATER_TENANT_GRANTS", json.dumps({sha(TA): ["tenant-a"], sha(TB): ["tenant-b"]}))
    monkeypatch.setenv("AUREX_DISPATER_DB", str(tmp_path / "c.db"))
    return TestClient(app, raise_server_exceptions=False)


def dataset(tenant: str, amount: str = "150.00") -> dict[str, Any]:
    return {
        "tenant_id": tenant, "dataset_type": "SYNTHETIC_ONLY",
        "jobs": [{"job_id": "J1", "customer_id": "C1", "service_code": "S1", "date": "2026-03-01"}],
        "rates": [{"rate_id": "R1", "customer_id": "C1", "service_code": "S1", "start": "2026-01-01",
                   "end": "2026-12-31", "amount": "100.00"}],
        "invoices": [{"invoice_id": "I1", "job_id": "J1", "amount": amount, "status": "open"}],
        "payments": [],
    }


def ev(system: str, rid: str, content: str = "1", days_old: int = 1, **kw: Any) -> dict[str, Any]:
    return {"source_system": system, "source_record_id": rid,
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "event_time": (datetime.now(UTC) - timedelta(days=days_old)).isoformat(), **kw}


def open_claim(client: TestClient, tok: str = TA, tenant: str = "tenant-a") -> dict[str, Any]:
    run = client.post("/v1/dispater/reconciliation", json=dataset(tenant), headers=H(tok)).json()
    r = client.post("/v1/dispater/claims", headers=H(tok), json={
        "tenant_id": tenant, "run_id": run["run_id"], "finding_id": run["findings"][0]["finding_id"]})
    assert r.status_code == 200, r.text
    return r.json()


def adv(client: TestClient, claim: dict[str, Any], target: str, evidence: list[dict[str, Any]],
        tok: str = TA, tenant: str = "tenant-a", **kw: Any) -> Any:
    return client.post(f"/v1/dispater/claims/{claim['claim_id']}/advance", headers=H(tok),
                       json={"tenant_id": tenant, "target": target, "evidence": evidence, **kw})


def pay(rid: str, **kw: Any) -> dict[str, Any]:
    return ev("bank-feed", rid, days_old=0, **kw)


GOOD = [ev("dispatch-gps", "TRK-1"), ev("customer-rate-sheet", "RS-7")]


def verified(client: TestClient) -> dict[str, Any]:
    c = open_claim(client)
    assert adv(client, c, "VERIFIED_DISCREPANCY", GOOD).status_code == 200
    return c


def test_full_chain_counts_recovery_only_with_independent_payment(client: TestClient) -> None:
    c = verified(client)
    assert adv(client, c, "SUBMITTED_CLAIM", GOOD[:1]).status_code == 200
    assert adv(client, c, "APPROVED_CLAIM", GOOD[:1]).status_code == 200
    assert client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TA)).json()["confirmed_recovered_usd"] == "0"
    own = adv(client, c, "CONFIRMED_RECOVERED", [ev("dispatch-gps", "TRK-1")], received_amount="50.00")
    assert own.status_code == 422 and "already used" in own.text  # claim's own source is not payment proof
    ok = adv(client, c, "CONFIRMED_RECOVERED", [pay("DEP-9")], received_amount="50.00")
    assert ok.status_code == 200 and ok.json()["recovered_amount"] == "50.00"
    s = client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TA)).json()
    assert s["confirmed_recovered_usd"] == "50.00"
    assert [h["to"] for h in ok.json()["history"]][-1] == "CONFIRMED_RECOVERED"
    assert all(h["reviewer"].startswith("principal:") for h in ok.json()["history"])


def test_derived_copies_cannot_verify_discrepancy(client: TestClient) -> None:
    c = open_claim(client)
    copies = [ev("invoice-pdf", "INV-1"),
              ev("ocr", "o1", derived_from=[{"source_system": "invoice-pdf", "source_record_id": "INV-1"}]),
              ev("db", "r1", derived_from=[{"source_system": "ocr", "source_record_id": "o1"}])]
    r = adv(client, c, "VERIFIED_DISCREPANCY", copies)
    assert r.status_code == 422 and "independent" in r.text
    assert client.get(f"/v1/dispater/claims/{c['claim_id']}?tenant_id=tenant-a", headers=H(TA)).json()["state"] == "DETECTED_EXPOSURE"


def test_stale_and_future_evidence_rejected(client: TestClient) -> None:
    c = open_claim(client)
    stale = adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1", days_old=400), ev("b", "2")])
    assert stale.status_code == 422 and "CURRENT" in stale.text
    future = adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1", days_old=-5), ev("b", "2")])
    assert future.status_code == 422


def test_state_bypass_skip_replay_and_reversal(client: TestClient) -> None:
    c = open_claim(client)
    assert adv(client, c, "APPROVED_CLAIM", GOOD).status_code == 422
    assert adv(client, c, "CONFIRMED_RECOVERED", GOOD, received_amount="1").status_code == 422
    assert adv(client, c, "VERIFIED_DISCREPANCY", GOOD).status_code == 200
    assert adv(client, c, "VERIFIED_DISCREPANCY", GOOD).status_code == 422  # replay
    assert adv(client, c, "DETECTED_EXPOSURE", GOOD).status_code == 422  # reversal
    assert adv(client, c, "NOT_A_STATE", GOOD).status_code == 422


def test_recovery_cannot_exceed_claim_or_be_zero(client: TestClient) -> None:
    c = verified(client)
    adv(client, c, "SUBMITTED_CLAIM", GOOD[:1])
    adv(client, c, "APPROVED_CLAIM", GOOD[:1])
    for amt in ("50.01", "0", "-1", "abc", "NaN", "sNaN", "Infinity", "-Infinity", "1e999999", "1E-99999", "0.001"):
        r = adv(client, c, "CONFIRMED_RECOVERED", [pay("D1")], received_amount=amt)
        assert r.status_code == 422 and "after the claim" not in r.text, (amt, r.text)


def test_duplicate_claims_per_obligation_are_idempotent(client: TestClient) -> None:
    a = open_claim(client)
    run2 = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a", "175.00"), headers=H(TA)).json()
    again = client.post("/v1/dispater/claims", headers=H(TA), json={
        "tenant_id": "tenant-a", "run_id": run2["run_id"], "finding_id": run2["findings"][0]["finding_id"]})
    assert again.json()["claim_id"] == a["claim_id"]
    assert client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TA)).json()["count"] == 1


def test_tenant_crossover_denied_everywhere(client: TestClient) -> None:
    c = open_claim(client)
    cid = c["claim_id"]
    assert client.get(f"/v1/dispater/claims/{cid}?tenant_id=tenant-a", headers=H(TB)).status_code == 403
    assert client.get(f"/v1/dispater/claims/{cid}?tenant_id=tenant-b", headers=H(TB)).status_code == 404
    assert adv(client, c, "VERIFIED_DISCREPANCY", GOOD, tok=TB, tenant="tenant-b").status_code == 404
    assert adv(client, c, "VERIFIED_DISCREPANCY", GOOD, tok=TB, tenant="tenant-a").status_code == 403
    assert client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TB)).status_code == 403
    assert client.get("/v1/dispater/quarantine?tenant_id=tenant-a", headers=H(TB)).status_code == 403
    run_a = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a"), headers=H(TA)).json()
    r = client.post("/v1/dispater/claims", headers=H(TB), json={
        "tenant_id": "tenant-b", "run_id": run_a["run_id"], "finding_id": run_a["findings"][0]["finding_id"]})
    assert r.status_code == 404  # another tenant's run id is not resolvable
    assert client.post("/v1/dispater/claims", json={}).status_code == 401


def test_unsigned_state_edit_detected(client: TestClient, tmp_path: Path) -> None:
    c = verified(client)
    conn = sqlite3.connect(tmp_path / "c.db")
    doc = json.loads(conn.execute("SELECT claim_json FROM dispater_claims").fetchone()[0])
    doc["state"] = "CONFIRMED_RECOVERED"
    doc["recovered_amount"] = "150.00"
    conn.execute("UPDATE dispater_claims SET claim_json=?", (json.dumps(doc),))
    conn.commit()
    conn.close()
    assert client.get(f"/v1/dispater/claims/{c['claim_id']}?tenant_id=tenant-a", headers=H(TA)).status_code == 500
    assert client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TA)).status_code == 500


def test_conflicting_evidence_is_quarantined_not_merged(client: TestClient) -> None:
    c = verified(client)
    bad = adv(client, c, "SUBMITTED_CLAIM", [ev("dispatch-gps", "TRK-1", content="DIFFERENT")])
    assert bad.status_code == 409
    q = client.get("/v1/dispater/quarantine?tenant_id=tenant-a", headers=H(TA)).json()
    assert q["count"] == 1 and "conflicting" in q["items"][0]["reason"]
    got = client.get(f"/v1/dispater/claims/{c['claim_id']}?tenant_id=tenant-a", headers=H(TA)).json()
    assert got["state"] == "VERIFIED_DISCREPANCY"  # original evidence and state untouched
    assert client.get("/v1/dispater/quarantine?tenant_id=tenant-b", headers=H(TB)).json()["count"] == 0


def test_quarantine_is_bounded(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dispater_claims, "MAX_QUARANTINE_PER_TENANT", 2)
    c = verified(client)
    for i in range(4):
        assert adv(client, c, "SUBMITTED_CLAIM", [ev("dispatch-gps", "TRK-1", content=f"x{i}")]).status_code == 409
    assert client.get("/v1/dispater/quarantine?tenant_id=tenant-a", headers=H(TA)).json()["count"] == 2


def test_malformed_evidence_and_limits(client: TestClient) -> None:
    c = open_claim(client)
    assert adv(client, c, "VERIFIED_DISCREPANCY", [{"source_system": "x"}]).status_code == 422
    assert adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1", content="z")] * 0).status_code == 422
    too_many = [ev("s", str(i)) for i in range(21)]
    assert adv(client, c, "VERIFIED_DISCREPANCY", too_many).status_code == 422
    bad_time = ev("a", "1")
    bad_time["event_time"] = "not-a-date"
    assert adv(client, c, "VERIFIED_DISCREPANCY", [bad_time, ev("b", "2")]).status_code == 422
    assert client.get("/v1/dispater/claims/clm-nothex?tenant_id=tenant-a", headers=H(TA)).status_code == 422


def test_separator_collision_in_identifiers_rejected(client: TestClient) -> None:
    c = open_claim(client)
    r = adv(client, c, "VERIFIED_DISCREPANCY", [ev("a|b", "c"), ev("a", "b|c")])
    assert r.status_code == 422


def test_cannot_open_claim_without_exposure(client: TestClient) -> None:
    run = client.post("/v1/dispater/reconciliation", json=dataset("tenant-a", "100.00"), headers=H(TA)).json()
    assert run["findings"] == []
    r = client.post("/v1/dispater/claims", headers=H(TA), json={
        "tenant_id": "tenant-a", "run_id": run["run_id"], "finding_id": "FND-none"})
    assert r.status_code == 404


def test_concurrent_advances_apply_exactly_once(client: TestClient) -> None:
    c = open_claim(client)
    codes: list[int] = []

    def go() -> None:
        codes.append(adv(client, c, "VERIFIED_DISCREPANCY", GOOD).status_code)

    ts = [threading.Thread(target=go) for _ in range(6)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert codes.count(200) == 1 and codes.count(422) == 5
    got = client.get(f"/v1/dispater/claims/{c['claim_id']}?tenant_id=tenant-a", headers=H(TA)).json()
    assert len(got["history"]) == 1 and got["version"] == 1


def test_models_have_no_path_to_advance_claims() -> None:
    # The advance API takes no actor field: every transition is attributed to an authenticated principal.
    from aurex.dispater_api import ClaimAdvance

    assert "actor" not in ClaimAdvance.model_fields and "reviewer" not in ClaimAdvance.model_fields
    assert Outcome.CONFIRMED_RECOVERED.value in {o.value for o in Outcome}


def test_claims_fail_closed_without_receipt_keys(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    c = verified(client)
    monkeypatch.delenv("AUREX_DISPATER_RECEIPT_KEYS")
    assert client.get(f"/v1/dispater/claims/{c['claim_id']}?tenant_id=tenant-a", headers=H(TA)).status_code == 500


def _approved(client: TestClient) -> dict[str, Any]:
    c = verified(client)
    adv(client, c, "SUBMITTED_CLAIM", GOOD[:1])
    adv(client, c, "APPROVED_CLAIM", GOOD[:1])
    return c


def test_claim_evidence_cannot_be_reused_as_payment(client: TestClient) -> None:
    c = _approved(client)
    for reused in (GOOD[:1], GOOD[1:]):  # verification and submission-stage evidence alike
        r = adv(client, c, "CONFIRMED_RECOVERED", reused, received_amount="10.00")
        assert r.status_code == 422


def test_payment_dated_before_submission_rejected(client: TestClient) -> None:
    c = _approved(client)
    r = adv(client, c, "CONFIRMED_RECOVERED", [ev("bank-feed", "OLD", days_old=60)], received_amount="10.00")
    assert r.status_code == 422 and "after the claim was submitted" in r.text


def test_one_payment_cannot_confirm_two_claims(client: TestClient) -> None:
    two = dataset("tenant-a")
    two["jobs"].append({"job_id": "J2", "customer_id": "C1", "service_code": "S1", "date": "2026-03-02"})
    two["invoices"].append({"invoice_id": "I2", "job_id": "J2", "amount": "180.00", "status": "open"})
    run = client.post("/v1/dispater/reconciliation", json=two, headers=H(TA)).json()
    assert len(run["findings"]) >= 2
    claims = []
    for f in run["findings"][:2]:
        c = client.post("/v1/dispater/claims", headers=H(TA), json={
            "tenant_id": "tenant-a", "run_id": run["run_id"], "finding_id": f["finding_id"]}).json()
        claims.append(c)
        for i, tgt in enumerate(("VERIFIED_DISCREPANCY", "SUBMITTED_CLAIM", "APPROVED_CLAIM")):
            ok = adv(client, c, tgt, [ev("gps", f"G{f['finding_id']}"), ev("rates", f"R{f['finding_id']}")])
            assert ok.status_code == 200, ok.text
    first = adv(client, claims[0], "CONFIRMED_RECOVERED", [pay("DEP-1")], received_amount="10.00")
    assert first.status_code == 200, first.text
    second = adv(client, claims[1], "CONFIRMED_RECOVERED", [pay("DEP-1")], received_amount="10.00")
    assert second.status_code == 422 and "already applied" in second.text
    assert client.get("/v1/dispater/claims?tenant_id=tenant-a", headers=H(TA)).json()["confirmed_recovered_usd"] == "10.00"


def test_dangling_parent_and_cycle_rejected(client: TestClient) -> None:
    c = open_claim(client)
    ghost = [ev("a", "1", derived_from=[{"source_system": "ghost", "source_record_id": "x"}]), ev("b", "2")]
    assert adv(client, c, "VERIFIED_DISCREPANCY", ghost).status_code == 422
    cyc = [ev("a", "1", derived_from=[{"source_system": "b", "source_record_id": "2"}]),
           ev("b", "2", derived_from=[{"source_system": "a", "source_record_id": "1"}])]
    assert adv(client, c, "VERIFIED_DISCREPANCY", cyc).status_code == 422


def test_cycle_rejected_at_every_step(client: TestClient) -> None:
    c = open_claim(client)
    assert adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1"), ev("b", "2")]).status_code == 200
    cyc = [ev("c", "3", derived_from=[{"source_system": "d", "source_record_id": "4"}]),
           ev("d", "4", derived_from=[{"source_system": "c", "source_record_id": "3"}])]
    assert adv(client, c, "SUBMITTED_CLAIM", cyc).status_code == 422
    assert adv(client, c, "SUBMITTED_CLAIM", [ev("e", "5")]).status_code == 200


def test_conflict_inside_one_submission_quarantined(client: TestClient) -> None:
    c = open_claim(client)
    r = adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1", content="x"), ev("a", "1", content="y"), ev("b", "2")])
    assert r.status_code == 409


def test_oversized_nested_fields_rejected(client: TestClient) -> None:
    c = open_claim(client)
    big = ev("a", "1", derived_from=[{"source_system": "s" * 500, "source_record_id": "r"}])
    assert adv(client, c, "VERIFIED_DISCREPANCY", [big, ev("b", "2")]).status_code == 422
    assert adv(client, c, "VERIFIED_DISCREPANCY", [ev("a", "1", transformations=["t" * 500]), ev("b", "2")]).status_code == 422
