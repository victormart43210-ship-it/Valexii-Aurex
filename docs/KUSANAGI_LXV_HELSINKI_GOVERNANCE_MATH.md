# KUSANAGI LXV — VALEXII Original Governance Mathematics

**Status: isolated implementation candidate.** This original Python code is inspired by well-established public mathematical ideas documented by University of Helsinki educational/research sources. The course material, code, exercises, illustrations, training data and model weights are **not copied or ingested**.

## Canonical integration boundary

`Evidence → Qualification → Reality → Authority → Effect`

`aurex/governance_math/` is a **non-executing research/advice layer** of the existing canonical AUREX backend. No new database, frontend, model provider, worker, or autonomous agent is introduced. An **opt-in, bearer-authenticated read-only HTTP advisory route** is added, disabled by default. Existing `aurex/evals/statistical.py`, `aurex/evals/four_arm.py`, `aurex/evals/governance.py`, `aurex/experiments/admission.py`, and `aurex/experiments/remediation.py` remain authoritative for their own jobs, signed admission and immutable experiment lineage. The research layer does not compete with them or grant authority.

| Original VALEXII component | Implemented module | Complementary mathematical technique |
| --- | --- | --- |
| Evidence/Context index | `retrieval.py` | sparse sublinear TF-IDF, cosine similarity, nearest neighbor; dedupe source family |
| CUSTOS independent evaluation | `calibration.py` | Brier, log loss, ECE/reliability, time-split prior-only baseline, lineage leakage HOLD |
| Bayesian next test | `information_gain.py` | exact binary Shannon EIG, sensitivity/specificity, budget/risk admission |
| Outcome→Fix chooser | `optimization.py` | bounded exhaustive search, prerequisite DAG, conflict/lineage filters, exact $0 default |
| Unified Reasoning Spine | `spine.py` | retrieve → safe candidate plan → optional test-next, full provenance/status |
| Offline script | `__main__.py` | local read-only JSON analysis, no network/auto-run |

### Honest claims

- Each module emits `ANALYSIS_ONLY`, `ADVISORY`, `NOT VERIFIED`, `REVIEW_REQUIRED` or `HOLD`, never independent PASS.
- Bayesian frequency counts and probe `calibration_reviewed` flags are **caller assertions**. They do NOT independently prove admission, signed witnesses, source independence, model calibration or authority. An authenticated adapter must verify origin and experiment admission before supplying any actual incident histories.
- TF-IDF similarity is not a probability of successful remediation and does not assess truth.
- Even a perfectly-ranked algorithm may fail; optimization is exact only over the **bounded supplied candidates and stated heuristic**, never all possible fixes.
- Empty, unsafe, costly, cyclic, unreversible or out-of-scope fixes do not execute; unknown outcome means HOLD.
- Bayesian Beta(1,1) conservative ranking is explicitly a *heuristic lower estimate*, not a frequentist confidence interval or a validated success probability.
- Prior-only baseline is fitted to **past records with labels observed by the cutoff only**; future-resolved labels are rejected as hindsight leakage. Every Prediction needs timezone-aware predicted_at and outcome_observed_at timestamps. Brier improvements on held-out future labeled events remain *diagnostics*, not independent verification or model superiority.
- Information gain only works when sensitivity/specificity are externally calibrated and an actual test exists; do not manufacture loss curves, GPU usage or model training percentages.
- No auto-merge, auto-code editing, production remediation, token costs, budget increase, deployment or website changes.

### Example local-only input

Save JSON locally as `/tmp/aurex-research-input.json` (illustrative synthetic entries, NOT an actual incident record):

```json
{
  "problem_code": "TEST_FAILURE",
  "description": "strict type checking failed in an isolated Python branch",
  "fixes": [{
    "key": "correct_type_contract",
    "problem_code": "TEST_FAILURE",
    "lineage_group": "exact-branch-1",
    "fix": ["Prepare isolated minimal correction to failing types"],
    "verify": ["Rerun mypy, Ruff, pytest and independent exact-SHA review"],
    "rollback": ["Revert candidate patch and preserve failing diagnostics"],
    "minutes": 15,
    "risk": 1,
    "cost_usd": "0",
    "impact": 8
  }]
}
```

