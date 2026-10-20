# KUSANAGI LV — Workflow Quality Gates

This policy supplements [AGENT_MAINLINE_POLICY.md](AGENT_MAINLINE_POLICY.md). A target of **9.9/10** is aspirational until measured; do not label it achieved without independent evidence.

## Single authority and branch discipline
- Canonical repository: `victormart43210-ship-it/Valexii-Aurex`; `main` is authoritative.
- Every agent records fresh `origin/main` SHA and creates an isolated branch from it.
- One integrator serializes reviewed merges. Legacy and draft PRs are inputs, not branch bases.
- File ownership and frozen API contracts precede parallel agent work. Disagreements trigger independent review, not forced consensus.
- Do not overwrite uncommitted Chromebook work or force-sync local clones.

## Mandatory PR evidence
Each PR description or attached release report must provide:
1. Base SHA and candidate head SHA; changed files and declared owner.
2. Contract impact, threat model, failure modes, and rollback procedure.
3. Reproducible tests with command, exit code, exact SHA, and failures.
4. Independent review of security-critical code, including worker claims, fencing, cancellation, evidence integrity, and authentication.
5. API compatibility proof for the deployed frontend; no browser-side service secrets.
6. Status for each requirement: PASS, FAIL, NOT RUN, or NOT VERIFIED.

## Merge and deploy separation
- Require green CI on the **exact head SHA**, resolved conflicts, approved review, and completed tests before merge. A blank commit-status response is NOT VERIFIED.
- Protect `main` with required checks and review via repository settings; this document alone cannot enforce branch protection.
- Merge only after explicit authorization. Re-fetch `main` and rerun dependent tests afterward.
- Deployment is a separate, explicitly authorized operation. A successful merge is not proof of live functionality.
- Production admission requires observed end-to-end authenticated website → API → worker → evidence flow and independent verification.

## Chromebook reconciliation
Run a read-only local inventory before claiming synchronization: clone path, remote URL, branch, HEAD, dirty status, Python/Node versions, dependencies, and listening ports. Compare to GitHub and preserve all uncommitted changes. Do not assert Chromebook alignment without actual local output.

## $0 default and security boundaries
- No paid provider calls, Lovable credit usage, deployment, or external spend without separate authorization.
- Preserve Evidence → Qualification → Reality → Authority → Effect; unknown is not healthy; a worker cannot certify its own evidence.
- Disabled/unavailable workers fail closed; historical evidence is distinct from current authority.

## Measurable workflow scorecard (rolling 10 PRs)
Record numerator, denominator, and exact evidence for:
- Fresh-main branch compliance: target 100%.
- Exact-head CI pass before merge: target 100%.
- Independent review for security-critical PRs: target 100%.
- No unapproved merges or deployments: target 100%.
- Contract tests on backend/frontend changes: target 100%.
- Chromebook drift checks before local integration: target 100%.
- Escaped critical regressions: target 0.
- Median time from PR ready to independently verified: track baseline, then improve.
- Open conflicting implementation branches: track and reduce.

**Release gate:** HOLD whenever any required evidence is missing, stale, or unverified.
