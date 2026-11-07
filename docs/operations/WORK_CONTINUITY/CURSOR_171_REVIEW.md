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

## What the challenge established

| Priority | Observation at the pinned SHA | Acceptance gate |
|---|---|---|
| High | `aurex/dispater_ingest.py:_rows_from_json/ingest_source` accepts a source explicitly labeled tenant OTHER and LIVE and emits T/SYNTHETIC_ONLY. Unknown tables alone produce a valid empty dataset. This is a library boundary defect; we did not find an HTTP route exposing this parser. The server tenant must still come from authenticated context. | Reject contradictory scope or data class, distinguish empty/unsupported input from an audited control, and explicitly require synthetic admission upstream. No claim that labeling verifies actual data origin. |
| High | Duplicate CSV header `amount,amount` with `900,1` produced a typed invoice for 1. Short required rows raised AttributeError instead of controlled IngestError. JSON duplicates default to last-key-wins; type coercion converts null to text. See `aurex/dispater_ingest.py:_rows_from_csv/_rows_from_json`. Monitors consume typed rows, not the ingestion receipt, so a downstream finding does not recover its source-byte digest/row path. | Reject ambiguous columns/keys and wrong cell types; preserve validated source lineage through reconciliation. |
| High | `aurex/dispater_intelligence.py:364–437` calculates a $100 overpayment from two indistinguishable $100 postings against one $100 invoice, while explicitly flagging the two payments as unresolved. Identified/unverified exposure **100.00**, withheld **0.00**, recovered **0.00**. Both duplicate export and distinct transfers fit the same evidence; a duplicate export yields no overpayment. This is a candidate-dollar overstatement in one consistent scenario, not a cash booking. | Withhold contested contribution or display scenario bounds until remittance identities are resolved. Preserve $0 actual recovery. |
| Medium | `aurex/dispater_intelligence.py:221–245` derives $100 unbilled exposure using a rate row but its only evidence kind is job. Changing the rate changes the dollar amount without changing the finding's listed source rows. Global dataset digest does not identify the required rate row. | Attach the effective rate and mark missing invoice as scoped to snapshot completeness. |
| Medium | `aurex/dispater_api.py:ReconciliationRequest` defaults absent data class to SYNTHETIC_ONLY. `website/src/components/dispater-reconciliation-console.tsx` says “Control Dataset Clean”/“Zero false positives” for zero findings. Empty inputs or unsupported evidence cannot establish that conclusion. `aurex/dispater_intelligence.py` also describes an orphan payment as deposited without a deposit record. | Require explicit synthetic classification and qualify absence and deposit status in UI/XAELI. |
| Medium | `aurex/dispater_monitor.py` refuses conflicting identifiers, suppresses recovery even on replay and calls absence non-resolution. It recomputes in memory from unversioned snapshot tables. No authenticated/durable incremental intake, independent roots, signed checkpoint or durable event delivery established. | Keep it an offline primitive; exercise versioned replay, restart and bounded volume before pilot. |

**Receipt and authorization boundaries:** `aurex/dispater_receipt.py:seal_run` includes run identity, timestamp, binding label and data in the hash and MAC. `aurex/dispater_store.py:_verified` checks these for v2; legacy adds unsigned annotations without rewriting. `list_runs` verifies returned rows; `finding_history` compares selected entries to the signed body. An attacker deleting a row can still hide a signed report: per-row MAC is not a completeness or freshness witness. The reviewed tests include downgrade, metadata swap, replay, tenant controls and short/absent keys. The web contract can render a binding label supplied by the backend; it does not independently authenticate a receipt. `/findings` projects results without the binding label; export/full report is the relevant artifact. Financial and production authority were never exercised.

**Commands/environment:** From a clean detached worktree (git status --short empty before/after), ran `git rev-parse HEAD`, read AGENTS and both linked playbooks, Cursor handoff, the modules cited above, and the website contract and console. Set `PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 AUREX_DB_PATH="$(mktemp -d)/jobs.db"` (exported); Python interpreter `../Valexii-Aurex/.venv/bin/python` (3.12). Asserted the imported module's parent matched the pinned worktree before running the probes.

```bash
../Valexii-Aurex/.venv/bin/python -m pytest -p no:cacheprovider -q tests/test_dispater_golden_audit.py tests/test_dispater_ingest_monitor.py tests/test_dispater_receipt_authenticity.py tests/test_dispater_security.py
```

**Observed:** 60 passed, 1 FastAPI/Starlette TestClient deprecation warning, 1.03 s. The independent Python probe above exited 0; it prints observed failures rather than asserting that they are desirable. Only the review report and replay probe were written; the pinned checkout stayed clean. This lane did not run the full suite, browser, frontend build, real document parsing, model inference, hosted runtime, field pilot, cash settlement, or production audit. No commercial efficacy, compliance conclusion, cash recovery or independent release approval follows from these synthetic results.

**Durable assertion-based replay:** `scripts/verification/ccxxxvi_cursor_171_probe.py` checks the exact candidate commit and imported module locations, emits JSON observations and expected results, and returns nonzero if any safety/correctness expectation fails. From the detached review checkout, ran `../Valexii-Aurex/.venv/bin/python ../ccxxxvi/scripts/verification/ccxxxvi_cursor_171_probe.py` with the environment above: **exit 1; 9 checks, 2 passed, 7 failed** (5 ingestion cases, 1 candidate financial dollar assignment, 1 omitted rate citation). Both no-cash-authority checks passed. This command is intentionally outside default pytest discovery.
