# Cursor #171 — independent source and synthetic challenge

**Disposition: HOLD; do not approve as a verified financial or ingestion baseline.** Review subject: `victormart43210-ship-it/Valexii-Aurex`, PR #171 detached HEAD `db4670ab78fa36c8a2b4b8b66df842350440e437`. Reviewer: separate ChatGPT Work review lane; did not author #171. This is independent of the candidate's author, not external audit or independent real-world evidence. Cursor's own `docs/operations/CURSOR_CHATGPT_HANDOFF.json` cites implementation SHA `1f6f740d4c95f410d5b5a31ee605ceced76c8b5e` and correctly distinguishes a later branch tip. No customer data, inference, payments, source changes or deployments.

## Reproducible challenge (Python; run locally in the pinned checkout)

```python
import json
from pathlib import Path
import aurex.dispater_ingest as ingestion
from aurex.dispater_intelligence import RevenueLeakageEngine
from aurex.dispater_monitor import monitor_increment
from aurex.dispater_api import ReconciliationRequest
assert Path(ingestion.__file__).resolve().parent.parent == Path.cwd()
ingest = ingestion.ingest_source
j = dict(job_id="J", customer_id="C", service_code="tow", date="2026-02-01")
r = dict(rate_id="R", customer_id="C", service_code="tow", start="2026-01-01", end="2026-12-31", amount="100")
i = dict(invoice_id="I", job_id="J", status="open", amount="100")
p = dict(payment_id="P1", invoice_id="I", amount="100")
d = dict(tenant_id="T", dataset_type="SYNTHETIC_ONLY", jobs=[j], rates=[r], invoices=[i], payments=[p, {**p,"payment_id":"P2"}])
engine = RevenueLeakageEngine("T")
reconcile = engine.reconcile_records
rep = reconcile(d)
print("two potentially identical remittances:",rep["financial_summary"],[(f["code"],f["exposure_usd"]) for f in rep["findings"]])
f = reconcile({**d,"payments":[],"invoices":[]})["findings"][0]
print("rate-funded estimate:",f["exposure_usd"],[ev["kind"] for ev in f["evidence"]])
bundle = ingest("T","batch.json",json.dumps({**d,"tenant_id":"OTHER","dataset_type":"LIVE"}).encode(),kind="json")
print("conflicting labels:",bundle["dataset"]["tenant_id"],bundle["dataset"]["dataset_type"])
csv = b'invoices,invoice_id,job_id,amount,amount,status\n,I,J,900,1,open\n'
print("duplicate column:",ingest("T","s.csv",csv,kind="csv")["dataset"]["invoices"])
try: ingest("T","s.csv",b'invoices,invoice_id,job_id,amount,status\n,I,J\n',kind="csv")
except Exception as exc: print("short CSV:",type(exc).__name__)
print("unknown table:",ingest("T","s.json",b'{"deposits":[{"id":"1"}]}',kind="json")["dataset"])
print("API synthetic label default:",ReconciliationRequest.model_validate({"tenant_id":"T"}).dataset_type)
print("freshness/source SHA present in report finding?",[k for k in f if "source" in k or "fresh" in k])
print("monitor replay cash:",monitor_increment("T",d,d)["confirmed_recovery_usd"])
```
