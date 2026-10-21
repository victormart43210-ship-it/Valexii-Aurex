# KUSANAGI CX — Financial Evidence Intake v1 (SOURCE-ONLY, RELEASE HOLD)

**Contract:** 2026-10-20. **Canonical base:** main `df0654390049118a142ec3b3356f0f40b4789fe4`.

**Owner-approved aim:** `AUREX FIELD AUDIT — Protect Every Dollar. Verify Every Record. Stay Audit-Ready.` Support both service-company missed revenue and operator overcharges; continuous audit preparation; one AUREX backend; Qwen assistance with zero financial authority.

This PR **implements only the first offline document-receipt and formula-observation layer**. It does not read the owner's USB without their involvement, complete the reported ~27k-file inventory, OCR PDFs, establish source authenticity, recalculate formulas, process real customer data for training, train or download Qwen, reconcile invoices against a live company, deploy, certify audit compliance, or merge draft PRs #99/#100.

## Why this is intentionally narrow

AUREX must first distinguish:
1. **Evidence:** original file SHA-256 + private relative source path + size/timestamps, with bounded parser results;
2. **Qualification:** workbook formula text, its *untrusted* saved/cache result, and red flags (external links, hidden sheets, shared-formula followers);
3. **Reality:** independently recalculated values against source agreement, rate-version and authorization — **NOT IMPLEMENTED HERE**;
4. **Authority:** human identity, legally appropriate retention, reviewer approval — **HOLD**;
5. **Effect:** no payments, no sharing or training rights from mere possession of files.

This follows research source contracts from CIX (draft PR #100), including W3C PROV entities/activity/agent relationships, OpenLineage job/dataset receipts, ISO 15489 records management concepts, ATO/CRA reconstructability, IRS support, OOXML formula-cache limitations, OWASP file-upload defense and MLflow/HLE held-out model evaluations. See `docs/KUSANAGI_CIX_WORLDWIDE_FINANCIAL_INTELLIGENCE_LOCK.md` on PR #100. CIX is NOT merged into this branch.

## Implemented

- `workstation/financial_evidence_batch.py`: Python-stdlib local CLI with **default read-only preflight** and an explicit `--execute` gate.
- SQLite receipt ledger, owner-only mode `0600`; path-scoped tenant/project IDs; SHA-256 of bounded local files; no mutation of source files; local-only.
- Resume batching skips unchanged documents using size + mtime + ctime metadata. For security-sensitive full integrity revalidation, create a new database and hash all sources; filesystem timestamps are not a cryptographic guarantee.
- Metadata indexing for PDF, CSV, XLS, XLSM (never parsed/executed). In `.xlsx`, observes OOXML formula source and separately stored cached values without evaluating them, with flags for external link references, hidden sheets and shared-formula followers.
- ZIP traversal, encrypted entry, symlink archive member, size/expansion and member-count checks; no remote relationships followed. `.xls` and `.xlsm` explicitly remain extraction HOLD.
- Failed or unsupported sources recorded as negative receipts; unchanged failures are skipped in later batches but remain **unresolved**, requiring a separate corrected/retry lane. Changing the file triggers reprocessing.
- Read-only aggregate report with content-blind SHA-256 receipt; unresolved count, document count, formula witness count, **NOT_VERIFIED**, **HOLD**, and default `training_authorization=NONE`.
- Regression tests use fictional generated XLSX/PDF bytes only. No personal or company financial documents committed.

**Security note:** For customer material, local operator consent and a dedicated protected tenant store are required before use. This tool is a developer/owner ingestion pilot, not a hardened multitenant web upload endpoint or a malware sandbox. Do not feed untrusted externally supplied office files until the parser is security reviewed. Keep backups encrypted.

## Chromebook / Linux commands (run ONLY after checking USB mount and a safe backup)

From the exact branch checkout of `Valexii-Aurex`, first try with a tiny synthetic directory rather than the full USB:

```bash
python3 -m workstation.financial_evidence_batch intake \
  --root "$HOME/aurex-synthetic-inputs" \
  --db "$HOME/AUREX_FINANCIAL_ENGINE/evidence_v1.sqlite3" \
  --tenant local_owner --project synthetic_lab --limit 25
# Only after verifying path, consent, disk space and that the input is local:
python3 -m workstation.financial_evidence_batch intake \
  --root "$HOME/aurex-synthetic-inputs" \
  --db "$HOME/AUREX_FINANCIAL_ENGINE/evidence_v1.sqlite3" \
  --tenant local_owner --project synthetic_lab --limit 25 --execute
python3 -m workstation.financial_evidence_batch report \
  --db "$HOME/AUREX_FINANCIAL_ENGINE/evidence_v1.sqlite3" \
  --tenant local_owner --project synthetic_lab
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_financial_evidence_batch.py
```

**Do not point it at `THE BIG ONE` until disk use, backups and the existing `financial_evidence.sqlite3` have been reconciled.** This new `evidence_v1.sqlite3` uses a different schema and intentionally **does not replace, migrate or overwrite** the earlier `~/AUREX_FINANCIAL_ENGINE/financial_evidence.sqlite3`. The script is not a magical `--limit` resume flag for the old processing system; they must be reconciled before using production historical data.

When a file is too large (>32 MiB), XLSX has more than 5,000 archive members, >160 MiB expanded data, >50,000 formulas, malformed XML or legacy macros, it is **not** fully analyzed. This requires a separately permissioned, bounded worker and reviewers, not silently lifting limits.

## Next dependency DAG

1. Reconcile old USB inventory against new read-only receipts; independently back up existing DB; get count/failed/unsupported, stale/duplicate/missing without inventing a complete inventory count.
2. Source parser hardening, PDF/text/tables under bounded resources; add no-training default and tenant RBAC for customer flows.
3. Exact formula evaluator with allowlisted Excel function subset, reference graph, named ranges, workbook locale, decimal units, circular and external-link HOLD. Compare separately against approved dated contracts and field evidence; never trust a cached value.
4. Attach original receipt IDs to unified payables/receivables exceptions from draft #99 (selectively reviewed code only); support rate effective dates, credits, legitimate extras, counterevidence, and human approvals.
5. Create audit-readiness package `manifest + document references + missing-items report + finding receipts + signed reviewer disposition`; verify export and selective disclosure.
6. Generate *permission-cleared* training examples; sealed evaluator split by customer, vendor, project, timeframe; Qwen LoRA snapshots and incremental gates; GPU only with explicit budget authorization.
7. Run exact-head independently verified CI, security tests, industry expert review and a closed beta before any customer data.

**Status:** New source + unit tests **awaiting exact-HEAD CI** (GitHub Actions previously reported account billing lock; do not pretend test jobs passed). Existing PR #99 is a separate draft; PR #100 is policy/research only. Neither is merged. No cloud/API spend or Lovable credits. CUSTOS = **HOLD**.
