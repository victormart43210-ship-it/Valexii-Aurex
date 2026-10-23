# KUSANAGI XCIX — TWO-WAY FIX WRANGLER ↔ AUREX/OX CONVERGENCE
**2026-10-18 · OWNER DIRECTIVE · SOURCE-ONLY / PRODUCTION HOLD**

This is the **shared cross-thread engineering contract** for both the *Fix Wrangler Commands* conversation and the *APIS PRIME / unified research / synthetic-company audit* conversation. **Neither thread replaces the other.** Both must use this record to preserve all constraints, source identities, evidence boundaries, and test status.

## 1. What is locked in both directions

### From Fix Wrangler Commands → the APIS PRIME / financial-research lane
- **AUREX is a cross-domain company evidence system, NOT a financial-only document app.** It must recognize invoices, purchase orders, banking, general ledgers, IRS/tax reports, DOT/FMCSA inspection/compliance records, insurance policies/claims, business/ownership documents, field tickets, contractual records, source-code/Python repositories, historical manuscripts, and unknown forms.
- User's adversarial review question is **“How could an examiner, insurer, IRS/DOT reviewer, auditor or opposing party reasonably deny or challenge this claim, and which source evidence answers that challenge?”** Apply this as a grounded challenge method, not an automatic assumption of wrongdoing.
- Existing local **SOVEREIGN AUDIT R1** pilot was reported by the Fix Wrangler thread on 2026-10-18: `AUREX_OX_SOVEREIGN_AUDIT_R1_20261018.zip` and `AUREX_OX_SOVEREIGN_AUDIT_R1_20261018_install.sh`; 14/14 local tests reported, 24/24 local PDF extractions reported. **I have only inspected the available installer metadata, NOT the ZIP bytes or customer PDFs.** The reported categories (banking 6, IRS 5, oilfield 3, corporate 3, insurance 1, DOT 1) sum to **19**, not 24; five cannot be categorized from this record and must remain **UNKNOWN/OTHER** pending private manifest review. The private PDF contents, raw OCR, bank numbers, names and corporate secrets stay **off GitHub and outside the public website**.
- Historical XC offline finance pilot: synthetic `$28,750` invoice vs `$25,000` field ticket = `$3,750` discrepancy; 47/47 tests **reported in isolated local build**, not production proof. Complete ZIP reported SHA-256 `537bbf1fd00b8ef5032f501dd15ad4e3697ecba4ae52b6692a33cb1e81afd427`; core ZIP `18c74963dc11896b78450d4acdb8802921d3326f2be665a433b1eb0c83a1be51`. Neither file is automatically an admitted GitHub release.
- Browser/transport: **Wrangler 4.151.1**, user's local project `~/AUREX_NEXT/valexii_repair`, Cloudflare Worker `tanstack-start-ts` **built / locally dry-run**, with `117 modules / 86 assets` reported, local `GET /`, `/aurex`, `/aurex/ox` **200**; local Worker command `wrangler dev --local --port 8787` worked. **`wrangler list` is not a valid v4 command**, and the generic Worker name was not verified as a deployed route. The LXXXV **256 KiB raw-byte, fatal UTF-8, manual-redirect, min-32-char bearer** hardening must be reconciled with actual current website code. Wrangler dev/dry-run ≠ Cloudflare production deployment.
- Cloud backend: Railway `aurex-api` production has been observed as **older read-only five-GET bridge** based on SHA `57a079f93b947594f1a6f854aa46a6f606f86f76`, while canonical GitHub main is newer. A direct Railway 2xx **does not prove** authenticated Cloudflare Worker → Railway provenance. Four staged DB/worker changes are **not live**. Do not print tokens, copy .env, change routes or apply staged deployments.
- `FIX_WRANGLER_COMMANDS_THREAD_HANDOFF_2026-10-17.md` is a prior Library handoff (dated 2026-10-17). Some site/credit/CI facts in it are superseded by fresher source checks; do not overwrite history. Actual Lovable project `811ffc43-2c8b-4c88-ab4c-4de668d089cb` is published with **source version `b1d00f6bfac7e5abe38fd1de0ca9378f680fc6e7` observed on October 18**, but this does **NOT** prove it published the newest source or the XCIX evidence engine. Test its *current* source before modifying.

