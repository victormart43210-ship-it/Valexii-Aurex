# KUSANAGI — Local Financial Evidence Source Convergence

**Objective:** Reconcile the locally developed AUREX financial/document-processing engine into the **single canonical** `victormart43210-ship-it/Valexii-Aurex` repository. This PR introduces **source-only intake tooling**; it does not claim to have imported the Chromebook's current code or connected its financial engine to production.

## Evidence from the Create Logo Options workstream

The latest user-thread Step 79 report states a controlled **100-PDF real-file batch**: 15 `TEXT_EXTRACTED`, 85 `NO_TEXT_LAYER`, with 0 reported errors and original USB files unchanged. That is a **previously reported local result**, not independently replayed in this PR. The earlier 15-of-20 pilot is not the latest batch. At Step 80, `pdftoppm` and `pdfinfo` were available; Tesseract and ImageMagick were not installed.

Previously reported Excel inventory: 27,965 total files scanned, 1,928 XLSX discovered, 1,908 readable, 8,238 worksheets, 1,690,160 formula cells, 54,964 shared-formula groups, zero reported scan errors. **Excel recalculation, reconciliation correctness and actual financial verification remain NOT VERIFIED.**

Local AUREX source reported at:
`/home/victormart43210/aurex-kusanagi-lxx/Valexii-Aurex-main`.

Read-only original documents reside on removable USB:
`/mnt/shared/removable/THE BIG ONE`.

Expected code modules in that local repository:
- `aurex/financial/scanner.py`
- `aurex/financial/dashboard.py`
- `aurex/financial/cli.py`
- `aurex/financial/reconciliation.py`
- `aurex/financial/pdf_batch.py`
- optional `aurex/financial/pdf_reconcile.py`, related tests

The financial evidence SQLite database belongs to **local user-managed storage** such as `$HOME/AUREX_FINANCIAL_ENGINE/financial_evidence.sqlite3`. It must never be included in GitHub PRs or this source-only intake report. No financial artifacts, OCR output, invoices, statements, spreadsheets, or raw text should be pushed to GitHub or a public website.

## Run source-only inventory on Chromebook (no financial document reads)

From a terminal:

```bash
cd /home/victormart43210/aurex-kusanagi-lxx/Valexii-Aurex-main

git fetch origin work/kusanagi-financial-source-convergence-intake
git show FETCH_HEAD:scripts/financial_source_preflight.py > /tmp/aurex_financial_source_preflight.py

python3 /tmp/aurex_financial_source_preflight.py \
  --source "$PWD" \
  --usb-root "/mnt/shared/removable/THE BIG ONE" \
  > /tmp/aurex_financial_source_preflight.json

cat /tmp/aurex_financial_source_preflight.json
```

This tool checks *only* selected Python source/tests in the local repository, and it checks whether the mount-root directory exists. It does **not** traverse or open any files on the USB, read the SQLite database, modify local sources, create a remote commit, or upload anything. It reports only relative code paths, size, SHA-256, syntax status, git HEAD, whether the worktree is dirty, mount-presence bool, and an integrity digest of this self-generated report.

The report's `PASS_SOURCE_INVENTORY_ONLY` means required source files were found and parse as Python. **It does not establish financial accuracy, safe handling of real documents, CI success, an authenticated live website connection, or independent attestation.**

If `git fetch` cannot access the PR branch, download the exact script directly from reviewed PR #67 through your authenticated GitHub session instead of installing tools or making changes to the local AUREX working tree.

## Integration process AFTER inspecting the report

1. Freeze local code and capture source hashes; **do not overwrite existing worktrees** or USB originals.
2. Selectively stage only reviewed `aurex/financial/*.py` and synthetic `tests/test_financial*.py` / `tests/test_pdf*.py`; manually inspect contents for secrets, embedded document data, test fixtures, home paths, or sensitive hardcoded values **before** any push.
3. Open one narrowly scoped **financial source PR** against canonical main, independent of existing IRON BRIDGE security PR #66. Avoid unrelated branch merges and do not force push.
4. Run synthetic tests, pylint/mypy/ruff if configured, bounded *read-only* local 100-PDF reproduction only when authorized, SHA-256 before/after original files, and independent CUSTOS review.
5. Do not expose local financial data through Lovable/Railway: any future API is a separate authenticated, owner-restricted, schema-validated and explicitly authorized deployment.
6. Continue read-only production AUREX bridge proof separately in Issue #65: Railway ONLINE ≠ website server-side authenticated handshake.

## Release and privacy gate

| Evidence gate | Status at intake creation |
| --- | --- |
| Local source bytes accessible to this PR | NOT VERIFIED |
| Local synthetic preflight tool created | YES — exact script Git blob dba4852048091178927ded7f7f85a4fb5a857885 |
| Preflight regression tests | 13/13 PASS on independently matched local code/test bytes; Python 3.13, pytest 9.0.2 |\n| Ruff / Mypy / full repository CI | NOT RUN locally; may be unavailable in runner |\n| Step 79 controlled 100-PDF results | USER-THREAD REPORTED |
| USB originals | MUST REMAIN UNCHANGED |
| Financial source code merged into canonical main | NO |
| Financial engine published to Railway or Lovable | NO |
| IRON BRIDGE PR #66 | DRAFT / UNMERGED |
| Deployed frontend-to-backend authenticated handshake | NOT VERIFIED |

**Authority doctrine:** Evidence → Qualification → Reality → Authority → Effect. A source inventory cannot self-certify the underlying data or grant authority. Unknown is never healthy.
