# Cross-lane alignment checkpoint

Observed 2026-10-16 UTC (2026-10-15 America/Chicago). Alignment is PARTIAL; merge/release remains HOLD.

- Canonical repository remains `victormart43210-ship-it/Valexii-Aurex`; no new backend repository or production resource created.
- Main advanced from `c98ca176ee0fb0e2f4a79427d0ee225eca6b0305` to `62d67c7636c58359998268e8e73c853493fb56f8`, including PR26 persistence and PR35 evaluation work. Earlier branch-local tests are not tests of this new main.
- PR28 is our fenced execution/website/analytics candidate. Its dashboard commit `47b7cf39edaa829066c2d0e68a951b0387ac7c04` is already an ancestor of PR29 (`9aa1b0104db0531e0c8513ff68b5442cedf04d0b`), which adds scientific-evidence work. Preserve this lineage; do not duplicate that implementation.
- PR37 (`1d35a83d795850bd04dffff5c02bd9adfdccec75`) targets `aurex-mainline-convergence-5126581965977077235`, not main. Its offline worker delegates to `aurex.atomic_claims.claim_queued_job`. Do not equate this with the PR28 lease/fencing engine without contract reconciliation.
- PR31/34 cover release identity and readiness; PR36 Studio targets the evaluation branch. They remain separate review candidates, not verified integrated capabilities.
- Read-only `git merge-tree --write-tree HEAD origin/main` detected conflicts in `aurex/api.py`, `aurex/database.py`, `aurex/experiments/admission.py`, `tests/test_api.py`, and `tests/test_kusanagi_workflow.py`. No merge or conflict resolution was applied to the working branch.

## Integration order

Freeze one job/schema/claim contract against current main before importing workers or evaluation changes. Reconcile API admission and evidence semantics with PR29/31/34/37; preserve tests from both sides. Bring the owner website bridge and analytics across only after that contract is stable. Apply the separately pinned Lovable route patch to the current source in a controlled preview. Run combined tests and independent security review before any release approval.

## Follow-up recovery evidence

Independent read-only review found that the first backup command accepted an empty database bearing schema version 2. A failing regression reproduced it; the repair checks canonical core column definitions without migrating the source. Independent recheck: 5 focused tests passed. Full local backend: 213 passed, 1 skipped, existing Starlette/httpx warning. Ruff PASS; strict Mypy PASS (44 files). Full schema constraint equivalence, production restore, real Qwen and live website execution remain NOT VERIFIED.

No merge, deployment, DNS change, live migration, credential rotation, public tunnel or paid service was performed. Model output remains advisory; $0 paid-provider default and BCXMET authority boundaries remain unchanged.
