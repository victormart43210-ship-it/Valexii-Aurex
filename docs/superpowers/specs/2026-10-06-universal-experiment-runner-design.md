# AUREX Universal Experiment Runner — Design Specification

**Date:** 2026-10-06
**Status:** DESIGN APPROVED IN CONVERSATION; SPEC AWAITING REVIEW
**Canonical doctrine:** [ARCHITECTURE_LOCK_V1.md](../../ARCHITECTURE_LOCK_V1.md)
**Repository:** `victormart43210-ship-it/Valexii-Aurex`
**Branch:** `aurex-hle-readiness`

## 1. Purpose and non-goals

Build a provider-neutral, locally executable Universal Experiment Runner (UER) that powers HLE-style exams, decipherment hypothesis tests (Voynich, Linear A, Rongorongo), 4D-lattice ablations, agent orchestration, mathematics and algorithm comparisons through the *same* evidence lifecycle. Its first deliverable is a **synthetic fixture runner** that demonstrates fail-closed grading, immutable experiment records and independently checked results; it does not claim that real HLE or historical decipherment benchmarks ran.

AUREX is a witness, never a truth or authority owner. UER will not rewrite BCXMET runtime authority, certify a breakthrough, access proprietary corpora without authorization, fetch concealed HLE answers, or quietly accept an AI-generated answer as its own proof.

## 2. Alternatives evaluated and decision

- **Separate runner per research track:** quick to prototype but creates inconsistent evidence and incomparable status rules. Rejected.
- **One monolithic evaluator:** shared metrics but evaluator/runner entanglement permits accidental self-grading and increases audit complexity. Rejected.
- **Small canonical orchestration core + versioned track adapters + external verifier boundary:** selected. Shared immutable contracts and lifecycle; track-specific semantics remain explicit, with separate independent verification.

## 3. Inputs and contracts

Each experiment is identified by an immutable `experiment_id` and a canonical SHA-256 digest of a versioned manifest (deterministic JSON encoding; exclude mutable status timestamps). A manifest declares:
- schema version, track name, benchmark/dataset revision and checksum, stable unique item IDs, explicit data authorization state;
- frozen baseline and experimental arm identifiers plus model/provider versions and generation parameters;
- prompt, tool, scoring protocol and execution-config digests;
- an independent verifier specification (identity, provenance, independence relation to generating models, reference-access policy);
- leakage/contamination policy, resource/time/cost bounds and planned metric definitions;
- selected ablation(s) and preregistered success/failure thresholds.

Validation rejects missing or empty identifiers, duplicate IDs, invalid digests, unknown track names, out-of-bound resource settings, incongruent manifest version, or incomplete frozen settings. Track adapters **must not** edit the manifest or fabricate outside anchors.

## 4. Core boundaries

**Manifest Validator** checks schema and stability; declarations such as `dataset_authorized=true` are never treated as proof of permission.

**Execution Coordinator** schedules baseline and AUREX arms against the same item set using frozen settings; bounded retries and error recording; provider adapters may produce proposed answers but never grades or PASS.

**Track Adapter** transforms authorized inputs into track-specific tasks and returns candidate outputs/metrics. Initial adapter implements only synthetic deterministic fixtures. Subsequent adapters add HLE protocol compatibility, decipherment holdout testing, lattice invariants/ablations, orchestrator comparisons, mathematical proof checking and algorithm correctness/complexity comparisons.

**Evidence Store** is append-only with canonical hashes, parent event pointers, UTC timestamps, source identity and recorded environment/version fingerprints. Previous FAIL records stay intact after remediation, revocation or re-execution. Any modification/corruption fails validation. A hash chain alone is integrity detection, not authenticated provenance; external signatures and trusted storage are separate requirements.

**Independent Verification Gateway** accepts separately sourced grader/validator attestations tied to exact experiment/manifest/item/run digests. Mismatched identities, same-actor self-witness, missing signatures where configured, insufficient attestations, stale references or unverifiable grading → HOLD / NOT VERIFIED, never PASS.

**Promotion Gate** maintains distinct *experiment lifecycle*, *result*, and *admission* states. A model-generated `SUPPORTED` challenge finding is not a benchmark PASS. Only separately verified results can progress beyond EXPERIMENTAL.

## 5. Lifecycle and error semantics

