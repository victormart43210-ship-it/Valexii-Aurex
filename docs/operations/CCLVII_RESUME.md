# CCLVII — START HERE

Repository: https://github.com/victormart43210-ship-it/Valexii-Aurex
Work branch: `work/kusanagi-cclvii-sovereign-execution`
Draft PR: https://github.com/victormart43210-ship-it/Valexii-Aurex/pull/183
Base integration #181: `c4f45925e086bbb23b643e66707b224419d52b60`
Main: `34cda4bd8f207f5b1284093b87e4760d782a4903`
Cursor #182: `8323f6db245186b98f2bf2c99a9297e88849e15e`
Last verified code and preceding remote checkpoint: `a8ee5cb7abb1454058f693dc8165ae6dbad58117`.
A following documentation-only commit records these results. Always read actual remote HEAD; a commit cannot embed its own SHA.

## Exact next action
Fetch PR #183's remote head. Copilot should incorporate repair commits `0638ace8`, `bdb09ec3` and `a8ee5cb7`, then the separate Cursor #182 repair set. Rerun the frozen golden ledger, security and full-stack suites on the exact reconciled SHA. Cursor must review that new SHA before an owner merge decision. Do not repeat historical repository discovery or independently merge overlapping PRs.

## Completed and verified
The local prompt proxy leak, duplicate unbilled equipment estimate, dropped HTTP hour collections and dropped document financial metadata are fixed. The clean pushed code SHA passed 741 backend tests with one skip, 157 website tests, 25 DISPATER-web tests, Ruff, strict Mypy, TypeScript and both builds. The real frontend HTTP sandbox test ran. A disposable Cursor #182 overlay applied cleanly and passed 54 selected tests. No shared branch was merged.
Golden amounts remain $385 identified, $150 withheld, $0 recovered; synthetic invoice $10 discrepancy/$0 recovered. No frozen expected values changed.

## Reproduce
Create a clean checkout of the Work branch. Read `CCLVII_RECOVERY.json`, `CCLVII_EXECUTION_LEDGER.json`, `CCLVII_BUG_REGISTER.json` and `CCLVII_VERIFICATION_REPORT.json`.

```bash
git fetch origin
git ls-remote origin refs/heads/work/kusanagi-cclvii-sovereign-execution
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
# Use a unique disposable AUREX_DB_PATH for all synthetic tests.
.venv/bin/python -m pytest -q --junitxml=/tmp/cclvii-pytest.xml
.venv/bin/ruff check .
.venv/bin/mypy --strict aurex
```

Install website and DISPATER-web dependencies from their unchanged package locks with `npm ci --ignore-scripts`. Website: `npx vitest run`, `npx tsc --noEmit`, `npm run build`. DISPATER-web: `npm test`, `npm run build`.
Tested environment: Python 3.12.14, pytest 8.4.2, pypdf 6.21.4, openpyxl 3.1.5; exact Node version and other tools are in the verification report. Host SOCKS proxies may require environment-only `socksio` for existing HTTPX tests. No project dependency was added by Work.

## Recovery and limits
Shell GitHub push credentials were absent. Connected GitHub Git-data writes used expected-SHA leases; remote `git ls-remote` readback verified checkpoints. A local-only commit is not durable. The final response supplies the final documentation checkpoint SHA.
Source review was a separate agent, not external human or organizational assurance. Browser execution was unavailable because Chromium is absent. Live Qwen/model identity, external witness, host firewall and production storage remain unverified. Findings columns and lifecycle limitations remain documented. Conflicting job/customer references and repeated parser fields still require bounded repairs.

Production HOLD; production/mainline merge authority NONE; financial authority NONE. No customer data, paid inference, training, model downloads, third-party contact, destructive deletion or deployment is authorized or performed.
