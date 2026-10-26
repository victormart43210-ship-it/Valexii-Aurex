# CLXXXIV Work → Jules continuation

Canonical repository: victormart43210-ship-it/Valexii-Aurex.
Main inspected: 551625e5be41ef6fd16e70e7a72404400032f4bc.
Branch: work/kusanagi-clxxxiv-inference-guard. Draft PR #150.
Verified implementation checkpoint CP003: dc6ed44c486b94d1723a6d1095f2ff51e20aec09.
The containing continuation commit adds documentation only; obtain its exact SHA from remote branch HEAD and reconcile any newer contributions. Do not rewrite shared history.

## First executable instruction

Fetch this branch and inspect the policy before enabling anything:

```sh
git fetch origin main work/kusanagi-clxxxiv-inference-guard
git switch --detach dc6ed44c486b94d1723a6d1095f2ff51e20aec09
git show origin/work/kusanagi-clxxxiv-inference-guard:RECOVERY.json
git show origin/work/kusanagi-clxxxiv-inference-guard:RESUME.md
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_remote_inference_hold.py tests/test_model_execution.py tests/test_workflow_budget.py tests/test_four_arm.py
```

Then review aurex/adapters/inference_policy.py and direct adapter transport enforcement. Continue on the existing branch only after comparing its remote head; otherwise create a continuation branch from that head. Do not continue edits from detached CP003 if newer changes exist.

## Completed by Work

- Main/PR145/146/147/149 inventory and exact heads: operation report.
- New central local-only admission policy; OpenAI-compatible transport always denies remote requests before credential lookup or network. An environment enable flag cannot override HOLD.
- InferenceClient records REMOTE_INFERENCE_DISABLED rather than a generic provider failure. Direct adapter calls are protected too.
- Ollama supports existing factory generation settings, sends num_predict/seed/temperature, revalidates endpoint before dispatch and disables ambient proxies.
- 13 new denial/factory/loopback tests; existing llama.cpp real HTTP fixture retained.
- Repaired setuptools discovery and fixture packaging for dispater_proof.
- Full Python suite: 449 passed, 2 skipped; Ruff PASS; MyPy PASS 78 files. Existing Starlette warning.
- dispater-web Node tests 25 passed, build PASS, production npm audit zero reported vulnerabilities. Bun website suite is NOT RUN here.
- Existing deterministic towing demonstration rerun; sanitized actual report committed, 3 revenue candidate findings + 2 readiness findings, all awaiting human review.
- Read-only staging metadata and official NVIDIA/Runpod cost comparison recorded. No paid requests or infrastructure mutations.

## Incomplete, with acceptance tests

