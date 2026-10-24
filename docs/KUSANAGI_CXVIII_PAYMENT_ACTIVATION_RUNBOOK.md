# KUSANAGI CXVIII — SUBSCRIPTION-READY INTEGRATION / OWNER ACTIVATION RUNBOOK

**Snapshot:** 2026-10-21 · **State:** PREPARED / NOT PURCHASED / NOT DEPLOYED · **CUSTOS: HOLD**.
**Canonical repo:** `victormart43210-ship-it/Valexii-Aurex` main at `df0654390049118a142ec3b3356f0f40b4789fe4`. Draft PR #104 is **not merged**. This runbook is an *owner-only operations guide*, NOT authority to turn on production or take customer documents.

## Inventory verified via connected provider tools

| Item | Existing resource | Immediate action |
| --- | --- | --- |
| Lovable | Workspace `V's Lovable` **Pro**; project `Valexii Ai`, `811ffc43-2c8b-4c88-ab4c-4de668d089cb`; source HEAD `0cc4f81e0fa423247be834d45451ed66e1e9487b`; website published / new source preview | Keep plan. Check remaining credits; add only minimal one-off credit pack if required. Do NOT make new project or publish unverified financial capability. |
| Lovable Supabase | Cloud database **enabled** in same website project | Reuse. Do not buy second Supabase project or add customer uploads without tenant security assessment. |
| Railway | `VALEXII-AUREX` project `78095d3d-5911-41c8-aa3e-f9ebf5d81054`; API service `2b51dfe6-2175-4cb0-aac2-eb40ecbc3a1d`, last reported SUCCESS 2026-10-14; configured source `integration/kusanagi-xvi-railway@57a079f9...` (OLDER BRIDGE) | Check actual workspace plan and estimated usage. Do NOT create a second backend or deploy PR #104 blindly. |
| Railway staged patch | Four **not applied** changes under patch `814e3b02-7f90-4812-b107-32e3e7aad529`: staged `aurex-evidence-db` volume at `/data`, `AUREX_DB_PATH`, `AUREX_ENABLE_OFFLINE_LAB` | Keep staged; before accepting verify value of lab flag, storage/backups, database path, migration/rollback and source image compatibility. Staged volume is not a live backup. |
| Railway newsletter | Existing `BCXMET V43 Website` project `898d92fa-4a15-4832-91cb-cc6caa74e6d3`, live Listmonk + PostgreSQL and 2 persistent volumes | Reuse only if needed for existing newsletter; not a dependency for financial proof. No duplicate purchase. |
| GitHub | Canonical repo, draft PR #104 `KUSANAGI CXVII`; hosted CI / image / independent runner **FAIL**, prior jobs returned no executed steps | Check account billing and Actions spending restriction; do not disable CI. Review workflow metadata after billing repair, then rerun exact PR head. |
| Namecheap domain | `valexii.com` exists, public website previously published | Check renewal expiry; no new domain required for integration. |
| Qwen/Ollama | Local research path; live inference not independently verified | Start with offline $0 baseline; no OpenAI API credit or GPU subscription required to test synthetic deterministic path. |

### Authoritative published prices (check checkout before paying)
- Lovable Pro: **$25/month** with **100 monthly credits**; current workspace is already Pro. On-demand top-ups are separate and currently quote at checkout. https://lovable.dev/pricing
- Railway Hobby: **$5/month**, including up to $5/month of usage credited against its fee; Railway Pro: **$20/month**, $20 usage included. **Actual workspace tier is not exposed by connected Railway workspace listing.** Storage, compute and egress over included usage can increase charges. https://docs.railway.com/pricing/plans
- GitHub Free has private repos and included Actions minutes; paid plans/Actions usage vary. Current account plan and exact billing restriction **cannot be read by the GitHub connector**. https://github.com/pricing
- Don't add these line items together as if all are new charges: **Lovable Pro is already active** and Railway service is already live. Account statement/checkout determines what is actually due.
- No new paid Qwen, OpenAI API, Resend, Vercel, Namecheap domain, Supabase Pro, or Cloudflare Pro is required for the $0 synthetic proof.

## OWNER STEPS — after funding card (personal payment only)

