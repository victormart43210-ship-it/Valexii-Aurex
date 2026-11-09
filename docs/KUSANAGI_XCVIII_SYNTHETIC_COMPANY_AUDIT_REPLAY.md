# KUSANAGI XCVIII — SYNTHETIC COMPANY EVIDENCE REVIEW (ONE-SPINE REPLAY)

**Status: DRAFT / HOLD, offline research demonstration.** No real enterprise records, no CPA financial audit, no IRS/DOT compliance determination, no payments, no API changes, no Lovable/Railway/Cloudflare deployment, no LLM training or paid inference.

## Scope and dependency reconciliation

This isolated PR is based on **current canonical main** `df0654390049118a142ec3b3356f0f40b4789fe4`, consistent with `docs/AGENT_MAINLINE_POLICY.md`. It **ports and directly uses** the metadata-only Folio Index originally proposed by **draft PR #88**, without merging #88. It adopts the **one-view NOW → CHANGED → NEXT → WHY → PROOF contract** from **draft PR #86** but does **not** copy the unmerged fourteen-role runtime; it calls the existing **`aurex.engine.AurexEngine`** directly with no independent challenger, which correctly results in HOLD.

**PR #80** contains an unmerged archived synthetic invoice audit kit that is review input for future integration, not an implemented upstream dependency of this PR. **PR #77** is a financial review design. The behavior here is a bounded new direct implementation; no claim that the older PRs have merged or reached production. Do not create a second AUREX backend.

## What the bounded fictional package represents

Fictional entity `fictional_northstar_001`, tenant `demo-tenant`, 2026-09. Nine **invented** UTF-8 JSON source documents and one manifest pin each original file's SHA-256:
- A purchase order for **$42,000** (10 units × $4,200)
- A vendor invoice for **$48,000** (10 × $4,800)
- A field ticket for **$42,000** on September 15
- A payment register for **$48,000**
- A fictional bank statement transaction of **$47,950** (masked account only)
- A September general ledger expense of **$46,000**
- A synthetic tax-summary expense of **$42,000**
- A DOT packet checklist referencing a missing inspection source `INSP-1001`
- A fictional insurance certificate with `expires_on=2026-08-31`

**This is a nine-document representative packet, not all records of an actual company.** Real audit readiness would additionally require source completeness, records retention, authorization, authenticity, signatures, ledger controls, period boundaries and professional review.

## Execute and independently replay ($0, offline)

From this branch, with Python >=3.12 and a local checkout:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  tests/test_folio_index.py tests/test_audit_pilot.py
python -m compileall -q aurex/folio_index.py aurex/audit_challenge.py \
  aurex/audit_pilot.py workstation/audit_pilot_cli.py
ruff check aurex/folio_index.py aurex/audit_challenge.py \
  aurex/audit_pilot.py workstation/audit_pilot_cli.py tests/test_audit_pilot.py
mypy --strict aurex/folio_index.py aurex/audit_challenge.py \
  aurex/audit_pilot.py workstation/audit_pilot_cli.py

python -m workstation.audit_pilot_cli \
  --packet fixtures/synthetic_company_packet \
  --out /tmp/aurex-synthetic-review.json
python -m workstation.audit_pilot_cli \
  --packet fixtures/synthetic_company_packet \
  --verify /tmp/aurex-synthetic-review.json
```

Choose a **new output filename**, because the CLI refuses overwrite; the resulting JSON is private, permission 0600 on POSIX. The local replay verifies report hash *and recomputes the entire report from the original nine sources*. Hash consistency is not source authenticity, independent reviewer proof, or a cryptographic signature.

The no-follow bounded reader denies symlinks, unreadable sources, malformed JSON, duplicate keys, oversize files, out-of-folder paths, unlisted extra docs, missing originals, wrong type/company linkage and unverified manifest hashes. Floating-point money is not accepted: canonical fixed-cent strings and Python `Decimal` are required.

## Expected outcomes on the original synthetic packet

**9 original sources, 7 deterministic review flags, 7 canonical AUREX `HOLD` challenge outputs, 1 consolidated report, 0 new dashboard tabs.**

| Review flag | Source evidence | Expected finding |
| --- | --- | --- |
| `INVOICE_EXCEEDS_PO` | INV-1001 / PO-1001 | $6,000 |
| `INVOICE_VS_FIELD_TICKET` | INV-1001 / FT-1001 | $6,000 |
| `PAYMENT_VS_BANK_STATEMENT` | PAY-1001 / BANK-1001 | $50 |
| `LEDGER_VS_INVOICE` | GL-1001 / INV-1001 | $2,000 |
| `TAX_SUMMARY_VS_LEDGER` | TAX-1001 / GL-1001 | $4,000; not an IRS finding |
| `DOT_SUPPORT_NOT_IN_PACKET` | DOT-1001 | Inspection source missing from this packet, not proof of noncompliance |
| `INSURANCE_CERTIFICATE_EXPIRED` | INS-1001 / FT-1001 | Submitted certificate predates service, actual coverage unknown |

**Never add those amounts together**: several findings refer to the same transaction and are not separate financial losses.

An `AurexEngine` with **no external independent challenger** returns `HOLD`, even when its evidence references contain SHA-256 fingerprints. All business findings are `HUMAN_REVIEW_REQUIRED`, **authority NONE**, and **independent verification NOT VERIFIED**. This does not complete an audit, determine a tax violation, establish an insurance lapse, or establish DOT noncompliance.

## Integration boundaries

```text
fictional 9 source files + immutable source SHA
                   ↓
         typed manifest admission
                   ↓
         Folio Index (private metadata)
                   ↓
        typed cross-document relations
                   ↓
       deterministic Decimal/date checks
                   ↓
         AUREX canonical challenge engine
         7 HOLD results (no independent reviewer)
                   ↓
           ONE PRIVATE APIS PRIME REPORT
       NOW / CHANGED / NEXT / WHY / PROOF
                   ↓
          local replay against original files
                   ↓
           CUSTOS RELEASE HOLD
```

**Folio metadata** is in memory only; original files remain owned by the operator and are never rewritten. The actual full shared APIS PRIME 14-role dispatcher from PR #86 is a **future typed-adapter integration gate**, not in this base-main PR. Documents are NOT copied to public cloud, sent to Qwen, uploaded to the website, converted into model weights, or automatically shared between tenants. Real private enterprise intake needs authenticated server-side authorization, durable cryptographically reconciled source storage, retention/deletion, encryption and legal review.

## Verification honesty and release

The author ran **18 synthetic unit/negative-control tests in an isolated local Python 3.13.5 fixture using a contract-compatible Folio/engine stand-in**, with `pytest` PASS and `compileall` PASS. The local demo produced **9/7/7** and an internally replay-matching report. These are **not** independent exact GitHub HEAD proof; `ruff`, `mypy --strict`, CI, complete canonical suite, real tenant RBAC, production site/API worker round-trip and independent reviewer are **NOT VERIFIED**. Reproduce on the exact GitHub SHA before promotion.

No real file inputs permitted by this prototype unless explicitly converted into a new, consented, separately reviewed production ingestion workflow. User-authorized **financial, DOT, IRS and insurance audits remain preparation/review use cases**, not automatic certifications. Observe no-self-witness, Evidence → Qualification → Reality → Authority → Effect, and **$0 unapproved external spend**.

**Disposition: SOURCE REVIEW ELIGIBLE, RELEASE HOLD.** Rollback: do not merge; closing the PR leaves production unaffected. After reviewer approval, reconcile #88 and #86 to avoid duplicate Folio Index files and test the one-spine adapter with independent witness controls.
