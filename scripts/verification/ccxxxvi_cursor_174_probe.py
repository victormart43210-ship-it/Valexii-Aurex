"""Offline semantic challenges for Cursor PR #174. Exit 1 means at least one failed gate."""
import json
import subprocess
import sys
from pathlib import Path

SHA = "2d0b62400e0ad40f2780f51b26ba0d09261cd724"
repo = Path.cwd().resolve()
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
if head != SHA or subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "aurex"], cwd=repo).returncode:
    sys.exit("Run in a clean, detached worktree matching pinned PR #174")
sys.path.insert(0, str(repo))
from aurex import dispater_ingest, dispater_intelligence, dispater_monitor

for module in (dispater_ingest, dispater_intelligence, dispater_monitor):
    if Path(module.__file__).resolve().parent.parent != repo:
        sys.exit(f"Wrong source: {module.__file__}")

j = dict(job_id="J", customer_id="C", service_code="tow", date="2026-02-01")
r = dict(rate_id="R", customer_id="C", service_code="tow", start="2026-01-01", end="2026-12-31", amount="100")
i = dict(invoice_id="I", job_id="J", status="open", amount="100")
p = dict(payment_id="P1", invoice_id="I", amount="100")
d = dict(tenant_id="T", dataset_type="SYNTHETIC_ONLY", jobs=[j], rates=[r], invoices=[i], payments=[p, {**p,"payment_id":"P2"}])
cases = []

def check(name, expected, observed):
    cases.append({"check": name, "expected": expected, "observed": observed, "pass": observed == expected})

def parse(raw, kind):
    try:
        result = dispater_ingest.ingest_source("T","batch."+kind,raw,kind=kind)
    except Exception as exc:
        return type(exc).__name__
    dataset = result["dataset"]
    return {"accepted": True, "tenant":dataset["tenant_id"], "class":dataset["dataset_type"], "invoice_amounts":[row["amount"] for row in dataset["invoices"]]}

check("reject_cross_tenant_live_source", "IngestError", parse(json.dumps({**d,"tenant_id":"OTHER","dataset_type":"LIVE"}).encode(),"json"))
check("reject_ambiguous_amount_columns", "IngestError", parse(b"invoices,invoice_id,job_id,amount,amount,status\n,I,J,900,1,open\n","csv"))
check("controlled_short_row_rejection", "IngestError", parse(b"invoices,invoice_id,job_id,amount,status\n,I,J\n","csv"))
check("reject_unsupported_only_table", "IngestError", parse(b'{"deposits":[{"id":"1"}]}',"json"))
check("reject_duplicate_json_keys", "IngestError", parse(b'{"invoices":[{"invoice_id":"I","job_id":"J","amount":"900","amount":"1","status":"open"}]}',"json"))
reconcile = dispater_intelligence.RevenueLeakageEngine("T").reconcile_records
report = reconcile(d)
check("no_point_estimate_when_duplicate_cash_unresolved", "0.00", report["financial_summary"]["identified_exposure_usd"])
check("no_cash_automatically_confirmed", "0.00", report["financial_summary"]["confirmed_recovery_usd"])
unbilled = reconcile({**d,"invoices":[],"payments":[]})["findings"][0]
check("unbilled_dollars_reference_causing_rate_and_job", ["job","rate"], sorted(ev["kind"] for ev in unbilled["evidence"]))
check("monitor_replay_cannot_settle_cash", "0.00", dispater_monitor.monitor_increment("T",d,d)["confirmed_recovery_usd"])
import hashlib
import io
import os
import secrets
import sqlite3
import tempfile

import openpyxl
from aurex import dispater_store

def from_json(dataset):
    blob = json.dumps(dataset).encode()
    return dispater_ingest.ingest_source("T", "records.json", blob, kind="json")["dataset"]

hours = {**d, "rates":[{**r, "unit":"HOUR", "amount":"25"}], "invoices":[], "payments":[],
         "equipment":[dict(ticket_id="E",job_id="J",equipment_id="truck",service_date=j["date"],billable_hours="8",standby_hours="0",invoiced_hours="8")]}
