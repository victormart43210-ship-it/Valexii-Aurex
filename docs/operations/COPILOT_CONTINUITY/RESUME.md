# START HERE — RECOVER THE LAST VERIFIED COPILOT STATE

Operation: KUSANAGI CCXXXVIII (Project Sovereign Code Assurance)

- **Repository:** `victormart43210-ship-it/Valexii-Aurex`
- **Active branch:** `work/kusanagi-ccxxxviii-copilot-assurance`
- **Base SHA (main):** `34cda4bd8f207f5b1284093b87e4760d782a4903`
- **Candidate:** `main` + PR #171 (`db4670a`, already contains #170) + PR #172 (`46befcb`), merged cleanly. Only `aurex/dispater_api.py` overlaps.
- **Latest remote checkpoint:** `6bb61754490d7601e89b8d827c2524a13aca3475` (implementation + tests + registry). Later commits only add continuity metadata. Verify with `git ls-remote origin work/kusanagi-ccxxxviii-copilot-assurance`.
- **Active PR:** draft PR into `main` (see `COPILOT_CHATGPT_HANDOFF.json`). It also shows #171/#172 content because no combined integration branch exists.
- **Production:** HOLD. **Financial authority:** NONE. External paid inference OFF.

## Completed
See `TASK_LEDGER.json`. Summary: independent financial oracle, receipt/API/ingest security tests, pipeline/monitoring/36-month manifest tests, registry honesty review, and 6 defect fixes (D1–D6).

## Current task
Hand off to the integration owner. Nothing in progress.

## Next exact action
1. Fetch `origin`; if PR #171/#172/#173 or a combined integration branch changed, rebase/merge this branch onto it and rerun the test commands below.
2. Owners (Cursor/Jules/Work) review defects D1–D6 and the open limitations L1–L6 in the ledger.
3. Do not merge to `main` automatically.

## Test commands
```
python3 -m venv /root/venv && /root/venv/bin/pip install -e '.[dev]'
pytest -q -p no:cacheprovider          # 797 passed, 1 skipped at 6bb6175
ruff check aurex tests
mypy aurex
cd website && npm ci && npx vitest run && npx tsc --noEmit -p . && npx vite build
```
Note: `pip install -e` rewrites the tracked `valexii_aurex.egg-info/`; run `git checkout valexii_aurex.egg-info` before committing.

## Known failures
None in the executed matrix. NOT_RUN: Bun runner, Playwright e2e, Semgrep.

## Dependencies / overlap
- Cursor owns PR #170/#171 files (`dispater_receipt/store/ingest/pilot/intelligence`, `evidence_kernel`). Copilot made **no** edits to them.
- Jules owns PR #172 files. Copilot edited small parts of `dispater_pipeline.py`, `dispater_monitoring.py`, `dispater_api.py` (see ledger). Expect merge conflicts if Jules changes the same lines.
- ChatGPT Work owns PR #173 (continuity/verification). No overlap.
