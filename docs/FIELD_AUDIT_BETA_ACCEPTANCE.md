# AUREX FIELD AUDIT — Beta admission gate (synthetic only)

**State: BETA CANDIDATE / RELEASE HOLD — 2026-10-19**

Commercial direction **C**: start with oilfield invoice/field-ticket verification; then towing; long term enterprise automation verification. This is a readiness gate, **not** a production financial-audit engine or an approved customer pilot. AUREX remains a witness, not an authority. **No Lovable credits spent. No launch or merge.**

## One canonical repo; existing work remains unmerged

- Mainline `victormart43210-ship-it/Valexii-Aurex` is canonical. This proposal does **not** create another financial-audit runtime.
- Existing **draft PR #89** contains synthetic-company dossier/reconciliation/traceability and AUREX challenge HOLD; review and selectively reconcile it after independent tests.
- Existing **draft PR #80** contains a separate encoded financial-review kit; decode and inspect offline before considering any reuse. Do not execute unreviewed installers.
- Current publicly hosted AUREX bridge is **read-only**; a reachable health check is not proof of inference, auditing, independent evidence or tenant isolation.

## Runnable 100-case source-separated acceptance set

A standalone, dependency-free acceptance tool creates **100 fictional** invoice/ticket/rate scenarios and a SHA-256-bounded suite. It is NOT an implementation of the financial review engine. A separate candidate must produce results against the fixtures, without seeing ground-truth labels:

```bash
python3 -m workstation.field_audit_beta_gate --cases > /tmp/aurex-field-audit-100-cases.json
# Run a separately implemented candidate against the cases and write a result JSON.
python3 -m workstation.field_audit_beta_gate --score /tmp/aurex-field-audit-candidate-results.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_field_audit_beta_gate.py
```

Case inventory: **40 consistent**, **20 overbilled**, **10 underbilled**, **10 ticket/rate mismatches** (two flags each), **10 missing rate approvals**, **10 duplicate invoice IDs**. The fixed fixture oracle expects **60 flagged cases / 70 finding labels**, with none of the 40 consistent cases implying a security, financial or payment clearance. Integer cents, not floating-point currency. Cases contain no real names, identifiers, customer files, or uploaded documents.

Candidate result JSON schema:

```json
{
  "schema": "aurex.field-audit-beta.results.v1",
  "synthetic": true,
  "suite_sha256": "COPY_VALUE_FROM_EMITTED_CASES",
  "results": [
    {
      "case_id": "BETA-001",
      "flags": [],
      "authority": "HOLD",
      "independent_verification": "NOT_VERIFIED",
      "effect": "NONE"
    }
  ]
}
```

The candidate must return **all 100 case IDs exactly once**; every row must contain *only* the documented keys and known flags. The gate explicitly rejects unverifiable authorization claims, extra/missing cases, unknown flags, duplicate IDs, malformed JSON, oversized files, symlinks, and suite SHA mismatch. The gate prints `SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE` **only if** all 100 cases match the fixture oracle exactly with 0 FP and 0 FN, but even that outcome remains **NOT VERIFIED / HOLD** for production. No score is emitted until external candidate results are provided; reference expectations in tests exercise the gate itself, not AUREX's production accuracy.

## Required gates to authorize a closed beta

1. **Contract & review:** Independent reviewer checks the exact branch/commit, the packet input schema, source authenticity protections, no-self-witness, threat model, tests and any PR #89/80 dependencies. No duplicate engines.
2. **Real functional integration:** Run an owner-authorized, $0, end-to-end trace through authenticated website proxy → deployed versioned AUREX API → fenced worker/SQLite → evidence receipt → owner UI. Prove rollback/failure handling; do not rely on transport-only health checks. Keep production on HOLD until verified.
3. **Pilot privacy:** Tenant RBAC, explicit consent, encrypted storage, retention/deletion schedule, no training by default, isolated logs, customer document ingestion bounds and a security review are prerequisites for any real customer paperwork. None is established by this fixture suite.
4. **Accuracy:** Execute this 100-case battery against the *actual candidate engine*, publish confusion matrix and error examples, then validate a separately held-out set sourced with an industry reviewer. Never describe fixture self-tests as externally validated field accuracy.
5. **Human control:** Every finding remains `HUMAN_REVIEW_REQUIRED`; dispute handling and human decision log exist before any external action. NO invoice payment, tax/DOT compliance opinion or financial certification implied.
6. **Commercial pilot:** One identified consenting oilfield pilot with agreed scope, written data handling, baseline review time, $ impact independently confirmed, false-positive rate, per-case review cost, and human sign-off. Towing only after oilfield proof.
7. **Release:** GitHub Actions on exact head, independent security/adversarial tests, signed deployment evidence, mobile usability checks, and explicit owner approval. Keep `main`, website, Railway, Cloudflare and customers unchanged until admission.

## Release dashboard (as of this PR)

| Gate | Status |
| --- | --- |
| Public synthetic fixture generator + local acceptance evaluator | IMPLEMENTED / awaiting independent review |
| Evaluator's own regression tests | See exact-head CI/test logs |
| 100 candidate audit responses checked against the oracle | **NOT RUN** |
| PR #89 / #80 independently reviewed and merged | **NOT VERIFIED / HOLD** |
| Owner identity, tenant privacy, end-to-end service/website | **NOT VERIFIED / HOLD** |
| Paying oilfield pilot or real invoice accuracy | **NOT VERIFIED / HOLD** |
| Production beta | **NOT AUTHORIZED** |

**Rollback:** Close this draft PR or revert its new files; no persistent migration or deployment occurs. Evidence → Qualification → Reality → Authority → Effect. **The system may never be its own sole witness.**
