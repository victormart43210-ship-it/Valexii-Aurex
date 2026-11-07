# KUSANAGI CXXXIV — Mainline convergence evidence and review gates

**Scope:** `victormart43210-ship-it/Valexii-Aurex`, open-PR snapshot on 2026-10-22 (America/Chicago).
**Baseline `main`:** `df0654390049118a142ec3b3356f0f40b4789fe4`.
**Status:** SOURCE INVENTORY ONLY; no merge/deployment authority; independent review NOT RUN.

## Work actually completed
- Queried all **78** currently open PR metadata records and **all 78 changed-file inventories** using authenticated GitHub API reads.
- Preserved their titles, exact head/base refs, head SHAs, draft/mergeability *observations*, and exact changed paths in the eight machine-readable shards below.
- Computed overlapping paths and non-main dependency edges in `KUSANAGI_CXXXIV_OVERLAP_GRAPH.json`. **File overlap does not prove a merge conflict or equivalence.**
- Repaired CI lint on existing PR #119 in commits `4ad9930ba20e44a368ca6f2839bc21786b26fb77` and `91e10e8cc9e5b4018ffdbde2de500df78b296998`; GitHub Actions **CI / Canonical Railway image / independent-runner smoke** reported **success** on the latter exact commit. These checks do not constitute independent security review or deployed Railway proof.

## Snapshot totals
| Measurement | Count |
| --- | ---: |
| Open PRs inventoried | 78 |
| Draft | 69 |
| Non-draft | 9 |
| Targeting main | 61 |
| Targeting non-main bases | 17 |
| Mergeability observed as false | 17 |
| Changed-file occurrences across PRs | 981 |
| Distinct file paths | 422 |

> GitHub mergeability is an ephemeral API observation, **not** a green light to merge; every candidate must be retested against updated `main`. No PR has been classified as genuinely superseded without code-level proof.

## Documented inventory
- [Shard 01](cxxxiv_open_pr_shard_01.json) — exact PR metadata + changed paths
- [Shard 02](cxxxiv_open_pr_shard_02.json) — exact PR metadata + changed paths
- [Shard 03](cxxxiv_open_pr_shard_03.json) — exact PR metadata + changed paths
- [Shard 04](cxxxiv_open_pr_shard_04.json) — exact PR metadata + changed paths
- [Shard 05](cxxxiv_open_pr_shard_05.json) — exact PR metadata + changed paths
- [Shard 06](cxxxiv_open_pr_shard_06.json) — exact PR metadata + changed paths
- [Shard 07](cxxxiv_open_pr_shard_07.json) — exact PR metadata + changed paths
- [Shard 08](cxxxiv_open_pr_shard_08.json) — exact PR metadata + changed paths

## Highest-overlap source paths
| File | Open PRs touching file |
| --- | ---: |
| `aurex/api.py` | 22 |
| `aurex/database.py` | 11 |
| `website/docs/aurex-api/openapi.yaml` | 11 |
| `website/src/lib/aurex-client.server.ts` | 10 |
| `website/src/lib/aurex-api-schema.ts` | 9 |
| `website/src/lib/aurex-service.server.ts` | 9 |
| `tests/test_kusanagi_workflow.py` | 7 |
| `aurex/fenced_worker.py` | 6 |
| `integrations/kusanagi-xvi/backend/app.py` | 6 |
| `pyproject.toml` | 6 |
| `aurex/experiments/admission.py` | 6 |
| `aurex/folio_index.py` | 5 |
| `integrations/kusanagi-xvi/backend/Dockerfile` | 5 |
| `tests/test_folio_index.py` | 5 |
| `website/src/components/aurex-capabilities.test.ts` | 5 |

