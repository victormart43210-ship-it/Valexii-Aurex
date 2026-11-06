# START HERE — RESUME WITHOUT REPEATING COMPLETED WORK

Operation: KUSANAGI CCXXXVI. Repository: https://github.com/victormart43210-ship-it/Valexii-Aurex
Active branch: `work/ccxxxvi-continuity-verification`. Base SHA: `34cda4bd8f207f5b1284093b87e4760d782a4903`.
Latest durable checkpoint: UNKNOWN — initial commit not yet pushed. Always fetch and verify actual remote HEAD; recorded SHA is preceding checkpoint, never self-referential.
Pull request: NONE.

## Resume now
1. `git fetch origin`
2. `git switch work/ccxxxvi-continuity-verification` (or clone canonical repository then select branch).
3. Read CHECKPOINT.json, TASK_LEDGER.json and VERIFICATION.json in this directory.
4. `git rev-parse HEAD` and `git ls-remote origin refs/heads/work/ccxxxvi-continuity-verification`; compare actual remote.
5. Recheck #171/#172/newer Cursor or Jules work before edits. Do not re-investigate #159–#164 unless materially changed.

Last completed: C36-001 baseline inspection. In progress: C36-002 initial remote savepoint.
Exact next action: push this continuity commit, verify remote HEAD, then review pinned #171 and #172 in separate clean worktrees.

## Environment and checks
Python 3.12; `python3 -m venv .venv`; `.venv/bin/pip install -e '.[dev]'`.
Use unique disposable databases: `AUREX_DB_PATH=/tmp/ccxxxvi-unique.sqlite .venv/bin/pytest tests -q`.
Run `.venv/bin/ruff check aurex aurex_foundation tests`; `.venv/bin/mypy --strict aurex aurex_foundation`.
Frontend: inspect lockfile/runtime, install frozen dependencies; run recorded project test command and production build. Not run yet for current SHA.
No paid inference, customer records, production mutation or external effects.

## Known state and conflicts
Main is 34cda4bd8f207f5b1284093b87e4760d782a4903. #171 includes #170, both open. #168 is overlapping evidence enforcement, #169 contract-only. New #172 Jules pipeline exists, not reviewed yet. No observed CCXXXV branch at baseline; query again.
Prior local CCXXV branch `work/kusanagi-ccxxv-sovereign-convergence` @89ec43cc has uncommitted slices and is superseded by newer main/Cursor work; preserve as archive, do not integrate blindly. Its baseline test result (609 pass, 2 fail due missing socksio, 2 skip) is NOT current candidate verification.
Files modified by Work: only this continuity directory initially. Runtime/receipt/financial/UI files owned by Cursor/Jules are excluded.
Blockers: Cursor CCXXXV branch not yet observed; recheck before touching product files; PR #171 and Jules #172 overlap; neither integrated; Prior CCXXV work remains in separate local worktree pending archival checkpoint; Independent verification REVIEW_PENDING; no commercial or staging validation.
Production: HOLD. Financial authority: NONE. External paid inference OFF. Automatic merge prohibited.