1. VALIDATE manifest and freeze baseline/experimental arm definitions.
2. RUN paired items, capturing per-arm outputs, token/resource/cost/latency accounting and failures.
3. NORMALIZE evidence into append-only events, preserve raw errors without exposing credentials.
4. REQUEST independent verification; verifier cannot be the sole source of the claim being checked.
5. CHALLENGE completeness, leakage, contamination, independence and baseline comparability.
6. If FAIL: open remediation case bound to original immutable failure event, capture proposed root cause and candidate fix.
7. RETEST on a frozen or properly versioned blind set; append the retest event, never replace original FAIL.
8. REPLICATE with separate execution environment and qualified independent evaluator.
9. PROMOTE only on admissible evidence.

States: `PASS`, `FAIL`, `HOLD`, `NOT RUN`, `NOT VERIFIED`. Never infer PASS from missing test results, resource exhaustion, API failure, an untrusted manifest flag, or a model's self-report.

## 6. Scoring, baselines and statistical discipline

- Preserve original correct/incorrect counts and per-item discordances in paired benchmarks.
- Report accuracy, percentage-point delta and relative uplift separately, with uncertainty and paired significance where sample size permits.
- Track coverage, abstention, calibration, hallucination/citation accuracy, regressions, latency and costs.
- In decipherment, score independently anchored predictions and held-out phenomena; document non-testable hypotheses as INSUFFICIENT, never assign translation accuracy against invented ground truth.
- Compare 4D vs 2D/3D/non-lattice baselines; orchestration vs single-agent and no-verifier controls; algorithms vs credible simple baselines.
- Preregister metric definitions and avoid post-hoc cherry-picking. Clearly segregate exploratory and confirmatory outcomes.

## 7. Security and privacy

Use authorized/licensed corpora; no embedded HLE private solutions or patent-sensitive BCXMET internals. Enforce adapter endpoint trust, bounded requests/responses, timeouts, safe subprocess/sandbox limits, input validation and secret redaction. A model cannot access withheld references during answer generation. Independent grader access is scoped after answer freeze. Captured data has retention/export/deletion controls consistent with any applicable permissions.

## 8. First implementation slice (after spec + implementation-plan reviews)

Suggested boundaries:
- `aurex/experiments/contracts.py`: strict manifest, arm, item and event contracts.
- `aurex/experiments/ledger.py`: canonical serialization, append-only hashing and verification.
- `aurex/experiments/runner.py`: bounded paired synthetic execution and recording.
- `aurex/experiments/admission.py`: fail-closed verification and status promotion logic.
- `aurex/experiments/tracks/synthetic.py`: deterministic synthetic track adapter.
- `tests/test_experiment_*.py`: behavior-first tests (red → green), invalid manifests, tamper, missing/forged graders, partial runs, remediation immutability, independent-baseline comparisons.

Existing `aurex/evals/hle_gate.py` remains a structural pair validator, not an official HLE runner. Integration must preserve its conservative status vocabulary and must not retroactively certify prior HLE work.

## 9. Acceptance test matrix (minimum)

| Case | Expected |
| --- | --- |
| Valid synthetic baseline-vs-AUREX paired run | Raw outputs recorded, status NOT VERIFIED until independent validation |
| Missing or duplicated task IDs | HOLD |
| Dataset authorization only self-declared | No independent authorization certification |
| Evidence event tampered with | FAIL integrity check / HOLD admission |
| Generator submits its own verifier decision | HOLD |
| Verifier checks different manifest/run/arm | HOLD |
| No evaluator available / API timed out | NOT VERIFIED or HOLD, not PASS |
| Remediation applied after FAIL | Original FAIL remains immutable; new attempt is linked |
| Hidden reference made available during generation | HOLD contamination |
| Experimental arm produces lower score | Regression recorded honestly |
| Lattice or orchestration claimed advantage without matched baseline | HOLD |
| Decipherment hypothesis fits training glyphs only | No decipherment admission |
| Repeated evidence item counted twice | Reject duplicate |
| Exact SHA CI fails or cannot execute | No release-grade PASS |

## 10. Evidence and exit gates

Development evidence must name the exact SHA and include failing-first tests, full pytest, static checks, packaging/install checks and CI. Independent review is required for safety-critical claims and before merge. Fix the existing failed CI through root-cause evidence, not guesses; if logs cannot be retrieved, record the blocker and obtain alternate reproducible diagnostics.

**Definition of done for initial slice:** deterministic synthetic fixtures can run end-to-end, preserve append-only failure/remediation history, refuse unverifiable admission, produce a machine-readable report and pass verified exact-head tests. This is not synonymous with completing HLE or deciphering a script.

## 11. Change control

The specification can evolve only through reviewed, versioned amendments. Preserve the no-self-witness law, fail-closed status mapping, baseline integrity, immutable historical evidence and independent verification. No merge or production release is implied by writing this document.