## Critical current mainline fork
- **#97** (`f44571a463ea46cd00c25bb1f672dd5fe6e9e382`): 84 changed files, five observed workflows success, independent review NOT RUN. Candidate for code-level reconciliation; *not* automatic admission.
- **#117** (`82d70c0da20ba5128c48c254987cb433ddae6b35`): foundational CXXVII reconstruction, five observed workflows success; draft.
- **#118** (`6adc1936d09534b134182e769f88fea9c5a0125a`): queued synthetic audit/receipt chain built on #117; four observed workflows success; draft.
- **#119** (`91e10e8cc9e5b4018ffdbde2de500df78b296998`): canonical schema gate plus recovered legacy runtime; CI repaired and three workflows success; draft. Local Chromebook tests *previously reported* 446 passed before the lint-only patch; new full suite requires exact-head proof from CI.
- **#120** (`3e7ce03d72031e048f0101e3484f176b56b542fa`): separate read-only schema preflight. Three observed workflows success; review for unique benefit vs #119 before incorporation; draft.
- #97 and #117/#119 have diverged histories; dependency chain #117 → #118 → #119, with #120 a sibling of #119. Cherry-pick/reconstruct on latest `main` with tests rather than stacking branches blindly.
- Railway staging was observed building older `work/kusanagi-xxiv-cxxviii-convergence`; current staging does **not** establish #119 deployment. Staging and production report the same logical volume ID; physical isolation is NOT VERIFIED. All deployment / migration authority HOLD.

## Mainline admission runbook
1. **Freeze exact heads.** Fetch latest `main`, inspect all PR metadata, changed paths, patches, issue/review threads, and exact-head CI. Reject stale snapshot if any head moved.
2. **Independent review.** Security reviewer checks auth, receipts, integrity, SQLite lease generation, idempotency collisions, subprocess lifecycle, environment gates, dependency provenance, and API/browser credential boundaries. No self-witness.
3. **Order by code dependencies.** Evaluate foundational verified code first; reconcile #97 with #117, then #118, then #119 + unique tested #120. Respect the non-main base edges in the overlap graph. Do not cherry-pick the same content twice.
4. **Small PR batches.** Establish a fresh isolated worktree against the latest `main` for each separate change; preserve original PR identity and why code was accepted or rejected. Avoid blanket `git merge` across 78 branches.
5. **Exact-head validation.** Run Ruff, MyPy, full pytest, relevant website Bun tests/build, auth/worker/receipt adversarial tests, and Docker build as appropriate. Hold if red or not run. A passing old head SHA never proves new merged source.
6. **One verified merge at a time.** Obtain required independent approval. Merge only where authorized; immediately fetch new `main` and rerun tests/recheck downstream PRs. Do not bypass branch protections.
7. **Backlog closure.** Before closing any source PR as superseded, prove and record equivalent behavior on current `main`, tests, merge SHA, and reviewer. Obsolete docs/unsafe code may be rejected but require a written rationale.
8. **No deployment in this wave.** After mainline code convergence, perform separate Railway volume isolation, disposable staging schema admission, restore/rollback rehearsal, owner-only website end-to-end synthetic audit; production remains HOLD.