1. **Durable remote spending control** — aurex/workflows/budget.py is memory-only and unchanged. Do NOT replace unconditional remote denial with an environment flag. Design transactional reservations, per-request scoped authorization (fresh/revoked state), exact endpoint/model allowlists, positive conservative Decimal bounds and token/deadline limits. Test simultaneous requests and process restart, exhausted/zero/missing budget, stale authorization, failed reservation, ambiguous network billing, retries, and direct adapter bypass. No remote request until all required controls exist. Do not automatically release uncertain charges. Provider account limits and permissions must be verified separately; no paid execution authorized.
2. **PR145 source repair** — refresh its head (last f145187acce5bf61ba2a0cafcc7bbf95663dd2d6). Two add/add conflicts: aurex/openshell_policy.py, tests/test_openshell_policy.py. Reproduce sibling prefix defect with evaluate_filesystem_boundary('/app/data/tenant-a-other/private',('/app/data/tenant-a',)): currently allowed, must deny. Add component-boundary and traversal tests before repair. Symlinks/runtime enforcement require actual supervisor tests; lexical checks cannot claim containment. Preserve main and Jules tests; no automatic merge.
3. **Runner** — PR149 manual workflow not on main. Verify owner runner online/labels, then dispatch reviewed exact SHA through authorized GitHub UI/API; record run and job evidence. Existing success run 40254381225 is independent-runner smoke CI, not proof of owner's headless host. Connected tool set lacked dispatch/runner administration.
4. **Railway/website** — preserve staging deployment 8fe3f398-4e6f-4bfa-8c79-da1b84ccefb4 and /data. Read-only metadata still selects legacy build root. Verify deployed SHA, storage isolation, rollback and server-side credentials before deployment. dispater-web/api/railway-status.js intentionally omits bearer; protected /v1/health cannot establish authenticated connectivity that way. Do not make protected health public or expose a browser token. Reproduce status timestamps in an authorized preview session; static page retrieval cannot validate dynamic UTC/cache behavior.
5. **Onyx** — reuse PR146 at c1d6f3aeb9451c1c5d79dc0bae150512998a51e6 after review. Mock candidates remain HOLD, not admitted evidence. Its CP005 final handoff was interrupted previously. Do not reconstruct adapter from scratch or assume live interoperability.
6. **Full DISPATER chain** — existing fixture/demo tests are local. Authentication, tenant-bound retrieval, durable provenance/manager decision, ledger-linked PROOF and actual preview-to-staging execution must be demonstrated together. Current synthetic output is not a live end-to-end receipt. Use separate manager authority; do not self-approve.
7. **Spreadsheet intake** — inspect current CSV components before adding XLSX. Required tests: fixed synthetic schema, exact cents, duplicate/missing fields, explicit mapping and preserved source hashes; no real uploads. No XLSX implementation was added here.

## Known execution failures and recovery

- Bare pytest initially could not import dispater_proof. Fixed package discovery; isolated editable reinstall and bare pytest now pass.
- pip --no-build-isolation failed because the build backend was unavailable in the reused venv. Standard build-isolated install succeeded. Do not interpret initial subsequent import errors as new source failures.
- Initial frontend run lacked three. Locked npm ci fixed the environment; 25 tests pass.
- CP002 CI/CLIV/CLII failed; CP003 repairs the reproduced package defect. Inspect exact latest CI before release. Earlier CLII website failures expected old marketing copy; do not delete assertions just to get green.
- Shell git push previously lacked credentials. Connected GitHub tree/commit/ref API published commits with expected-head checks, no force. Remote commits have identical source trees but different hashes from local commits; use remote SHAs, not local 64f191d.

## Reproduce verification

```sh
python -m pip install -e '.[dev]'
ruff check .
mypy aurex
env -u ALL_PROXY -u HTTPS_PROXY -u HTTP_PROXY -u all_proxy -u https_proxy -u http_proxy pytest -q
cd dispater-web
npm ci --ignore-scripts --no-audit --no-fund
node --test tests/*.test.mjs
npm run build
npm audit --omit=dev
```

Removing ambient proxy variables was only for the local test process, not production configuration. Python audit, website Bun/TypeScript, live Onyx/NVIDIA, deployed sandbox containment, tenant isolation and complete hosted workflow remain NOT RUN/NOT VERIFIED. Independent reviewer: none yet; Work's tests are not independent certification.

## Stop conditions

No production, merge, paid requests, credentials rotation or real customer records. If tools/time expire, checkpoint source and recovery docs, publish with expected-head protection, verify remote SHA and report actual failures. Keep remote inference disabled. Roll back source to inspected main only through a reviewed branch/revert; no deployed rollback was needed. No automatic Jules background execution has been started.

## Final exact-implementation CI readback

For dc6ed44c486b94d1723a6d1095f2ff51e20aec09: CI 40277912589 PASS, CLIV 40277912627 PASS, canonical Railway image 40277912679 PASS, independent-runner smoke 40277912577 PASS. CLII 40277912587 FAIL: Python/lint/type checks pass; website Vitest 148 passed, 2 failed in consolidated-editorial.test.ts and domain-directions.test.ts, expecting earlier DISPATER copy. TypeScript/build not reached in that chained step. Do not treat the total CI state as PASS. Final documentation-only checkpoint preserves this evidence. Local generated egg-info changes from installation were restored; intended worktree clean.
