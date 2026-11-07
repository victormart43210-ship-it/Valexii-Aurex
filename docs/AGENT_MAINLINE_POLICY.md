# AUREX / OX — Canonical Mainline Agent Policy

**Single source of truth:** `victormart43210-ship-it/Valexii-Aurex`, protected `main`.

Every Jules, Cursor, Claude, Grok, Lovable-backend, and ChatGPT coding agent MUST:

1. Fetch `origin/main` immediately before work. Record its exact SHA.
2. Create an isolated `work/<operation>-<agent>-<scope>` branch **from that SHA**. Do not base new tasks on another agent's branch or a stale integration branch.
3. Declare owned files, dependencies, test plan, and expected API contracts before editing. No overlapping parallel writes.
4. Open a PR targeting `main`; no independent production deployments or automatic merges. Rebase on the latest `origin/main` before review and rerun tests after every rebase.
5. Preserve Evidence → Qualification → Reality → Authority → Effect, $0 budget, no self-witness, honest unknown/NOT VERIFIED, and fail-closed worker availability.
6. Independent reviewer checks tests, race/cancel/lease fencing, evidence integrity, CI results and exact head SHA. Only merge when checks PASS and conflicts resolved.
7. Integrator merges **one verified PR at a time** into `main`, then all agents fetch the new `main` SHA before starting the next dependent wave.
8. Lovable frontend changes must match deployed backend contracts; source-code merge is not proof of deployment. Never expose service credentials client-side.
9. Existing legacy branches and open PRs are **review inputs only**, not agent bases. Cherry-pick verified changes or reimplement against fresh `main`.
10. Release/deployment remains HOLD until separate production authorization and observed end-to-end proof.

## Current reconciliation
PR #39 is a draft candidate, not canonical main. Its existence does not override this policy. Resolve worker claim/finalization and test failures before merge. The older #20, #25, #27–32, #34, #36–38 require per-PR disposition; do not bulk merge.

## Required final report
`main_base_sha`, `head_sha`, changed paths, test commands/results, independent reviewer identity, unresolved failures, merge SHA if merged, deploy SHA if deployed, and CUSTOS gate.
