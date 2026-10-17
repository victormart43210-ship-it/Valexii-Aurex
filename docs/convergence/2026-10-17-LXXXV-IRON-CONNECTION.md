# LOCKED — KUSANAGI LXXXV / Expert-Depth Iron Connection

**Capture date:** 2026-10-17 (user confirms “Lock all these in”)  
**Evidence class:** OFFLINE SOURCE REPAIRS + LOCAL TESTS; **NOT** MERGED, DEPLOYED OR PROD-VERIFIED  
**Production decision:** **HOLD; NO DEPLOY**  
**Parent:** [Continuous workflow capture](WORKFLOW_CAPTURE.md) · [2026-10-17 baseline](2026-10-17.md) · [Issue #75](https://github.com/victormart43210-ship-it/Valexii-Aurex/issues/75)

## Canonical engineering direction (LOCKED)

Use the four-dimensional expert-depth framework before major change:

1. **SPEED:** Optimize measured turnaround, responsiveness and operating cost; avoid duplicate systems and meaningless new models.
2. **ALTITUDE:** Optimize independently proven end-user outcomes; for AUREX/OX the milestone is an authenticated **Cloudflare server → Railway read-only AUREX API → browser owner-status display**, not local HTTP 200.
3. **DEPTH:** Start from actual source/build/runtime evidence, reproduce failure RED, minimize repair, run GREEN, then find a non-self witness. No green badge inferred from missing CI steps.
4. **RANGE:** Combine streaming byte safety, Worker runtime compatibility, server-only secrets, Railway API, browser accessibility, mobile Ouroboros performance and financial review while respecting boundaries.

> **Outside-Judge question:** What would a leading professional inspect at the rawest source level, which instruments would they use, what competing failure hypotheses remain, and what **independent** test—not AUREX's own narrative—would prove or falsify the result?

**Non-negotiable constitution:** Evidence → Qualification → Reality → Authority → Effect; the system may never be its own sole witness. Unknown/stale/infra failure ≠ PASS. **ORB MOTION AUTHORITY = NONE.** Default paid execution = $0. No unapproved deployment, domain/DNS changes, merge, Worker publish, backend job submit, secrets handling or financial effect.

## LXXXV bounded change — client response-size defect

**Source under review:** owner-exported Oct 17 `valexii-ai` website plus earlier reviewed V2 offline patch; NOT the current private GitHub checkout and NOT the Lovable published SHA. Core source: `src/lib/aurex-client.server.ts`, `src/lib/aurex-client.server.test.ts`; additional independent offline checks under `verification/`.

**Root cause:** Legacy response cap compared decoded JavaScript `text.length` against `256 KiB` *after* `await Response.text()`. JS UTF-16 length can underestimate the raw UTF-8 response size, and reading all text first defeats bounded-memory handling.

**Proposed implementation in offline ZIP:** bounded `ReadableStream` reader counts **raw response bytes** (≤256 KiB), promptly cancels oversized streams, rejects invalid UTF-8, preserves redirects-disabled behavior and minimum 32-character Bearer preflight. Adds defensive Cloudflare generated-Wrangler readiness checks that reject plaintext-looking secrets and do not confuse runtime compatibility with uploaded bindings.

**Versioned owner-held offline artifact:** `KUSANAGI_LXXXV_Expert_Depth_Iron_Connection_20261017.zip`, SHA-256 **`90e9b464e162a629940f3fc08707071c892c2e681706187ccbb5186c8c81c6ef`**. ZIP has 24 entries: 13 modified/new site-source files, source patches, offline test tools, manifest and README. This artifact is in the user's ChatGPT conversation; it is **not** a GitHub website PR, Railway release or deployed Cloudflare Worker. Its README explains exact-source patch preconditions. Do not force `git apply` on newer/diverged source. No `.env` included.

## Fresh reproducibility check, after owner's lock request

On an isolated extraction of the above ZIP:
- `node verification/test_transport_depth.cjs`: **5/5 PASS** (offline transpiled TypeScript with schema stubs; not real Zod or network).
- `node --test verification/test_wrangle_readiness.mjs`: **5/5 PASS** (synthetic Wrangler configuration; never accesses Cloudflare).
- `python -m pytest -q verification/test_ox_latest_release.py verification/test_ox_backend_auth_parity.py`: **7 PASS / 1 FAIL** *when run from the ZIP alone* because the ZIP intentionally contains modified files only, not the unmodified original `src/components/ox-control-station.tsx` required by one source audit. This is a **test-fixture packaging limitation**, not proof of an underlying app failure.
- The same Python tests from the **existing local full-source workspace** (`/mnt/data/KUSANAGI_LXXXV_IRON_CONNECTION`, containing that original component): **8/8 PASS**.
- Release/full-app browser and authenticated service proof: **NOT RUN / NOT VERIFIED**.

These are re-executed offline checks by the same assistant environment, **not** independent third-party witness or production CI. Record the 7/8 standalone ZIP limitation until the next test bundle explicitly includes the original source fixture or the test skips with an honest reason.

## Source-of-truth integration state as of capture

- Published Lovable project `811ffc43-2c8b-4c88-ab4c-4de668d089cb` at SHA **`94ecb8d82f97bc5f1abfc4489eee1c2a2e970358`**: LXXXV site patch **NOT APPLIED**. Lovable workspace AI edit quota was previously exhausted; access not established.
- ChatGPT GitHub app access to the private, Lovable-synced `victormart43210-ship-it/valexii-ai` repo returned **404**; no site PR exists.
- Railway `aurex-api`: **ONLINE/SUCCESS** on read-only bridge SHA **`57a079f93b947594f1a6f854aa46a6f606f86f76`**. Storage and worker configuration patch remains **STAGED**, not accepted.
- AUREX canonical `main`: **`df0654390049118a142ec3b3356f0f40b4789fe4`**; secured canonical integration in **draft PR #72** head **`a490cbe820de7577b1767924998f81b3193d70a7`**, not merged.
- Cloudflare: owner-reported compatible local TanStack/Wrangler dry run, local `/`, `/aurex`, `/aurex/ox` served HTTP 200; **NO verified production Worker deployed** under the test name, route binding and service secret presence **NOT VERIFIED**.

## Next acceptance checks before any deployment request

1. Confirm the **actual live website source SHA** and authorized website repo access; protect any local uncommitted changes.
2. Apply the appropriate incremental/full patch only after exact-source comparison; open **draft PR** and run entire website build, real Vitest, typecheck, lint and browser mobile profiling.
3. Verify bounded stream handling against real JS runtime/Response behavior including chunk boundaries, invalid UTF-8, payload limits, redirect attempts, and minimum-token failures.
4. On actual generated Worker config, check name, custom domain/routes and secret *presence without disclosure*. Keep Worker routing isolated from VALEXII.COM until separately approved.
5. After explicit owner permission, securely verify all **five authenticated GET contracts** end-to-end with exact deployment IDs and no browser token exposure; security owner-only jobs remain private.
6. Obtain independent review/CI on exact SHAs, durable-storage/rollback evidence, and **separate owner authorization** before any source switch, Cloudflare publish, Railway release or domain change.

**Disposition: LOCKED ENGINEERING STANDARD + REPRODUCED OFFLINE REPAIR; WEBSITE PRODUCTION AND CANONICAL RELEASE REMAIN HOLD.**
