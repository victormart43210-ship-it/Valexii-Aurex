# KUSANAGI LXXII — local verification while GitHub Actions runners are unavailable

The repository's GitHub-hosted jobs have repeatedly failed before runner allocation
(see GitHub issue #58). This script is an interim way to make engineering progress,
**not a bypass of required CI or independent CUSTOS review**.

## Chromebook / laptop (no new hosted infrastructure)

Use a fresh, disposable checkout of the exact branch; this preserves work in the
existing AUREX checkout. Use Python 3.12 if installed, because main CI uses 3.12.
A Python 3.13 run is still useful local evidence, but is not identical to CI.

~~~bash
cd ~/Valexii-Aurex
git fetch origin
git worktree add --detach ~/aurex-local-ci origin/work/kusanagi-lxxii-local-ci-fallback
cd ~/aurex-local-ci

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'

python scripts/offline_preflight.py --expected-sha "$(git rev-parse HEAD)"
~~~

The script checks a **clean exact commit** and executes Python compileall, Ruff,
strict Mypy and the entire Pytest matrix using the currently active interpreter.
It does not install packages itself, contact GitHub/Railway, merge, deploy, publish,
start LLM models, or enable a paid runner.

Optionally, if Docker is installed locally and an image download is acceptable,
add --docker-build; this checks a local image build, not a container runtime
smoke test or Railway volume persistence.

~~~bash
python scripts/offline_preflight.py --expected-sha "$(git rev-parse HEAD)" --docker-build
~~~

The default evidence directory is a private local temporary directory **outside
the source tree**. The manifest records the target commit SHA, Git tree SHA, local
Python version, each check result, log filename, duration and SHA-256 of each log.
Do not publish raw logs without checking them for credentials or other sensitive
data. The tool strips common cloud/API secrets from subprocess environment and
disables AUREX runtime worker flags, but it is **not a network sandbox**:
running any repository's tests executes arbitrary local Python code. Run only
reviewed source in a disposable, restricted environment without live credentials.

## Gate contract

Even when all local checks pass, the manifest must always read:

- local_checks = PASS (local checks only)
- github_actions_verification = NOT VERIFIED
- independent_verification = NOT VERIFIED
- release_authority = NONE
- release_gate = HOLD
- production_deployed = false

A SHA mismatch, dirty worktree, failed checks or missing tools cannot return a
local PASS. Python 3.13 runs will report python312_ci_equivalent = false.
Local Docker build is opt-in and does not exercise the deployed service.

**Do not disable existing GitHub required checks or merge unverified changes.**
Official CI, independent security review, and separately authorized staging /
production release must be completed once runner access is restored.

## Verification while waiting

1. Run the checker on this branch and retain the private local manifest.
2. Continue reviewing/fixing open draft PRs #56, #60 and #61 against canonical main.
   The script belongs to this particular branch. To test another PR without
   modifying its commit, run the four printed commands in that PR's clean worktree
   and record the SHA manually. Do not claim the resulting logs are a manifest
   generated on that PR by this script.
3. When issue #58 is resolved, rerun official CI + canonical Docker smoke on the
   exact reviewed commit SHA. An offline PASS never authorizes ADMIT or merge.

**Security warning:** Do not register a self-hosted Actions runner with secrets
that could be reached by untrusted pull requests on this currently public
repository. No new cloud provider, paid infrastructure or Railway setting is
required for this fallback.
