# KUSANAGI LXIV — VALEXII Immediate Remediation Kernel

**Status:** isolated candidate; main and Railway production unchanged. No execution authority.

## Objective

Every detected problem yields, **in the same computation**, a candidate fix immediately after the outcome, independent verification requirements, rollback instructions and contingency handling for every possible *known action result*. Infinite real-world error states cannot be exhaustively predicted: `UNKNOWN` is always mapped to evidence-preserving HOLD rather than a fabricated fix.

The governed Python engine lives at `aurex/remediation.py`.

```bash
python -m aurex.remediation --outcome API_CONTRACT_FAILURE
python -m aurex.remediation --matrix
python -m aurex.remediation --outcome RELEASE_REGRESSION --severity 10
```

Outputs machine-readable JSON, ready for **read-only** display in AUREX/OX. No shell commands are run, no website API is added, and no scripts are executed in the user's environment.

## Mathematical choice

This is a **constrained, conservative Bayesian decision ranking**, not an unrestricted autonomous fixer.

1. **Recognize/classify** outcome into the versioned finite taxonomy.
2. **Safety constraints FIRST**: require reversible action, bounded risk and zero spending by default.
3. **Bayesian evidence**: with successes `s` and failures `f`, use `Beta(1+s,1+f)`. Rank using conservative one-standard-deviation lower bound `p_low=max(0,E[p]-sqrt(Var[p]))`, not an unqualified raw confidence.
4. **Optimization**: rank eligible actions deterministically by `utility = severity × p_low × hypothesized_effectiveness − 0.7×risk − 0.015×minutes`, breaking ties by action key. The expected effectiveness numbers and utility coefficients are **design heuristics only**, NOT benchmarks or calibrated probabilities.
5. **Fix immediately behind detection**: supply ranked fix, independent verification plan, rollback, and a second-stage response table for SUCCEEDED / FAILED / TIMED_OUT / INCONCLUSIVE / CANCELLED / REVOKED / INTEGRITY_FAILED / UNAUTHORIZED / UNKNOWN.
6. **Never self-promote**: even post-action SUCCEEDED means *await independent verification*, never VERIFIED/PASS.

Historical counts supplied to `plan(history=...)` are advisory inputs that are **not verified by the Python module**. Integrating the evidence ledger must authenticate historical samples, bind them to exact SHA and qualification, check correlation, and avoid training on self-reported successes before using them for authoritative reporting.

## Governance contracts

`Evidence → Qualification → Reality → Authority → Effect`.

- **Evidence**: keep finding, source provenance and exact source/deploy SHA.
- **Qualification**: independent auditor reviews input, candidates, and sample histories; unknown != safe.
- **Reality**: check actual deployment/version, constraints, cost budget and whether recovery is possible.
- **Authority**: the planner produces `REVIEW_REQUIRED` or `HOLD`, never write permission.
- **Effect**: a separately authorized, fenced, idempotent executor (not in this PR) may eventually propose a controlled change, run independent tests, then stage a PR; production remains HOLD.
- **ROTAS/CUSTOS**: audit result → authority → truth → admissibility → source; preserve failure history; reject stale evidence and competing self-witnesses.

For repo work, the desired remediation pipeline is:

```text
Problem found
 → capture exact-SHA evidence
 → classify + propose best *eligible* fix in the same response
 → create isolated corrective branch (future adapter)
 → code patch + targeted regression test (future approved executor)
 → run full Ruff/Mypy/Pytest/contract CI
 → independent challenger + CUSTOS
 → approved PR, serialized integration
 → deployment verification and rollback (separate owner authority)
```

For security incidents, integrity failures, invalid authentication, or revoked leases, **containment/HOLD takes precedence over clever optimization**. Do not auto-rotate secrets, disable a production system, retry non-idempotent work, or overwrite evidence.

## Existing systems reused

- Existing `aurex/experiments/remediation.py` models `RemediationCase`, `RetestRecord`, and immutable `compute_lineage_digest` for experiments. The new planner provides **advisory candidate selection only**; it must not replace immutable experiment lineage.
- Existing `aurex/fenced_worker.py` controls leases, cancellation and execution. The planner has no path to `claim_job`/`finalize_job`.
- PR #51 supplies separate Bayesian hypothesis evidence fusion and remains unmerged. The present Beta-Binomial ranking is intentionally independent of that PR to conform with fresh-main isolation.
- PR #50 is a distinct readiness/acceptance gate and should not be conflated with remediation success.

## Next integration gates

1. Independent CI pass against exact candidate SHA; document failed/blocked tests.
2. Add validated evidence-ledger adapters, provenance and outcome-calibration datasets.
3. Benchmark Bayesian ranking against deterministic baselines, real incidents and withheld cases. Report false remediation rates, rollback frequency, latency and resolution success, not imaginary improvement percentages.
4. Introduce typed, domain-specific action contracts only with owner-authorized permissions, idempotency, bounded retries, revocation and independent rollback.
5. Expose results through authenticated AUREX REST endpoint and Lovable server-side proxy only after separate contract review; browser has **no authority**.
6. Add systematic adversarial/fuzz testing for injection, fabricated evidence, correlated confirmations, unknown categories and race conditions.

## Research background

Risk-based incident handling: NIST SP 800-61 Rev. 3 (April 2025), https://csrc.nist.gov/pubs/sp/800/61/r3/final

Supervised progressive rollout and rollback: Google SRE production best practices, https://sre.google/sre-book/service-best-practices/

These are inspiration and design comparisons, not proof this model is superior.
