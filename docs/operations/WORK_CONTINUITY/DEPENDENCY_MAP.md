# Engineering ownership and integration dependencies

| Owner | Branch / PR | Owned area | Work boundary |
|---|---|---|---|
| Cursor | cursor/fail-closed-audit-fixes-4082 #170; cursor/kusanagi-ccxxxiv-sovereign-beta-4082 #171 | evidence_kernel, receipt/store, intelligence/pilot, ingestion/monitor, console; CCXXXV planned OCR/hours/persistence | Read and test pinned SHA; no runtime rewrites |
| Jules | work/kusanagi-ccxxxii-pipeline-1185966213576242581 #172 | envelope/international/pipeline/monitoring/API and frontend timeout fix | Read and test; overlapping pipeline must be reconciled before integration |
| Earlier agent | work/ccxxix-evidence-enforcement #168 | v2 receipt/recovery claims/quarantine/frontend | Review input only; overlaps #171 |
| Earlier agent | work/ccxxxi-international-pipeline-contract #169 | contract docs | No automatic runtime integration |
| ChatGPT Work | work/ccxxxvi-continuity-verification | WORK_CONTINUITY, CHATGPT_WORK_HANDOFF, uniquely named verification fixtures/harness | No edits to Cursor/Jules handoffs or active files |
| Earlier Work session | work/kusanagi-ccxxv-sovereign-convergence local | historical recovery, prototype kernel/outcomes/store/UI | Superseded; archive separately, never merge blindly |

Shared contracts: tenant authorization, evidence qualification, receipt versions, decimal money, synthetic-only admission. #171 contains #170. #172 is a sibling candidate from main; concurrent edits to intelligence/API create integration risk. Exact conflict status must be measured, not assumed. No merge/rebase planned. Review and artifact-only branch is conflict safe.