check("direct_hourly_8_times_25", "200.00", reconcile(hours)["financial_summary"]["identified_exposure_usd"])
check("document_hourly_8_times_25", "200.00", reconcile(from_json(hours))["financial_summary"]["identified_exposure_usd"])
reversed_cash = {**d,"invoices":[{**i,"status":"paid"}],"payments":[p,{**p,"payment_id":"X","kind":"REVERSAL","amount":"40"}]}
def mismatch(snapshot):
    finding = next(f for f in reconcile(snapshot)["findings"] if f["code"] == "PAID_STATUS_UNRECONCILED")
    return finding["xaeli_explanation"]["now"]
check("direct_reversal_leaves_60",True,"payments total $60.00" in mismatch(reversed_cash))
check("document_reversal_leaves_60",True,"payments total $60.00" in mismatch(from_json(reversed_cash)))
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title="invoices"
sheet.append(["invoice_id","job_id","amount","amount","status"])
sheet.append(["I","J","999","1","open"])
buffer=io.BytesIO()
workbook.save(buffer)
check("ambiguous_workbook_amounts_rejected","IngestError",parse(buffer.getvalue(),"xlsx"))
with tempfile.TemporaryDirectory() as tmp:
    os.environ.update(AUREX_DISPATER_DB=tmp+"/audit.sqlite", AUREX_DISPATER_REQUIRE_PERSISTENT="0",
                      AUREX_DISPATER_RECEIPT_KEYS=json.dumps({"test":secrets.token_hex(32)}),
                      AUREX_DISPATER_RECEIPT_ACTIVE_KID="test")
    import base64
    from fastapi.testclient import TestClient
    os.environ["AUREX_DB_PATH"]=tmp+"/jobs.sqlite"
    token=secrets.token_hex(32)
    os.environ["AUREX_SERVICE_TOKEN"]=token
    os.environ["AUREX_DISPATER_TENANT_GRANTS"]=json.dumps({hashlib.sha256(token.encode()).hexdigest():["T"]})
    from aurex.api import app
    with TestClient(app) as client:
        headers={"Authorization":"Bearer "+token}
        typed=client.post("/v1/dispater/reconciliation",json=hours,headers=headers)
        typed.raise_for_status()
        check("http_reconciliation_preserves_hours","200.00",typed.json()["financial_summary"]["identified_exposure_usd"])
        document={"tenant_id":"T","filename":"source.json","kind":"json",
                  "content_base64":base64.b64encode(json.dumps(hours).encode()).decode()}
        via_doc=client.post("/v1/dispater/documents",json=document,headers=headers)
        via_doc.raise_for_status()
        check("http_documents_preserves_hourly_rate","200.00",via_doc.json()["report"]["financial_summary"]["identified_exposure_usd"])
    source_sha = hashlib.sha256(b"synthetic").hexdigest()
    base={**d,"jobs":[],"invoices":[],"rates":[],"payments":[]}
    event,created=dispater_monitor.persist_increment("T",base,hours,source_sha)
    repeated,created_again=dispater_monitor.persist_increment("T",base,hours,source_sha)
    check("sqlite_event_reopened_same_id",True,created and not created_again and repeated["event_id"]==event["event_id"])
    with sqlite3.connect(os.environ["AUREX_DISPATER_DB"]) as con:
        con.execute("UPDATE dispater_monitor_events SET payload_json = ?",(json.dumps({"identified_exposure_usd":"999999.00","financial_authority":"GRANTED"}),))
    try:
        altered=dispater_store.get_monitor_event("T",source_sha)
        outcome=altered["payload"]["financial_authority"]
    except dispater_store.IntegrityError:
        outcome="REJECTED"
    check("tampered_monitor_payload_rejected","REJECTED",outcome)
failed=sum(not row["pass"] for row in cases)
print(json.dumps({"candidate_sha":head,"cases":cases,"passed":len(cases)-failed,"failed":failed},indent=2))
sys.exit(int(failed != 0))
