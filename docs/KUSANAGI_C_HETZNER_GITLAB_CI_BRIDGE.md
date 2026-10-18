# KUSANAGI C — EXISTING HETZNER/GITLAB RUNNER → CANONICAL GITHUB AUREX CI

**Created 2026-10-18. SOURCE STAGED / EXTERNAL ACTIVATION NOT VERIFIED / NO MERGE / RELEASE HOLD.**

## Scope and truth

The user asked to reuse their **previously discussed Hetzner CX33 / GitLab Runner** infrastructure after GitHub Actions jobs began failing with **zero executed steps** due to GitHub billing restrictions. Previous Hetzner records discussed an Ubuntu 24.04 CX33 (4 vCPU / 8 GiB RAM / 80 GiB disk), server label `medaurus-runner-01`, and a **MEDAURUS/CoreGuard-Android GitLab** build role, but did **not prove** the runner was ever registered, currently online, tagged, or attached to any known GitLab project. **Do not claim the runner has been remotely configured or that GitLab is receiving AUREX jobs** without an actual GitLab pipeline URL.

This change creates only the **GitLab manual CI bridge** and **read-only Hetzner preflight** files inside the existing **single canonical GitHub AUREX repo**. It **does not** migrate AUREX source-of-truth to GitLab, change the MEDAURUS project, register a runner, install packages on Hetzner, perform paid API inference, unlock GitHub Actions, merge any of the 51 PRs, touch private USB files, deploy Railway/Lovable/Cloudflare or authorize a financial decision.

Relevant upstream: https://docs.gitlab.com/runner/security/ ; https://docs.gitlab.com/runner/executors/docker/ ; https://docs.gitlab.com/ci/runners/configure_runners/

## G0: Inspect existing Hetzner safely (no secrets)

After logging into the existing server through its owner-authorized SSH session, use a **trusted review of this exact source**:

```sh
# With a checkout of this draft branch in a temporary workspace:
bash ci/hetzner/read_only_preflight.sh

# If service config is root-only, optionally run ONLY this local read-only command:
sudo bash ci/hetzner/read_only_preflight.sh
```

It reports only binary/service presence, masked runner count/executor, Docker privileged/socket flags and Docker availability. It **does not** print runner tokens, project URL, other config.toml secrets or the server's address. Look at GitLab **Settings → CI/CD → Runners** yourself to confirm the runner is ONLINE and determine its tags. If not online, fix its existing service/registration before attempting a pipeline. **No evidence currently confirms the server is active.**

A runner already configured for Android shell execution or `privileged=true` should **not** be used to execute unreviewed Python pull-request code. GitLab warns that shell executors and privileged Docker runners can expose the host. On the **same** existing Hetzner machine, use a dedicated non-privileged Docker executor for AUREX, or a separate hardened environment if the host is not isolated. Do not bind the host Docker socket or USB drives, production secrets, private databases or persistent company documents into AUREX test containers. Apply resource limits/egress control at the host/runner layer.

## G1: Attach the job to the EXISTING GitLab setup, without GitHub mirroring

Only after validating the runner is appropriate, create a protected **CI-only branch** in an existing authorized GitLab project for this manual job, without replacing the Android project's `main` pipeline. Use the following minimal **GitLab `.gitlab-ci.yml`** on that branch (replace the pinned SHA if and only if independently reviewing a newer bridge implementation):

```yaml
stages:
  - test

include:
  - remote: 'https://raw.githubusercontent.com/victormart43210-ship-it/Valexii-Aurex/8b07881b8c6b77aa2391aafd1b9e472bc95f799d/ci/hetzner/gitlab-verify-pr.yml'
```

**Why pinned:** the remote YAML is retrieved from a known immutable GitHub commit where the bridge source was introduced, not a mutable `main`/feature branch. GitLab must be allowed to access `raw.githubusercontent.com` (AUREX repository is currently public). The CI-only branch is a trigger/configuration surface, not a fork or full mirror of AUREX source. Keep it protected/controlled; do not accidentally run Android build jobs or edit existing MEDAURUS Android CI.

