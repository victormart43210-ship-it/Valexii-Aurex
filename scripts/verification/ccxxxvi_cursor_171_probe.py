"""Offline semantic challenges for Cursor PR #171. Exit 1 means at least one failed gate."""
import json
import subprocess
import sys
from pathlib import Path

SHA = "db4670ab78fa36c8a2b4b8b66df842350440e437"
repo = Path.cwd().resolve()
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
if head != SHA or subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "aurex"], cwd=repo).returncode:
    sys.exit("Run in a clean, detached worktree matching pinned PR #171")
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
failed = sum(not row["pass"] for row in cases)
print(json.dumps({"candidate_sha":head,"cases":cases,"passed":len(cases)-failed,"failed":failed},indent=2))
sys.exit(int(failed != 0))
