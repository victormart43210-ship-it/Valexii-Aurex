# KUSANAGI CLVI — Parallel incremental integration lane

Status: **SCAFFOLD / NO RUNTIME ADOPTION**. This plan runs in parallel with the industrial audit convergence without blocking it.

## Two parallel lanes, one protected main

- **Lane A — commercial critical path (70%):** repair industrial-audit CI, reconcile towing/oilfield audit contracts, validate Railway staging against exact deployed SHA, and test VALEXII → XAELI → AUREX with synthetic data. Owners: Copilot implementation; Jules independent review; Work staging verification.
- **Lane B — incremental external pattern admission (20%):** build *test-only* safety-evaluation interface, then benchmark OpenJudge, then trial Qwen Code for bounded PR creation. Owner: separate agent/worktree with exclusive file ownership; independent reviewer cannot be implementer.
- **Lane C — bounded exploration (10%):** investigate AgentScope observability patterns; postpone ReMe and SEA-LION until a concrete requirement. No new service or runtime dependencies by default.

## Dependency and merge gates

1. Each agent fetches fresh `main`, records exact base SHA, and creates `work/<operation>-<agent>-<scope>` from that SHA. Do not base implementation on this research branch.
2. Freeze shared API contracts first. Lane B initially owns **only** `aurex/evals/external_safety_contract.py`, `tests/test_external_safety_contract.py` and `docs/verification/*` (adjust paths if conflicting; declare before edits). Lane A owns industrial audit modules/tests and website integration. No overlapping writes.
3. Phase B0: design typed evaluation contract, *no network access or third-party dependencies*. Evaluation input: synthetic case ID, fixture hash, scenario and safety property. Output: verdict `PASS|FAIL|NOT_RUN|NOT_VERIFIED`, tool/version, exact source SHA, independent reviewer ID, optional receipt reference, and explanation. Missing evidence or evaluator failure MUST NOT yield PASS.
4. Phase B1: deterministic tests with injected mock evaluator covering injection, missing auth, tenant isolation, stale evidence, unsupported claims, error paths and cancellation; CI must not require provider keys.
5. Phase B2: optional Moonshot runner in isolated CI, behind opt-in feature flag and fixed cost budget. Keep the contract provider-neutral.
6. Phase B3: optional OpenJudge adapter for explanation quality; no model judge grants compliance or production authority. Benchmark against deterministic ground truth and require separate reviewer.
7. Phase C1: Qwen Code isolated trial produces reviewable PRs only; no main merges, production deployment, customer data or credential access.
8. AgentScope, ReMe and SEA-LION remain research-only until observed need, licensing/SBOM review, data residency/privacy review, and resource budget.

## Merge and release discipline

- Each lane opens its own PR to protected `main`. Never bulk merge.
- Review by a different agent/model family, reproduce tests at **exact head SHA**, rebase to latest main, rerun CI, then request approval.
- Staging release needs a separately authorized deployment and exact SHA verification. Production remains HOLD.
- Existing industrial audit routes, tokens, receipts, tenant isolation and website visuals must remain unchanged by Lane B.
- Do not spend Lovable credits or activate paid inference without explicit approval.

## Metrics to justify each increment

| Gate | Measurable acceptance |
| --- | --- |
| Industrial audit | Synthetic towing and oilfield E2E complete on deployed SHA; auth/tenant/evidence checks reproducible |
| Safety contract | 100% of negative fixture cases fail closed; test runner works offline with $0 provider spend |
| Moonshot | Reproducible versioned red-team report; compare findings to baseline and triage false positives |
| OpenJudge | Measured judge agreement with independent ground truth; no self-witness |
| Qwen Code | Compare time-to-reviewed-PR, CI pass rate, defects and dollar cost vs existing workflow |
| Future adapters | Positive pilot business case, security approval and explicit ownership |

## Rollback

Keep each adapter opt-in, removable, and isolated. On regression, disable the adapter, preserve failure receipts, revert its PR if necessary, and continue Lane A without interruption.

## Next implementation instruction

On a **fresh branch from main**, implement **only Phase B0/B1** as a provider-neutral offline contract and tests. Do not introduce Moonshot/OpenJudge packages yet. Report tests and exact SHA; open PR; request independent review. Continue Lane A in parallel.
