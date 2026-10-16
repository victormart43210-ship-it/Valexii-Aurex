# AUREX / OX — Sovereign convergence audit (2026-10-15)

**State: HOLD — inventory branch, not a completed merge or release.**

## Canonical target
Repository: `victormart43210-ship-it/Valexii-Aurex`. Proposed monorepo includes the real Lovable website frontend, governed AUREX backend, a single versioned API contract, test and deploy manifests. Preserve Lovable editor until its actual GitHub sync target is proven. `Valexii-nexus` is a separate minimal repository; do not delete it or assume it is synchronized.

## Verified branch comparison (against main at inspection)
- `integration/kusanagi-xxix-sovereign-pipeline`: 32 commits ahead / 0 behind, 54 changed files.
- `integration/one-mainline-merge`: 15 ahead / 0 behind, 10 changed files.
- `integration/kusanagi-xvi-railway`: 1 ahead / 12 behind.
- `integration/kusanagi-xx-local-inference`: 4 ahead / 12 behind.
- `integration/kusanagi-xxii-governed-execution`: 5 ahead / 12 behind.
- `integration/aurex-website-20261013`: 0 ahead / 1 behind.
- `work/aurex-ox-e2e-gate-20261015`: 18 ahead / 0 behind.
- Comparing one-mainline to xxix: divergent (29 ahead, 12 behind). Do not fast-forward or overwrite.

## Hard blockers
1. **False execution evidence:** prior `aurex/api.py` regression_scan route generated PASS-like evidence without verified worker execution. PR #20 and PR #22 propose overlapping fail-closed remediation. Review exact target behavior and independent tests; an API returning 200 is NOT independent execution proof.
2. **CI:** PR #24 CI failed Ruff on import ordering; a repair was committed, but a new passing CI result has not been observed.
3. **Website:** Lovable project `811ffc43-2c8b-4c88-ab4c-4de668d089cb` has real source, owner-control and API contract. Actual Lovable-to-GitHub sync target is NOT VERIFIED. Preserve full Lovable HEAD, including binary assets and migrations, before any replacement.
4. **Deployment:** Railway VALEXII-AUREX currently has a production service `aurex-api` deployed from `integration/kusanagi-xvi-railway` at commit `57a079f93b947594f1a6f854aa46a6f606f86f76`. Isolated staging NOT VERIFIED; no writes to production for tests.
5. **Inference:** local Qwen/Chromebook execution NOT VERIFIED end-to-end.

## Reconciliation sequence
A. Freeze and record exact SHAs and content inventories for Lovable HEAD, main, PR #20/#22/#23/#24, xxix, one-mainline, Railway deployment. Preserve source provenance.
B. Independently test false-PASS negative cases, verifier trust pins, job ownership, idempotency, cancellation, budget 0, restart persistence, and evidence integrity. Resolve #20/#22 BEFORE allowing any job execution claim.
C. Three-way reconcile `integration/one-mainline-merge` and `integration/kusanagi-xxix-sovereign-pipeline` in an isolated worktree. Preserve independent changes, do not blindly choose one side. Run Ruff, Mypy, Pytest and security tests.
D. Import exact current Lovable source with assets into canonical `website/` only after GitHub synchronization ownership and licensing are confirmed; align OpenAPI schemas. Do not overwrite more recent frontend changes.
E. Provision isolated staging with separate secrets/storage and run opt-in API gate from PR #24 only after correcting its real-execution assertion. Then test browser → owner-authenticated server-side proxy → job → independent evidence.
F. Produce independent exact-SHA report with PASS/FAIL/NOT RUN/NOT VERIFIED for every gate. Request explicit approval before main merge or production deployment.

## Non-negotiables
Evidence → Qualification → Reality → Authority → Effect. No self-witness. Unknown ≠ healthy. $0 default paid spend. No browser bearer tokens. No fabricated results. No unapproved merges, production deploys or repository deletions.
