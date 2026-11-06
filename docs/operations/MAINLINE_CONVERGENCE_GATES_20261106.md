# Mainline convergence gates — verified CI / unresolved assurance
Date: 2026-11-06
Branch base main: 34cda4bd8f207f5b1284093b87e4760d782a4903
Status: SOURCE INTEGRATION HOLD; production HOLD; financial authority NONE.

## Verified GitHub evidence (not author-only claims)
PR #188 head: 7daeff45efecd5d0293ff8a75afd71b98e9d4df0
GitHub Actions completed successfully on that exact head:
- offline-practice run 42305092496, job offline-practice PASS
- CI run 42305092498, job test PASS (Ruff, Mypy, pytest)
- CLIV run 42305092259, job integration PASS (backend + website tests/build)
- CLII run 42305092275, job verify PASS (backend, Vitest, TypeScript, build)
- Canonical Railway image run 42305092274, job docker-build-and-smoke PASS (non-root, health, SQLite volume)
All returned jobs and steps have conclusion success. This proves CI workflows completed; it does not prove deployed staging, live Qwen, external assurance, or safe merge of conflicting branches.

## Mainline topology
#181 -> #182 -> #184 -> #185 -> #186 -> #187 -> #188 is an overlapping/stacked development chain (some PRs have different bases; do not blindly merge).
#183 contains independent financial and inference fixes, only partially staged into #184 initially; verify exact code in #188.
#172 and #176 have documented financial/evidence conflicts and are excluded pending manual reconciliation.
#188 is based on #187, not main; its mergeability against #187 does not establish admissibility against main.
Search returns at least 100 open PRs (first page cap); full pagination remains pending.

## Required pre-merge controls
1. Fetch fresh main SHA and exact PR head SHA; verify source identity and no hidden changes.
2. Independent reviewer must compare complete cumulative candidate diff with main and #183; verify duplicate-unbilled-ticket, prompt egress, hours/reversal metadata, tenant isolation, receipt authenticity, customer no-contact, $0 confirmed recovery.
3. Run CI on final cumulative candidate against current main; inspect skips, job conditions and workflow path filters.
4. Verify no source deletion of frozen safeguards; enforce explicit authorization, budget cap and fail-closed boundaries.
5. Verify exact tested SHA with full staging and Qwen claims only if those claims are promoted; otherwise maintain BLOCKED/NOT_VERIFIED.
6. Merge one eligible cumulative PR only with expected_head_sha and fresh base; do not separately merge its stacked ancestors.
7. Re-evaluate all remaining PRs as superseded/independent/conflicting and retain traceability.

## Evidence distinction
CI on #188 head: VERIFIED PASS.
Local full checkout and test in this chat: BLOCKED (container DNS cannot resolve github.com).
Financial branch reconciliation: OPEN.
Independent human assurance: OPEN.
Remote staging: BLOCKED.
Live private Qwen: BLOCKED.
Merged PRs: 0.
Production release: HOLD.

## Next executor
Use GitHub Actions or connected Work runner to produce full source review, reproducible CI logs and integration report. Do not convert this documentation PR into an authorization to merge application code.
