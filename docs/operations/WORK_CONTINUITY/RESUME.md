# START HERE — RESUME WITHOUT REPEATING COMPLETED WORK

Operation: KUSANAGI CCXXXVI. Status PARTIAL; production HOLD; financial authority NONE; paid inference OFF; customer data prohibited.
Repository: https://github.com/victormart43210-ship-it/Valexii-Aurex
Active branch: `work/ccxxxvi-continuity-verification`
Base: `34cda4bd8f207f5b1284093b87e4760d782a4903`
Preceding verified remote checkpoint: `3ad06d8594da1e0835100cec84db9006c5bd6495`
Draft PR: https://github.com/victormart43210-ship-it/Valexii-Aurex/pull/173
Always verify actual remote HEAD. The committed checkpoint records a preceding SHA to avoid self-reference.

## Exact next action
Validate the final remote checkpoint with resume checker from a clean checkout, then coordinate Cursor fixes on #174: preserve equipment/labor/unit/payment-kind through both API paths, reject ambiguous field/header imports, authenticate monitoring event payloads and enforce document limits. Rerun saved #174 probes and golden audit. Do not edit Cursor/Jules-owned runtime files from this verification branch.
Last completed: C36-008 latest Cursor CCXXXV review. In progress: C36-007 final remote verification.

## Resume commands
```bash
git clone https://github.com/victormart43210-ship-it/Valexii-Aurex.git
cd Valexii-Aurex
git fetch origin
git switch work/ccxxxvi-continuity-verification
git ls-remote origin refs/heads/work/ccxxxvi-continuity-verification
python3 scripts/verification/ccxxxvi_resume_check.py --check-remote
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```
If the host configures SOCKS proxies, install environment-only `socksio` or the relevant HTTP client extra. No project dependency was added.
Read CHECKPOINT.json, TASK_LEDGER.json, VERIFICATION.json and both source review reports. Do not repeat completed reconnaissance. Check newer Cursor/Jules commits before runtime work.

## Pinned candidate reproduction
Create separate detached worktrees (do not rebase or merge):
```bash
git worktree add --detach ../review-171 db4670ab78fa36c8a2b4b8b66df842350440e437
git worktree add --detach ../review-172 46befcb04d2a98633876b4239775bedbf0b265ca
.venv/bin/python scripts/verification/ccxxxvi_golden_files.py --candidate-root ../review-171 --expected-sha db4670ab78fa36c8a2b4b8b66df842350440e437
.venv/bin/python -m pytest tests/test_work_continuity_ccxxxvi.py -q
```
Run each defect probe from its candidate cwd: `PYTHONPATH=. <venv>/python <work>/scripts/verification/ccxxxvi_cursor_171_probe.py` or `ccxxxvi_jules_172_probe.py`. Exit 1 is expected while defects remain; Jules probe 14/14 means defective reference observations reproduced, not safety gates passed.
Candidate regression: `PYTHONPATH=. AUREX_DB_PATH=<unique disposable path> <venv>/python -m pytest tests -q`; `<venv>/ruff check aurex aurex_foundation tests`; `<venv>/mypy --strict aurex aurex_foundation`.
Website: `npm ci --ignore-scripts`, `npx vitest run`, `npm run build`. Separate dispater-web: `npm ci --ignore-scripts`, `npm test`, `npm run build`.

## Verified results and limits
- #171 @db4670ab: 637 pytest PASS/1 skip; Ruff/Mypy PASS; website 156 tests/build PASS; separate dispater-web 25 tests/build PASS. Probe 2 PASS/7 FAIL.
- #172 @46befcb: 622 pytest PASS/1 skip; Ruff/Mypy PASS; website 156 tests/build PASS. Probe reproduced 14 defective observations.
- Work mainline runtime: 616 pytest PASS/1 skip before adding 7 continuity tests; 12 continuity tests also PASS. Own implementation is not independently verified.
- New 36-file structured JSON corpus: 107 provenance rows; independent arithmetic 275.50 identified, 130.00 withheld, 0.00 recovered; month37 400.75/130.00/0.00. API/dashboard/tenant denial/v2 receipt/replay/separate-process DB reopen PASS. Monitoring remains in-memory.
- Browser E2E, PDF/OCR/XLSX, equipment/personnel hours, live mounted-volume durability and commercial correctness NOT VERIFIED.

## Ownership and blockers
Work owns continuity records, three probes/harnesses plus resume validator, new fixtures and recovery tests only. Cursor #171 includes #170; #168 overlaps receipt work; #169 is contract-only. Jules #172 overlaps API and pipeline/monitoring. No product code or their handoffs changed by Work.
Blockers: seven Cursor semantic failures; Jules false independent qualification, malformed-file handling, receipt binding and request-to-request document persistence; overlapping owners; human/real-world review pending.

## Preserved earlier work
`archive/ccxxv-superseded-work-20261106` @ `b0c1725b1895ca170c156d272b1866da5c2af63d` preserves the older session, superseded and DO NOT MERGE. Archive developer tests: 712 pass/1 skip, frontend NOT_RUN. It is not a competing candidate.
Shell push lacks credentials; connected GitHub Git-data writes succeeded, with git ls-remote readback. A local commit alone is LOCAL_ONLY. No merge/deploy authorized or performed.

Separate source review corrected golden-harness dirty-checkout/optimized-Python guards, exact provenance cardinality and replay after an already-applied month37. Resume remote checking now fetches the named ref, validates origin, local HEAD/branch, preceding-SHA ancestry and clean working tree. Initial schema-only remote check was superseded; do not use it as readiness evidence.

## Newly observed Cursor CCXXXV
PR #174: https://github.com/victormart43210-ship-it/Valexii-Aurex/pull/174, branch cursor/kusanagi-ccxxxv-industrial-beta-4082, head 2d0b62400e0ad40f2780f51b26ba0d09261cd724. This appeared during Work verification. #171/#172 reports are historical pinned evidence and do not qualify #174.

## Latest candidate findings (supersedes earlier candidate status)
Cursor #174 @2d0b62400e0ad40f2780f51b26ba0d09261cd724: 651 backend tests PASS, zero skipped; Ruff/strict Mypy PASS(92files);157 website tests/build PASS. Golden structured-file corpus PASS. Separate finance/API probe:5PASS/13FAIL; document probe13/13 defective reference observations reproduced. Digital PDF/XLSX exist, but no general OCR/image parsing. Same8h×25job:200.00direct,0.00reconciliation API,25.00documents API. Payment reversal kind is dropped by ingestion; duplicate PDF/XLSX fields overwrite; monitoring event payload is not independently sealed. See both174reports and executable probes.
Website scan:14advisories(2high/12moderate), no automatic upgrade. Python license/version inventory saved; Python vulnerability scan NOT_RUN.

Owner advanced to CCLVII. Active follow-on branch work/kusanagi-cclvii-sovereign-execution is based on current Copilot integration, not this old mainline verification branch. Preserve these pinned historical findings; do not reapply obsolete fixes blindly.
