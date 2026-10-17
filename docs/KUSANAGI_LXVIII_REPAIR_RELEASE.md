# KUSANAGI LXVIII — Current-main repair and release safety

**Status:** candidate PR from verified main `df0654390049118a142ec3b3356f0f40b4789fe4`.
**Policy:** [AGENT_MAINLINE_POLICY](AGENT_MAINLINE_POLICY.md); **production deployment HOLD**.
This is not a merge or a Railway change.

## What was broken, what is actually repaired

- Draft #51 Bayesian evidence fusion had Ruff UP017: `timezone.utc` instead of Python 3.12 `UTC`. It was based on the old main `c41675fc...`. Rather than blind-merge a stale branch, the original three changed files were reviewed and the implementation applied to a fresh-main repair branch.
- Additional boundedness issues fixed: extremely small likelihoods could make `p_h/p_not_h` overflow to `inf` before logarithm; use difference of logs. Explicitly reject naive/invalid current clock; reject huge Python integers that would overflow float conversion; bound record and cluster identifiers and CLI input size.
- IMPORTANT: the offline Bayesian input field strings `qualification: PASS`, `independent: true`, and `calibration: INDEPENDENTLY_VALIDATED` are **self-declared**, not signed or verified provenance. The result is always `ANALYSIS_ONLY_NOT_AUTHORITY`; no run on live admitted evidence was established. Never allow these flags to bypass CUSTOS or grant effect authority.
- Docker canonical image workflow now triggers for **every pull request**, so it can be a required status check even on docs-only PRs, and on **push to main** for application/deployment changes. It tests a nonroot container, `/v1/health`, SQLite persistence on a mounted **CI-only** volume, the unauthenticated jobs endpoint's 401, and importing new governance modules **inside the built image**. A CI container volume does not verify Railway's pending production volume.

## What still cannot be claimed fixed by this source PR

1. **GitHub branch protection is not active**: queried branch metadata reported `protected: false`; accessible ruleset list returned empty. The GitHub connector does not offer create/update branch protection or rulesets. A repository owner/admin must configure Settings → Rules → Rulesets, target `main`, require PR reviews and required status checks (`CI / test`; `Canonical Railway image / docker-build-and-smoke` **after** it reports successfully); block force pushes and deletions, restrict bypass, and ensure administrator enforcement. Exact check names should be selected from GitHub's actual Check runs; no guessed check IDs. The repair branch removes Docker path filtering from pull-request events so the required Docker check should always be emitted; verify its actual registered check name and completed run before selecting it. Do not claim GitHub settings changed.
2. **Production Railway remains on the older read-only bridge**: service `aurex-api`, source `integration/kusanagi-xvi-railway` root `/integrations/kusanagi-xvi/backend` at `57a079f93b947594f1a6f854aa46a6f606f86f76`. Canonical `main` now contains the root `Dockerfile` and FastAPI `aurex.api:app`, but **no release has been deployed** from those commits.
3. **Staged Railway changes must not be conflated with live**: 4 pending updates include `aurex-evidence-db` volume at `/data`, `AUREX_DB_PATH`, `AUREX_ENABLE_OFFLINE_LAB` and service mount changes. Staging is not attachment, persistence, backup, or restoration proof.
4. **GitHub Actions CI green does not independently validate** Bayesian posteriors, conformal exchangeability, conditional false-pass assumptions, live worker execution, authentic training, frontend-owner authorization, Railway storage durability, or CUSTOS admission.

## Mandatory release sequence (no automatic step)

1. Get this repair PR's exact head and run `ruff check .`, `mypy aurex`, `pytest -q`. Inspect Docker build-and-smoke job results on **the same commit** and CI logs. Run independent adversarial review.
2. Decide whether to close obsolete draft #51 after the replacement is accepted. Do not merge two competing implementations of `aurex/bayesian_evidence.py`.
3. Configure GitHub branch protection from an authorized administrator; **verify it is enforced**, not just documented.
4. Resolve target Railway branch/root, volume state, `AUREX_DB_PATH=/data/aurex_jobs.db`, `AUREX_ENABLE_OFFLINE_LAB=0` by default, healthcheck `/v1/health`, server-side bearer tokens and rollback. Check actual staged variables without printing secrets; preview env/plan, and separate staging from production before authorization.
5. Deploy to isolated Railway staging only after explicit permission and measured CI-container safety; test 401/503, jobs/evidence/budgets, database restart and backup restore, network protections, costs, and owner-only website proxy.
6. Ask for **separate explicit production approval**; deploy only approved exact release SHA, measure real website+backend results, retain rollback. P0 Lovable Ouroboros performance remains separate and not silently modified.

## Evidence states

| Item | State |
| --- | --- |
| Source repair | PR pending independent review |
| GitHub CI | NOT RUN until exact head completes |
| Docker image on PR | NOT RUN until exact head completes |
| Branch protection | FAIL / not enforced |
| Railway canonical deployment | NOT DEPLOYED |
| Signed Bayesian calibration | NOT VERIFIED |
| Lovable backend E2E | NOT VERIFIED |

No model weights downloaded, no paid services used, no GitHub merges, no Railway patch accepted, no Lovable credits spent.