Then:

```bash
python -m aurex.governance_math --input /tmp/aurex-research-input.json
python -m pytest -q tests/test_governance_math.py
ruff check aurex/governance_math tests/test_governance_math.py
mypy aurex
```

Output proposes the best eligible *known* fix immediately next to its observed problem and gives verification/rollback instructions; nothing runs automatically. Strict source provenance/authorization still belongs to the existing signed independent `decide_admission` and release-control workflow.

## OX tab mapping (NO LOVABLE CHANGE IN THIS PR)

1. **Intelligence Map / Nexus**: genuine indexed source/capability graph, no implied edges.
2. **Execute / Jobs**: ranked reversible actions and real execution status, if backend jobs are actually instrumented.
3. **Evidence / Context**: case matches with immutable SHA/source family; analysis != current verification.
4. **Agents**: only trace real Advocate/Challenger/Arbiter outputs when backend exposes them; otherwise NOT INSTRUMENTED.
5. **Models**: report evaluation calibration, Brier, log loss only for independently sourced labeled datasets; otherwise NOT INSTRUMENTED.
6. **Security**: HOLD / scoped authorization / harm, privacy and fairness reviews.
7. **Analytics**: real heldout and prior-only scores with counts, calibration and abstentions when data available.
8. **Nexus**: explicit lineage and integration evidence only.

**Implemented but disabled-by-default service route:** `POST /v1/research/advice` (computational read-only operation). Requires the existing server-side AUREX bearer authentication **and** `AUREX_ENABLE_RESEARCH_ADVICE=1`, which is not set by this PR. All lists and strings are strictly bounded; no API route writes jobs, runs models, accepts self-asserted calibrated-probe flags, or grants authority. The bearer is *service authentication*, not a new owner identity system; Lovable must continue its own server-side owner check before any owner access. The route must NOT be exposed on the public page and deployment must remain HOLD pending independent auth/contract review. Future owner-only versioned retrieval of stored advice/evaluation artifacts remains NOT IMPLEMENTED. Do **not** add to Lovable until the lagging Ouroboros P0 performance repair is complete and its five-credit cap is respected. UI animation has **ORB MOTION AUTHORITY = NONE**.

## Research/education source and IP boundaries

- University open-course overview: https://www.helsinki.fi/en/admissions-and-education/open-university/multidisciplinary-themed-modules/artificial-intelligence-collection
- Building AI course: https://buildingai.elementsofai.com/ (optimization, hill climbing, Bayes, regression, overfitting, NN)
- University Probabilistic ML: https://www.helsinki.fi/en/researchgroups/probabilistic-machine-learning/research-overview
- Multi-source Bayesian inference: https://www.helsinki.fi/en/researchgroups/multi-source-probabilistic-inference/research
- Trustworthy ML: https://www.helsinki.fi/en/researchgroups/trustworthy-machine-learning/research
- Ethics of AI: https://ethics-of-ai.mooc.fi/ and licensing https://ethics-of-ai.mooc.fi/about/
- Elements of AI legal terms: https://www.elementsofai.com/terms-of-service

**No course material, test items, model weights or private datasets are imported**. `Elements of AI`/`Building AI` restrict commercial copying; `Ethics of AI` CC BY-NC-SA does not allow unrestricted commercial reproduction. All mathematical formulas implemented independently using Python standard library. No claims of university endorsement or affiliated research.

## Remaining CUSTOS gates

1. Exact-branch CI Ruff + strict Mypy + Pytest PASS, then independent external review.
2. Qualified, signed incident/admission adapter built separately (never accept booleans as trust).
3. Holdout dataset authorization, contamination checks, calibration, false-remediation rate, baseline comparison.
4. Agent/worker permissions, idempotency, lease fencing and rollback if an executor is ever proposed.
5. Authenticated `/v1/research/advice` contract review, independent API smoke, production deployment/exact SHA and live owner-only browser integration: **HOLD**.
