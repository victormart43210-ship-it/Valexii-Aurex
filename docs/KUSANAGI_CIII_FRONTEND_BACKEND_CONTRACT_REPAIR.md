# KUSANAGI CIII — Frontend ↔ Backend contract repair (SOURCE-ONLY)

**2026-10-18 · DRAFT / REVIEW HOLD.** This is the next working pass after Lovable KUSANAGI CII. This branch targets the ONE canonical `Valexii-Aurex` GitHub `main`, base `df0654390049118a142ec3b3356f0f40b4789fe4`; it does not merge/deploy/publish, spend Lovable credits, run Qwen, submit jobs, send sensitive records, or alter Railway/Cloudflare bindings. Do not confuse this repository's **`website/` source copy** with the **separate, more recently edited Lovable project's current source**.

## Facts refreshed directly from providers
- Lovable project `811ffc43-2c8b-4c88-ab4c-4de668d089cb` source: `73f800bc43e32b3ebb907131480658262bc460ef`, published project exists, but source-to-production publish equivalence unverified. Latest task used **4.7 credits**; no further Lovable billable requests authorized during this GitHub-only pass. Prior Lovable task reported 43 focused tests PASS, scoped lint clean; independent owner-authenticated display and separate typecheck NOT VERIFIED.
- Railway project `VALEXII-AUREX` production contains live `aurex-api` service from branch `integration/kusanagi-xvi-railway`, older read-only bridge (source reported deployed SHA `57a079f93b947594f1a6f854aa46a6f606f86f76`). Latest Railway deployment status SUCCESS (control-plane). **Four staged changes** remain pending and a `aurex-evidence-db` volume is **staged-create**, not mounted live. No live worker/SQLite evidence-generation proof.
- GitHub canonical main `df0654390049118a142ec3b3356f0f40b4789fe4`, with many overlapping unmerged draft PRs. GitHub hosted CI has been failing before test steps owing to billing restrictions; **never treat this as tests passing**. The separate proposed Hetzner GitLab Runner bridge is draft #92, runner actual availability NOT VERIFIED.
- Current hosted bridge `integrations/kusanagi-xvi/backend/app.py` requires >=32-char server-side bearer and exposes exactly five read-only GETs: `/v1/health`, `/v1/capabilities`, `/v1/jobs`, `/v1/evidence`, `/v1/budgets`. `/v1/health` returns `{status,version,time}` **without capability list**; available capabilities are false, job list empty, evidence empty, budget zero in the exact source. Live caller Cloudflare attribution and secret configuration are not proven by code alone.

## What this branch implements in backend & frontend SOURCE

**Frontend source, isolated copy `website/`:**
- Port bounded raw-byte (256 KiB), manual-redirect, fatal UTF-8, early oversized body rejection and >=32-character token checks to `website/src/lib/aurex-client.server.ts` for the **GitHub historical website copy**, without relaxing HTTPS/non-local URL validation.
- Correct `website/src/lib/aurex-service.server.ts`: health and capabilities are **different endpoints**; health cannot self-report its capabilities. Require all data to pass typed schema; only evidence-linked, recent capabilities are shown as candidates. Import the client lazily to avoid existing module circular-reference initialization.
- Update `website/src/components/aurex-capabilities.test.ts` and add `website/src/lib/aurex-client.server.test.ts` to cover actual five-GET shapes, missing/false capabilities, HTTP 401/503, oversized raw bytes, forged Content-Length, invalid UTF-8 and short-token no-request. Fake responses are synthetic.
- Update the existing contract description: `website/docs/aurex-api/openapi.yaml` is a **draft full API**, separate from the deployed read-only five-GET bridge.

**Backend/source-only:** `integrations/kusanagi-xvi/tests/test_five_get_frontend_contract.py` asserts the actual FastAPI **read-only bridge source** returns the five exact frontend response shapes for a synthetic 32-character bearer; missing/wrong credentials 401; disabled secret 503; no POST effects; capabilities and evidence remain unavailable/empty. This tests an offline FastAPI app in-process, **not production DNS, Cloudflare, TLS, the Worker service credential, or real SQLite**. Its checks must be rerun on the exact PR SHA.

## Required independent tests

```bash
# From repo root:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q integrations/kusanagi-xvi/tests/test_contract.py integrations/kusanagi-xvi/tests/test_five_get_frontend_contract.py
ruff check integrations/kusanagi-xvi/tests/test_five_get_frontend_contract.py
cd website
# Use repo-approved frozen installation on trusted CI. Avoid unreviewed dependency scripts.
bunx vitest run src/components/aurex-capabilities.test.ts src/lib/aurex-client.server.test.ts
bunx tsc --noEmit
bun run build
```

Also preserve full AUREX `pytest`/Ruff/strict Mypy suite and CUSTOS auth/privacy/lease fencing regressions. Frontend CI must use actual repo lockfile and compatible Node/Bun versions. Results NOT RUN/NOT VERIFIED until exact SHA receipts exist; do not infer from previous Lovable PASS.

## Runtime launch ladder (do NOT skip steps)

| Gate | Current evidence | Admission |
| --- | --- | --- |
| 1. Source code | Older Railway GET bridge and new draft typed frontend repair | CODE AVAILABLE, PR review pending |
| 2. Test/CI | Past local tests, Github runner billing startup failures | NOT VERIFIED at this HEAD |
| 3. Deployed | Railway **older read-only bridge** SUCCESS, staged new worker/storage NOT applied; Lovable public site exists, current source publish SHA not established | PARTIAL / NOT CURRENT |
| 4. Browser→Worker→Railway→worker→SQLite→evidence→owner view | No independently verified real authenticated round trip through all components | NOT VERIFIED / HOLD |

Before promotion, on an approved test environment with existing secret provider (never print secret): obtain **authorized owner-only** read-only HTTP results from the **actual Worker route** and Railway host, with timestamp, actual deployment SHA, 401 reject and 200 typed payload. Prove request attribution without logging bearer, then prove working offline job/persisted evidence separately after owner deploy authorization. Do not treat a 2xx transport as independently verified intelligence. Real private-company PDFs and financial/IRS/DOT/insurance claims remain **LOCAL/PRIVATE, HUMAN REVIEW HOLD**.

## Remaining deployment blocker & how to avoid duplicate work
- Lovable latest source already has the bounded transport fix and corrected five-GET fixtures from the previous paid pass. **Do not send this entire historical `website/` tree to Lovable**, overwrite modern site source, create a second website, or pay Lovable to repeat finished work. Use this PR only to bring the **canonical GitHub website copy** into closer API/security alignment and independently review diffs.
- Authenticating the published site to the existing Railway backend is a separate **owner-authorized** Cloudflare/Railway credential and route task. Current source presence does not prove bindings or deploy.
- Review PR #76 and older CI specs before choosing the final app-worker integration; do not bulk merge 52 PRs or apply four staged Railway changes.
- Capture the evidence in GitHub issue #75 and have a reviewer other than the implementer verify the exact SHA. Keep **ONE APIS PRIME spine, zero extra tabs**; current 10 OX nav tabs and owner Studio A/B/C unaffected. Orb presentation has **zero authority**.

**CUSTOS STATUS:** DRAFT / HOLD. No main merge, production publication, DNS, payment, credit spend, inference or user-data operation. Rollback: close draft PR; deploy state unchanged.