**A. GitHub FIRST:** https://github.com/settings/billing
1. Check active plan, payment method, past-due status, Actions spending budget/limit, and any account restrictions. Do not change repository permissions.
2. After resolving a concrete billing restriction, rerun CI only for latest exact head of PR #104 and inspect **job step logs**; if still zero steps, escalate to GitHub support rather than repeatedly rerunning.
3. Pass local Python + web tests, Ruff/Mypy and independent review; no automatic merge.

**B. Lovable:** https://lovable.dev/settings/billing
1. Confirm the existing Pro subscription, exact current balance and whether top-up is needed.
2. Buy **one small top-up only** if balance insufficient; no Business upgrade by default.
3. Existing project editor: https://lovable.dev/projects/811ffc43-2c8b-4c88-ab4c-4de668d089cb
4. Important: its **actual** `src/lib/aurex-api-schema.ts` already accepts snake_case and `offline_probe`; do NOT apply old GitHub website contract changes blindly.
5. Hold public publishing until owner-only synthetic results and authentication have passed mobile and security tests.

**C. Railway:** https://railway.com/dashboard
1. Open project `VALEXII-AUREX`, inspect current **plan**, **usage**, **spending caps**, deployed SHA, health and all staged edits. Existing deployment and resource metrics do NOT equal latest AUREX code.
2. Do not accept the staged four-change production patch until backups/volume mount, DB migration, `AUREX_ENABLE_OFFLINE_LAB` value and compatibility with current deployed code have been checked.
3. For a future reviewed synthetic-only staging/canary, use a separately authorized config and keep `AUREX_ENABLE_SYNTHETIC_FIELD_AUDIT` absent/disabled by default.
4. Keep bearer secret server-side only. Owner config NAMES (do not paste values in chat): `AUREX_SERVICE_URL`, `AUREX_SERVICE_TOKEN`, `AUREX_OWNER_USER_ID`; backend `AUREX_DB_PATH`, `AUREX_ENABLE_OFFLINE_LAB`. `AUREX_ADMIN_TOKEN` must not conflict with service token.

**D. No additional subscriptions until actual test warrants them:** Local Qwen baseline, existing Supabase, Railway Postgres + Listmonk, website custom domain and simple synthetic proofs use what is already available.

## NON-DEPLOYING technical checks

Existing PR #104 has a fixed, fictional 100-case synthetic reconciliation candidate in the canonical AUREX API's **opt-in local** `regression_scan` probe. A scored toy fixture **does not prove real financial intelligence**.

On a local safe checkout of exact PR head:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q \
  tests/test_api_sqlite_contract.py \
  tests/test_field_audit_beta_gate.py \
  tests/test_field_audit_beta_pipeline.py \
  tests/test_wiring_preflight.py
python3 -m workstation.wiring_preflight    # default: prints NOT_RUN; ZERO network
```

Only when owner expressly wants a **read-only** diagnostic of their existing Railway URL, set the service root and bearer token as private environment variables (do not paste into chat), and run:

```bash
python3 -m workstation.wiring_preflight --execute
```

The diagnostic performs **five GET requests only** to a strict HTTPS `*.up.railway.app` host: health, capabilities, evidence, budgets, jobs. It rejects redirects, oversized responses and malformed wire schema, emits only coarse status, never prints token/job content and always reports `production_release=HOLD`. HTTP 200/shape success is **transport only**, not independent verification or genuine intelligence.

### Required release DAG — separate steps, no shortcuts

1. **Source:** exact SHA and CI PASS, independent reviewer, no-self-witness and safe branches.
2. **Evidence:** confirm database migration/lease failure policy, crash recovery and SHA-linked receipt to genuine accepted synthetic job through existing backend.
3. **Reality:** test owner-only authenticated website→backend request→worker→SQLite→evidence receipt→UI in nonproduction, with no PII or customer documents; read-only preflight alone is not enough.
4. **Qwen:** later measure real held-out prediction quality and false-positive rates; G-Factor PR #102 is not yet real Qwen performance.
5. **Authority:** owner explicitly authorizes a separate release after privacy/security and independent review; customer beta and payment controls remain HOLD.

**No card charge, subscription purchase, merge, deployment, database enablement, or public publication has been performed by this runbook.** Never send passwords, private tokens or bank-card details to this chat.
