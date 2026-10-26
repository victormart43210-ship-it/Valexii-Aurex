# CLXXXIV current-state inventory

Main: 551625e5be41ef6fd16e70e7a72404400032f4bc, fetched 2026-10-26 UTC.

| PR | Current state | Exact head |
|---|---|---|
|145|Open, conflicts; Jules active source; not imported|f145187acce5bf61ba2a0cafcc7bbf95663dd2d6|
|146|Draft, mergeable, governed Onyx synthetic adapter|c1d6f3aeb9451c1c5d79dc0bae150512998a51e6|
|147|Draft, mergeable, website copy only|0693f0cb2d4c7e38977fd3d86e4bcf9ba6446510|
|149|Draft, mergeable, runner preparation|0b8b0b282ffa11ec814268a54647fd1769a42537|

Main has no root RECOVERY.json or RESUME.md. Other branches' histories are preserved. PR146 CP004 remote head was read back in GitHub; its CP005 continuation remains unfinished. Do not duplicate its Onyx adapter.

Confirmed gap: InferenceClient calls adapter.answer without a budget guard; CLI factory constructs client without one. BudgetGuard is Decimal-based but mutable, memory-only, with no concurrency/restart durability. A zero reservation is accepted. Do not change that shared contract blindly.

Owned files: inference policy, OpenAI-compatible transport, execution client, Ollama and CLI compatibility, focused tests and recovery docs. No parallel writers. Acceptance: no remote dispatch, even through direct adapter calls, while durable accounting is unavailable; local loopback behavior survives. No paid positive-path claim. Rollback is main base above; no infrastructure changes. Independent reviewer pending Jules.

PR145, runner, website/Railway, pricing and full DISPATER convergence remain unfinished. No claim of live interoperability, GPU capacity or deployed containment.

## CP002 implementation

Seven tests failed before implementation (remote network attempted; Ollama factory generation TypeError). All seven pass after repair. Focused suite 35 passed; full module-invoked pytest 443 passed, 2 skipped, existing Starlette warning; Ruff PASS; MyPy PASS across 78 source files. Full command removes ambient proxy variables as documented in prior Onyx work.

Central require_local_dispatch is called at both OpenAI-compatible and Ollama transport boundaries. Direct adapter calls cannot bypass remote HOLD. Client records REMOTE_INFERENCE_DISABLED without credential text. No remote enable flag exists; this is a denial boundary, NOT completed durable budget accounting. BudgetGuard unchanged. Ollama factory now accepts generation settings and sends bounded num_predict, seed, temperature; ambient proxies disabled.

PR145 exact merge-tree check found add/add conflicts in aurex/openshell_policy.py and tests/test_openshell_policy.py. New filesystem startswith policy appears to admit tenant-a-other under tenant-a; requires adversarial repair before import. No shared branch overwritten.

PR149 exact-head CI: independent-runner smoke run 40254381225 success; CI 40254381281, CLIV 40254381315, CLII 40254381240 failed. This does not verify the owner's self-hosted runner. Manual headless workflow is absent from main; its branch requires self-hosted/linux/x64/aurex-verification labels. No workflow-dispatch tool is available, and registration/online state remains NOT VERIFIED.

## CP003 actual evidence and blockers

Expanded security tests preserve real loopback Ollama and llama.cpp. Latest 449 passed, 2 skipped, one Starlette warning; Ruff PASS; MyPy PASS (78 files). Reproduced bare pytest failure importing dispater_proof, repaired package discovery and CSV fixture inclusion in pyproject.toml. Editable installation with build isolation succeeded; bare pytest now also passes all 449 tests. Initial --no-build-isolation attempt failed due missing build backend; did not establish test success.

DISPATER frontend: npm ci --ignore-scripts --no-audit --no-fund, node --test tests/*.test.mjs: 25 passed; npm run build PASS; npm audit --omit=dev: zero reported vulnerabilities. Initial test run failed for missing three before dependencies were installed. These are Node tests for dispater-web, not the historical 149 Bun tests for website. Bun/website TypeScript build not reproduced. Python dependency audit NOT RUN.

Reused examples/dispater_towing_synthetic.json through aurex.dispater_demo.build_demo_report. Actual report committed at docs/verification/CLXXXIV_SYNTHETIC_TOWING_OUTPUT.json. Three revenue candidate findings, two readiness findings, five awaiting review, HOLD, NVIDIA NOT RUN. Existing loopback HTTP and human acknowledgment tests passed in the suite. This is not a tenant-authenticated live browser-to-ledger end-to-end claim; durable manager authorization remains unverified.

Railway read-only inspection: aurex-staging (98c103eb-a1af-46b6-948e-19c80e4d720d), service 2b51dfe6-2175-4cb0-aac2-eb40ecbc3a1d, deployment 8fe3f398-4e6f-4bfa-8c79-da1b84ccefb4 reports SUCCESS, created 2026-10-24T12:23:27.131Z. Main source with root /integrations/kusanagi-xvi/backend, Dockerfile builder, volume 4d23b1e6-3625-4def-aa97-82e10859f04d at /data; no staged changes. Deployed SHA and production isolation NOT VERIFIED. Only variable names inspected, never secret values. Current main Dockerfile copies app.py only and runs app:app; canonical adapter patch is not automatically included.

Public valexii.com static retrieval showed Check unavailable for API checks; dynamic authenticated state was not observed. Public health retrieval through search tool was unavailable, not proof of service outage. DISPATER railway-status.js deliberately sends no bearer to protected /v1/health; its 401 handling reports BEARER_AUTHORIZATION_REQUIRED rather than readiness. Requires approved server-side credential wiring, not loosening health authentication. No infrastructure changed.

PR145 adversarial reproduction at f145187acce5bf61ba2a0cafcc7bbf95663dd2d6: evaluate_filesystem_boundary('/app/data/tenant-a-other/private',('/app/data/tenant-a',)) returned allowed=True, reason=path_allowed. Expected False. This is a source-level policy defect, not evidence of deployed sandbox escape. Its claimed independent/production metrics were not adopted. OpenShell runtime remains NOT RUN.

Onyx PR146 remains separate and saved at c1d6f3aeb9451c1c5d79dc0bae150512998a51e6; avoid duplicate adapter development. Mainline CSV demo exists; XLSX intake not found in inspected mainline components and not implemented here. Local inference memory/hardware and NVIDIA account controls remain unverified. No paid requests, production deployment, credential rotation or main merge.