### From APIS PRIME / synthetic-company audit → Fix Wrangler Commands
- **APIS PRIME is one governed reasoning spine, one owner-facing evidence view, not 14 independent agents or tabs.** The fourteen display names are canonical in **draft PR #86** with stable AP01–AP14 IDs. Qwen/ELNOESIS is a separately approved, local-only, untrusted model adapter; no model automatically sees private PDFs or trains on them.
- **FOLIO INDEX** (draft PR #88) gives stable source accessions, relationships, visibility flags, source-time/calendar context and SHA-256 receipts. The index is in-memory research code, **not a durable encrypted evidence vault** or a tenant-authenticated public service. A SHA is a receipt for bytes, not authenticity or independent verification.
- **Synthetic Company Evidence Replay** (draft PR #89) created **9 fictional documents, 7 discrepancies/evidence gaps and 7 `AurexEngine` HOLD receipts**, under one NOW→CHANGED→NEXT→WHY→PROOF view, **0 new tabs**. Its local authoring-container controls were reported to pass, but exact-head GitHub CI failed before executing steps and full independent reproducibility is **NOT VERIFIED**. It is NOT the real 24-PDF company batch from Fix Wrangler.
- The **nine fictional source types** in PR #89 include bank, tax summary, DOT and insurance but are not a complete real business audit. Discrepancy amounts overlap and **must not be summed as losses**; a missing DOT source is not DOT noncompliance and an expired presented insurance certificate does not prove uncovered operations.
- Existing financial draft **#80**, Qwen draft **#84**, filter/plan **#85**, one-spine **#86**, source Folio **#88**, synthetic company **#89** remain **unmerged**; plan/spec #77 and Jules issue #87 are additional non-admitted evidence inputs.
- Domain roles must be **documented as actual vs provisional**. 14 display identities are not 14 independently demonstrated decipherers. Avoid fabricated manuscript translations, audit certifications, LLM training scores, working end-to-end status, or 100%-readiness bars.

## 2. The shared canonical workflow (one core, typed adapters)

```
PRIVATE COMPANY USB / DOCUMENTS              PUBLIC MANUSCRIPTS / CODE EXAMPLES
       | scoped human consent                      | license + source permission
       v                                           v
LOCAL-ONLY QUARANTINE / NO-SYMLINK INPUT GATE / FILE SIZE & TYPE CHECK
                  | class stated; unknown != finance
                  v
FOLIO INDEX: tenant / source ID / SHA256 / original / parent derivatives
                  |
PDF text or OCR / banking tables / Python AST / manuscript transcription
  (separate adapters; explicit extraction uncertainty + no auto trust)
                  |
AUREX CANONICAL EVIDENCE ENVELOPE + VERSIONED SOURCE RELATIONSHIPS
                  |
APIS PRIME (one spine, dynamically applicable research methods)
                  |
    "WHAT WOULD AN ADVERSARIAL EXAMINER CHALLENGE?"
                  |
XOLOTL independent evidence / CRUCIBLE controlled negative controls
                  |
CUSTOS: evidence > qualification > reality > authority > effect
                  |
NOW → CHANGED → NEXT → WHY → PROOF [one owner-only view, expandable receipts]
                  |
HUMAN REVIEW / AUTHORIZED EFFECT ONLY; NO LLM TRAINING BY DEFAULT
```

**One shared engine; NOT one shared public document database.** Separately authenticated, tenant-isolated PRIVATE vault vs only consented/licensed PUBLIC demonstration sources, with no indexing, embedding, upload, training or model exposure crossing their boundaries. No live customer files through Qwen/Cloudflare/Railway until approved contracts, RBAC, encryption and retention policy are independently validated.

### Domain triage contract

The source-only `aurex/company_evidence_taxonomy.py` module provides a bounded **customer-declared category → candidate review route → adversarial questions**, including distinct finance, tax, DOT, insurance, corporate, software and research pathways, with unknown → triage. It **does not read content, OCR a document or independently verify the declared type**. `authorized_for_local_review=False` returns HOLD and no review questions. Model-training permission cannot be conferred by intake metadata; it needs a separate reviewed opt-in authorization.

## 3. No race condition between the two development lanes

| Evidence / workstream | Tracked source | Trust state / next action |
| --- | --- | --- |
| Wrangler LXXXV 256KiB transport fix | Original local `~/AUREX_NEXT/valexii_repair` and source snapshot | Isolated code tested; check exact Lovable source and avoid overwriting current modifications |
| Local AUREX API auth and worker | canonical main vs deployed Railway SHA | Preserve bearer server-only; 401/200 proof must be measured from authorized actual Worker path |
| Real company USB local 6→24 PDF pilot | Fix Wrangler R1 ZIP and owner-private filesystem | User-side local report only; do not commit/export bytes, names, account data, OCR or diagnostic logs |
| XC synthetic finance & older financial review | PR #80 / older local ZIP / spec #77 | Audit for duplicates/typed Decimal/provenance; import only reviewed modules |
| XCV+ APIS PRIME unified spine | draft PRs #84–#86 | Exact-head local tests, independent negative controls, no fourteen UI tabs |
| Folio source catalog | draft PR #88; some source ported to #89 | Use one resolved implementation; immutable source IDs, no cross-tenant leak |
| 9-source fictional proof | draft PR #89 | Compare adversarial findings to reported 24 real documents WITHOUT ingesting real data |
| New XCIX cross-thread taxonomy + convergence contract | this draft PR | Apply to company classification; NOT deployed or integrated into final Folio/Spine yet |
| Published user-facing site | Lovable project source `b1d00f...` (source only) | Published yes; newest source **not verified published**; no simulated 100% |
| Independent release | Jules GitHub issue #87 and master evidence ledger #75 | Reproducible exact SHA CI, independent review, staged-approved E2E, then separately approved effect |

## 4. Strict promotion gates

**G0 Source:** reconcile newest GitHub, local installer ZIP *hash and bytes*, actual Lovable current source and deployed Railway SHA. 24 PDFs are private; inventory only sanitized counts.

**G1 Ingest:** isolated owner-only local read of consented records; PDF parsing confidence and provenance, no implicit OCR claims. Preserve original file bytes read-only and hash transforms separately; reject symlinks, unapproved paths, duplicate records and secrets leakage.

**G2 Interpret:** deterministic financial Decimal/unit/date logic, strict document-type triage, optional local Qwen only with explicit scope and approval. Validate reference IDs and source chain. Never silently treat absent amounts as zero.

**G3 Challenge:** use independent domain examiner persona with falsifiable objections tied to primary sources; tax/DOT/insurance conclusions remain *advisory*, never certified or legal opinions.

**G4 Prove:** exact source SHA tests, Ruff/Mypy, privacy/fencing/leak/adversarial tests, independent evidence; public website no unapproved customer data. Keep "Code → CI → Deployed → E2E proven" as **different evidence rungs**.

**G5 Authorize:** human compliance/financial reviewer and explicit owner production authorization; release HOLD before both.

## 5. How two-way sync works in practice

**Fix Wrangler → APIS:** new local Wrangler/Railway/auth/R1 pilot evidence should append a dated, sanitized receipt to **GitHub issue #75**, referencing exact SHA and run results. APIS PR work consumes this receipt, **never private raw input**.

**APIS → Fix Wrangler:** every APIS Folio/financial/Qwen test result or name/contract change should append a dated, sanitized receipt to issue #75 and link the applicable PR (#86, #88, #89, this XCIX PR). Fix Wrangler must consume these *same* versioned definitions rather than create a parallel backend.

**Human conversation limit:** neither thread can be automatically rewritten by a GitHub comment. For chat-side continuity, paste or reference this document in the other chat; the GitHub issue + this versioned document constitute the **durable shared project record**.

**Protected branches:** new changes occur on fresh main-derived work branches, not direct main and not by bulk merging legacy branches. Do not paste secret-bearing logs into the shared issue or GitHub. No auto-deploy, merge, paid LLM API or unapproved live document ingestion.

**AUTHORITATIVE SAFETY DOCTRINE:** Evidence → Qualification → Reality → Authority → Effect; historical truth != current authority; UNKNOWN ≠ SAFE; absence ≠ zero; no-self-witness; CUSTOS/SHRIKE demote-only; ORB MOTION AUTHORITY = NONE; `external_spend_usd=0` default.

**Status: CROSS-THREAD CONTRACT PROPOSED FOR REVIEW, NOT LIVE FULL-STACK CONVERGENCE.**
