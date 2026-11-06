# CCLVII — START HERE

Repository: https://github.com/victormart43210-ship-it/Valexii-Aurex
Work branch: `work/kusanagi-cclvii-sovereign-execution`. Base/current integration: `c4f45925e086bbb23b643e66707b224419d52b60` (#181).
Main: `34cda4bd8f207f5b1284093b87e4760d782a4903`. Cursor CCLVI #182: `8323f6db245186b98f2bf2c99a9297e88849e15e`.
Initial checkpoint not yet remotely persisted; verify actual remote HEAD rather than trusting this file. No self-referential SHA.

Next exact action: persist/read back this checkpoint, then compare current engine and Cursor182 changes to select a nonoverlapping defect. Add failing regression, bounded fix, focused/golden tests, next remote savepoint. Do not duplicate Cursor182 customer/orphan-payment or sidecar changes. Do not work from stale main.

## Reproduce
`git fetch origin`; select Work branch; inspect RECOVERY and EXECUTION_LEDGER. Create isolated venv with `python3 -m venv .venv` and `.venv/bin/pip install -e '.[dev]'`; parser deps from candidate manifest. Host proxy may require environment-only socksio. Use unique temporary databases, synthetic fixtures only. Commands: `python -m pytest -q`, `ruff check .`, `mypy aurex`; website `npm ci --ignore-scripts`, `npx vitest run`, `npx tsc --noEmit`, `npm run build`; dispater-web `npm test`, `npm run build`.

Shell GitHub push was unavailable in the prior session. Connected GitHub Git-data commits and ref writes succeeded; use compare-and-swap expected SHA and verify with git ls-remote. No force push. Prior Work173 actual checkpoint must be inspected if its artifacts are needed; old counterexamples may be repaired by the current stack.

## Boundaries
Work owns new CCLVII records and a narrow tested repair in its isolated branch. Copilot owns integration181, Cursor owns182. Read their records; no shared branch writes. Preserve385identified/150withheld/0recovered and invoice10/0. No source of truth from LLMs. Production HOLD, financial NONE, external paid inference/training/customer data/third-party contact OFF. No merge/deployment.

## Privacy slice ready
Initial remote7b50f9e verified; draftPR183. Local inference and OllamaAdapter now explicitly disable inherited proxies while keeping redirect/read bounds. Two new tests failed before fix and23focused tests pass after. No paid provider/model download. Next: verify next remote checkpoint, then financial duplicate-ticket slice.

## Financial slice ready
Proxy checkpoint0638ace verified. Duplicate equipment/date unbilled work now returns explicit DUPLICATE_FIELD_TICKET/INSUFFICIENT_EVIDENCE with all source hashes and0identified, instead of summing400; single-ticket control200.37financial/golden testsPASS. Next: HTTP request drops equipment/labor, three new regression assertions fail. Fix that boundary without changing legacy empty-field request digest.