## PR register (live metadata inventory, not approval)
| PR | Workstream | Draft | Base | Changed files | Current disposition |
| ---: | --- | :---: | --- | ---: | --- |
| #120 | Financial/worker/mainline | yes | `work/kusanagi-cxxix-staging-convergence` | 5 | REVIEW_REQUIRED |
| #119 | Financial/worker/mainline | yes | `work/kusanagi-cxxix-staging-convergence` | 12 | REVIEW_REQUIRED |
| #118 | Financial/worker/mainline | yes | `work/kusanagi-cxxvii-remote-recovery` | 10 | REVIEW_REQUIRED |
| #117 | Financial/worker/mainline | yes | `main` | 62 | REVIEW_REQUIRED |
| #115 | Research/models | yes | `work/kusanagi-xxiv-cxxviii-convergence` | 4 | REVIEW_REQUIRED |
| #114 | Research/models | yes | `work/kusanagi-xxiv-cxxviii-convergence` | 7 | REVIEW_REQUIRED |
| #113 | Docs/tooling | yes | `work/kusanagi-xxiv-cxxviii-convergence` | 3 | REVIEW_REQUIRED |
| #112 | Financial/worker/mainline | yes | `work/kusanagi-cxxviii-unix-worker-python-labs` | 10 | REVIEW_REQUIRED |
| #111 | Financial/worker/mainline | no | `candidate/aurex-ox-24x7-agent-20261022T162607Z` | 11 | REVIEW_REQUIRED |
| #110 | Financial/worker/mainline | yes | `integration/kusanagi-xvi-railway` | 17 | REVIEW_REQUIRED |
| #109 | Financial/worker/mainline | yes | `main` | 10 | REVIEW_REQUIRED |
| #108 | Financial/worker/mainline | yes | `main` | 7 | REVIEW_REQUIRED |
| #107 | Research/models | yes | `work/kusanagi-cxvii-contract-sqlite-proof` | 5 | REVIEW_REQUIRED |
| #106 | Research/models | yes | `main` | 5 | REVIEW_REQUIRED |
| #105 | Docs/tooling | yes | `main` | 2 | REVIEW_REQUIRED |
| #104 | Financial/worker/mainline | yes | `main` | 17 | REVIEW_REQUIRED |
| #103 | Finance/commercial | yes | `main` | 3 | REVIEW_REQUIRED |
| #102 | Research/models | yes | `main` | 3 | REVIEW_REQUIRED |
| #101 | Finance/commercial | yes | `main` | 3 | REVIEW_REQUIRED |
| #100 | Finance/commercial | yes | `main` | 2 | REVIEW_REQUIRED |
| #99 | Financial/worker/mainline | yes | `main` | 28 | REVIEW_REQUIRED |
| #97 | Financial/worker/mainline | no | `main` | 84 | REVIEW_REQUIRED |
| #96 | Financial/worker/mainline | yes | `main` | 43 | REVIEW_REQUIRED |
| #95 | Financial/worker/mainline | yes | `main` | 4 | REVIEW_REQUIRED |
| #94 | Financial/worker/mainline | yes | `main` | 8 | REVIEW_REQUIRED |
| #93 | Financial/worker/mainline | yes | `main` | 7 | REVIEW_REQUIRED |
| #92 | Docs/tooling | yes | `main` | 4 | REVIEW_REQUIRED |
| #90 | Finance/commercial | yes | `main` | 3 | REVIEW_REQUIRED |
| #89 | Finance/commercial | yes | `main` | 17 | REVIEW_REQUIRED |
| #88 | Finance/commercial | yes | `main` | 3 | REVIEW_REQUIRED |
| #86 | Research/models | yes | `feature/kusanagi-xcv-helsinki-delhi-alignment` | 12 | REVIEW_REQUIRED |
| #85 | Research/models | yes | `feature/kusanagi-xciv-local-qwen-fullstack-readiness` | 5 | REVIEW_REQUIRED |
| #84 | Research/models | yes | `main` | 12 | REVIEW_REQUIRED |
| #83 | Financial/worker/mainline | yes | `main` | 6 | REVIEW_REQUIRED |
| #82 | Financial/worker/mainline | yes | `fix/kusanagi-lxxvi-five-gate-contract` | 6 | REVIEW_REQUIRED |
| #81 | Research/models | yes | `main` | 7 | REVIEW_REQUIRED |
| #80 | Finance/commercial | yes | `main` | 8 | REVIEW_REQUIRED |
| #79 | Docs/tooling | yes | `main` | 3 | REVIEW_REQUIRED |
| #78 | Docs/tooling | yes | `main` | 2 | REVIEW_REQUIRED |
| #77 | Finance/commercial | yes | `main` | 2 | REVIEW_REQUIRED |
| #76 | Docs/tooling | yes | `main` | 5 | REVIEW_REQUIRED |
| #73 | Docs/tooling | yes | `main` | 1 | REVIEW_REQUIRED |
| #72 | Financial/worker/mainline | yes | `main` | 8 | REVIEW_REQUIRED |
| #70 | Finance/commercial | yes | `main` | 5 | REVIEW_REQUIRED |
| #67 | Finance/commercial | yes | `main` | 3 | REVIEW_REQUIRED |
| #66 | Financial/worker/mainline | yes | `main` | 3 | REVIEW_REQUIRED |
| #63 | Research/models | yes | `main` | 5 | REVIEW_REQUIRED |
| #62 | Docs/tooling | yes | `main` | 3 | REVIEW_REQUIRED |
| #61 | Financial/worker/mainline | yes | `main` | 4 | REVIEW_REQUIRED |
| #60 | Financial/worker/mainline | yes | `main` | 2 | REVIEW_REQUIRED |
| #56 | Research/models | yes | `main` | 5 | REVIEW_REQUIRED |
| #51 | Research/models | yes | `main` | 3 | REVIEW_REQUIRED |
| #50 | Finance/commercial | no | `main` | 2 | REVIEW_REQUIRED |
| #45 | Docs/tooling | yes | `main` | 1 | REVIEW_REQUIRED |
| #44 | Financial/worker/mainline | yes | `main` | 8 | REVIEW_REQUIRED |
| #43 | Docs/tooling | yes | `main` | 1 | REVIEW_REQUIRED |
| #42 | Docs/tooling | yes | `main` | 2 | REVIEW_REQUIRED |
| #41 | Financial/worker/mainline | yes | `main` | 5 | REVIEW_REQUIRED |
| #39 | Financial/worker/mainline | yes | `main` | 6 | REVIEW_REQUIRED |
| #38 | Financial/worker/mainline | yes | `main` | 4 | REVIEW_REQUIRED |
| #37 | Financial/worker/mainline | yes | `aurex-mainline-convergence-5126581965977077235` | 3 | REVIEW_REQUIRED |
| #36 | Research/models | yes | `work/kusanagi-xlv-international-eval-adapters` | 4 | REVIEW_REQUIRED |
| #34 | Docs/tooling | yes | `main` | 1 | REVIEW_REQUIRED |
| #32 | Financial/worker/mainline | yes | `main` | 5 | REVIEW_REQUIRED |
| #31 | Docs/tooling | yes | `main` | 2 | REVIEW_REQUIRED |
| #30 | Financial/worker/mainline | yes | `main` | 96 | REVIEW_REQUIRED |
| #29 | Financial/worker/mainline | no | `main` | 93 | REVIEW_REQUIRED |
| #28 | Financial/worker/mainline | yes | `main` | 94 | REVIEW_REQUIRED |
| #27 | Financial/worker/mainline | no | `main` | 4 | REVIEW_REQUIRED |
| #20 | Financial/worker/mainline | no | `main` | 33 | REVIEW_REQUIRED |
| #14 | Research/models | yes | `feature/aurex-local-inference-hardening-v1` | 9 | REVIEW_REQUIRED |
| #13 | Research/models | no | `feature/hle-practice-lab-v1` | 5 | REVIEW_REQUIRED |
| #12 | Research/models | yes | `main` | 8 | REVIEW_REQUIRED |
| #11 | Research/models | yes | `main` | 5 | REVIEW_REQUIRED |
| #8 | Research/models | yes | `main` | 1 | REVIEW_REQUIRED |
| #5 | Research/models | no | `main` | 27 | REVIEW_REQUIRED |
| #4 | Research/models | no | `main` | 6 | REVIEW_REQUIRED |
| #3 | Research/models | yes | `main` | 47 | REVIEW_REQUIRED |

## CUSTOS status
- Inventory completeness: **PASS**, 78/78 API changed-file inventories and metadata entries.
- Overlap analysis: **PASS**, source-level file/path overlap only.
- PR #119 GitHub Actions at `91e10e8`: **3/3 observed SUCCESS**.
- Functional equivalence of old PRs to current main: **NOT VERIFIED**.
- Comprehensive diff-by-diff review of 78 PRs: **NOT RUN**.
- Independent reviewer approval: **NOT RUN**.
- New merges into protected `main`: **NONE**.
- Railway staging financial integration: **NOT VERIFIED**.
- Production deployment/release: **HOLD**.
