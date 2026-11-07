# KUSANAGI LXVI — Global University Reliability Convergence

**Repository:** the single canonical `victormart43210-ship-it/Valexii-Aurex`.  
**Source base:** `main` SHA `c41675fc0830be5f1b66e2f75782b139668b6cb3`.  
**Status:** isolated draft PR research implementation; does **not** claim trained models, validated statistics, production deployment, or ownership of university IP. No existing backend, worker, Railway, Lovable, or authentication system modified.

## Research coverage (Firecrawl, October 16, 2026)

Reviewed official university pages, original faculty papers, and research material across multiple continents. **Each item is a design inspiration**, not a claim the originating university has collaborated with or endorsed VALEXII.

| University / region | Primary evidence | Complement to our architecture |
| --- | --- | --- |
| Stanford University, USA | [HELM, holistic language-model evaluation](https://crfm.stanford.edu/2022/11/17/helm.html) and [HELM portal](https://crfm.stanford.edu/helm/) | Multiple honest metrics instead of only accuracy and a synthetic combined safety percentage |
| University of California, Berkeley, USA | [Conformal prediction tutorial](https://www.stat.berkeley.edu/~ryantibs/statlearn-s23/lectures/conformal.pdf); [Angelopoulos/Bates notes](https://arxiv.org/html/2107.07511v6) | Abstention and set-valued uncertainty, with **exchangeability assumption explicitly unverified** |
| Carnegie Mellon University, USA | [Anytime-valid sequential inference (Ramdas)](https://stat.cmu.edu/~aramdas/icml25/) | Optional-stopping-aware e-process monitoring for excess false-pass rates |
| Massachusetts Institute of Technology, USA | [Functional clustering of program outputs](https://arxiv.org/html/2506.11021v1), with [MIT CSAIL thesis](https://commit.csail.mit.edu/papers/2025/Chaitanya_Ravuri_MEng_Thesis.pdf) | Compare pre-executed code-candidate behavior; **agreement never proves correctness** |
| University of Oxford (OATML), UK | [Bayesian/inference research publication index](https://oatml.cs.ox.ac.uk/tags/inference.html) | Confidence calibration, hallucination risk and selective model review |
| University of Tokyo, Japan | [Masashi Sugiyama publication record](http://www.ms.k.u-tokyo.ac.jp/sugi/publications.html) featuring deployment distribution shift and importance weighting | Data-shift monitoring; do not apply exchangeability-based guarantees after shift without qualification |
| National University of Singapore | [NUS AI research](https://www.comp.nus.edu.sg/cs/research/ai/) including trustworthy AI, planning and multi-agent systems | Cross-check adversarial and governance architecture; not a copy of NUS implementation |
| University of Cambridge, UK | [Deep ensembles and uncertainty MPhil research](https://www.mlmi.eng.cam.ac.uk/files/2020-2021_dissertations/improving_deep_ensembles.pdf) | Later independent model-uncertainty benchmarking; no models installed or trained |

Additional ETH Zürich/EPFL materials were discovered through search; a selected ETH PDF URL returned a 404 on live fetch. **No conclusions or imported implementation depend on that inaccessible PDF.**

## What we implemented

These are original, standard-library **read-only** Python functions inside the EXISTING `aurex/evals` package:

1. `conformal_guard.py`: split conformal with finite-sample `ceil((n+1)(1-alpha))` calibration quantile and set-valued binary outputs. Insufficient samples for requested tail level => threshold 1 (both labels) => abstain, NEVER a fake accuracy guarantee. Requires fixed model/run SHA, unique source families, timezone-aware cutoff and prior-observed outcomes. Assumes exchangeability; cannot validate it.
2. `anytime_watch.py`: simple pre-staked Bernoulli e-process for reviewing false-pass rates `E_t = Π[1 + λ(X_t - p_0)]`; under the **unproven conditional null** `E[X_t | history] <= p_0` and predictable admissible `λ`, Ville-style optional-stopping monitoring is possible. This function accepts only frozen, unique, ordered, source-identified input records. Returns an **advisory review signal** and no authorization.
3. `holistic_axes.py`: report the presence, units, samples and evidence digests for 10 distinct categories (accuracy, calibration/Brier, robustness, fairness gap, bias, toxicity, latency, false-pass, privacy-incident rate, mean cost). MISSING is explicitly visible. Even 10/10 source-reported metrics gives `REVIEW_UNVERIFIED_METRICS`, not PASS.
4. `behavioral_consensus.py`: hash and group **pre-observed** sandbox behavior vectors on a frozen test-suite identity. Returns dominant fraction, cluster provenance and `ABSTAIN_HOLD` if weak consensus. There is NO code execution, model sampling, interpretation of the code's semantic correctness or independent probability claim.
5. `shift_watch.py`: bounded categorical histogram total variation `0.5 Σ|p_i-q_i|`, conservative drift alert or `NO_DRIFT_SIGNAL_NOT_PROOF`. The threshold is a declared operator heuristic, NOT a statistically calibrated significance level.
6. `research_assurance.py`: combined **demote-only** safety review. Missing or adverse inputs produce HOLD. With all inputs favorable the strongest result is `INDEPENDENT_REVIEW_REQUIRED`, never automatic execution or certification.

## Architecture alignment: best-fit, never forced

`Evidence → Qualification → Reality → Authority → Effect`

- **Evidence & Analytics:** Stanford's metric inventory and Berkeley's calibrated prediction sets help expose epistemic uncertainty; only use authenticated records scoped to actual datasets/SHA.
- **Qualification & CUSTOS:** CMU e-process alerts on sustained false-pass observations. No self-verified or duplicated source family may qualify an outcome; existing `aurex/experiments/admission.py` remains the signed operator-trust boundary.
- **Remediation / EXECUTE:** MIT behavior grouping can cluster separately sandbox-tested candidate patches *before* a challenger evaluates their quality. No untrusted code is run by this module; a unanimous cluster can still be uniformly incorrect.
- **REALITY / CONTEXT:** Tokyo-style distribution shift diagnostics demote stale calibration and calibration coverage assumptions, not manufacture safety.
- **Models:** Oxford/Cambridge uncertainty research is a future benchmark, not an assertion that AUREX has trained a new model.
- **Nexus & Intelligent Map:** NUS trustworthy/multi-agent framing helps structure reviews; there is no new independent agent, runtime telemetry, or provenance graph introduced.

**Crucial dependency:** PR #53 (Helsinki-inspired governance math) is still a separate unmerged draft. This PR is built directly from `main`, not stacked on #53. Future integration can call `aurex.evals.research_assurance` from the existing research-spine *after* both proposals are individually admitted/serialized. Do NOT auto-merge two PRs or create competing repositories.

## Operational guardrails

- No OpenAI/Ollama/model execution or paid calls.
- No dataset downloads, prompts, private documents or training samples.
- No production config changes, no FastAPI privileged/public route, no worker lease changes.
- No Lovable source changes or credits spent. **Ouroboros P0 latency fix is still first** when Lovable credits renew.
- All dataset/source/provenance digest strings may be caller assertions: checking the SHA format alone does not authenticate historical records. Existing signature and independent witness systems must qualify them before use.
- Conformal marginal coverage needs calibration/evaluation exchangeability and correct split; **none proven here**. An observed drift alert should lead to HOLD and reassessment.
- Anytime validity requires its explicit conditional error-rate null and fixed predictable stake; the program cannot prove that conditional model from the observations.
- Behavioral agreement is neither correctness nor evidence independence.
- Fictitious/synthetic unit tests are engineering validation, not proof of generalization or trustworthy real-world LLM training.

## Next gates

1. Verify exact PR head: `ruff check .`, `mypy aurex`, `pytest -q`, independent runner smoke checks.
2. Independent mathematical/statistical audit of tail-quantile, optional stopping assumptions, duplicate-source protection, label timing, finite sample behavior and drift false positives.
3. Define a versioned **qualified evidence adapter** for signed model/run/data/test-suite digests, observation times, and leakage/audit guarantees. Must follow existing AUREX admission and independent witness workflow.
4. For AUREX/OX owner UI only: add real backend report schemas, authenticated owner-only data delivery, conservative refresh; no fake loss curves or evidence claims. **Fix the Ouroboros lag first**.
5. Cross-model adversarial verification, exact-SHA reproducibility, approval, serialized merge and production deployment are SEPARATE. Current release/deployment: **HOLD**.

## IP / attribution

The methods are described in public university research. This implementation is written anew without reproducing course exercises, paper algorithms verbatim, code repositories, figures, model weights, or datasets. Academic article/code licensing varies; using mathematical principles is distinct from copying material. No university endorsement or affiliation is implied.