Set runner tag **`aurex-hetzner`** (or a reviewed override with `AUREX_RUNNER_TAG` if your existing runner has a different safe tag). The job uses `python:3.12-bookworm` and **GIT_STRATEGY=none**. In GitLab, create a **web pipeline** on the CI-only branch with **both** variables:
- `AUREX_PR_NUMBER` = a specific GitHub open PR number that **targets `main`** (e.g. `90`).
- `AUREX_EXPECTED_SHA` = that PR's **current exact 40-character head SHA** from GitHub (e.g. for PR #90 as inspected: `b3d52c649cc5c4dbc40d7cc8a7cb5b1e4a9b80fa`; re-check before running).

Then **manually run** the `aurex_github_pr_verify` job. The job rejects mutated refs, external PR forks, stacked PRs whose base is not `main`, missing variables, and anything not running inside a container. It fetches exactly the GitHub pull request into a temporary job workspace, never modifies `main`, and runs on Python 3.12:
```
pip install -e .[dev]
python -m compileall -q aurex training workstation
ruff check .
mypy aurex
pytest -q
```
It generates an exact-SHA receipt, dependency versions, syntax/Ruff/Mypy/pytest logs as **seven-day GitLab artifacts**. It sanitizes the child process environment to avoid passing GitLab secrets to untrusted PR setup/tests. **The GitLab job itself still has normal GitLab job-token privileges, and an untrusted container may be able to obtain those via other channels; do not run external fork PRs, include secrets, or expose protected infrastructure.** First test must be a reviewed owner branch on a safe isolated runner.

**No automatic GitHub status checks:** GitLab artifact receipt is evidence, but GitHub's branch required-check policies may still block direct PR merges if they require GitHub Actions checks. Do **not** override branch policies or falsely mark a GitLab test as a GitHub-hosted pass.

## G2: Verify one small PR before the 51-PR program

1. Verify Hetzner host and runner **ONLINE**, dedicated Docker executor `privileged=false`/no docker socket, and protected manual CI pipeline ownership.
2. Run one owner-controlled **main-targeting** PR at a fixed SHA; confirm exact-SHA GitLab artifacts exist and jobs executed actual test steps. If the GitHub repo's current baseline contains unrelated failures, log the failure and fix them **on a separate main-derived branch**, do not fake green.
3. Record GitLab pipeline URL, runner identity, exact tested GitHub SHA, command outcomes, advisory security check and independent reviewer in master GitHub issue #75. Do not post credentials/secret-bearing logs.
4. For each other PR: preserve base/main SHA, source diff, dependency DAG, conflict status, reviewed code paths, tests, independent witness. Merge **one at a time**, only after true admission. Re-fetch main and rebase/retest after every merge. Avoid bulk merging stale branches, overlapping Folio/financial implementations, or PRs stacked on a different base.
5. Do not link source-only staging to website/Railway/Lovable until exact deployment contracts are independently measured. No production deploy, CI required-check bypass, auto-merge, or private audit data processing.

## Decision register

| Gate | Status |
| --- | --- |
| GitHub original code preserved | PASS (new branch only) |
| CI bridge and preflight authored in repo | SOURCE STAGED |
| Hetzner server exists / accessible / healthy | NOT VERIFIED |
| GitLab runner registered / Docker safe / online | NOT VERIFIED |
| GitLab protected CI-only pipeline configured | NOT VERIFIED |
| Actual GitLab AUREX run against pinned PR SHA | NOT RUN |
| GitHub Actions billing/required checks restored | NOT VERIFIED |
| Canonical CI + Mypy + Ruff + pytest + Docker | NOT VERIFIED |
| Mainline merges or production deployments | NONE; HOLD |

**CUSTOS:** Evidence → Qualification → Reality → Authority → Effect. Unknown≠safe; no self witness; no secret logging; no training/customer uploads; unapproved external API spend $0. Bridge setup alone is NOT a production release or 51 safe merges.
