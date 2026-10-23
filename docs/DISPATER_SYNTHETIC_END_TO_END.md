# DISPATER.AI — Synthetic End-to-End Demonstration

**Product direction:** one business intelligence layer for **towing/recovery** and **oilfield services**. Integrate with existing CRM, dispatch, ticketing, payroll, and accounting systems later—do not rebuild those systems for the first paid pilot.

**Status:** prototype source, **HOLD**. This branch is not merged, deployed, independent-reviewed, or permitted to receive real business records.

## What exists in this candidate

- `aurex/dispater_pilot.py`: deterministic, fictional **job → effective rate → invoice → payment** comparisons.
- `aurex/dispater_evidence.py`: fictional IRS/DOT **document index** check against explicitly supplied *demo* requirements; not a legal applicability or compliance assessment.
- `aurex/dispater_workflow.py`: bounded, fictional Make/Zapier-style automation proposals and tenant/role-aware retrieval concept; no running automations or secure knowledge gateway.
- `aurex/dispater_demo.py`: combines revenue and record-index findings; produces stable finding keys and optional explicit **demo manager review**; emits deterministic self-issued SHA-256 receipt.
- `examples/dispater_towing_synthetic.json` and `examples/dispater_oilfield_synthetic.json`: fictional-only demonstration inputs.
- `tests/test_dispater_pilot.py` and `tests/test_dispater_demo.py`: tests intended to run offline.

A self-issued digest is useful for *repeatable comparison only*; it cannot attest to independent accuracy or establish regulatory compliance. No model provider authenticates its own conclusions.

## Run locally (from repository root)

```bash
python -m pytest -q tests/test_dispater_pilot.py tests/test_dispater_demo.py

python -m aurex.dispater_demo \
  --input examples/dispater_towing_synthetic.json \
  --output /tmp/dispater-towing-report.json

python -m aurex.dispater_demo \
  --input examples/dispater_oilfield_synthetic.json \
  --output /tmp/dispater-oilfield-report.json
```

Use Python >=3.12 and repository dev dependencies. These commands never use the network. The `--output` path is an operator-chosen local file.

### Expected **fixture-defined**, not independently verified, findings

- **Towing:** unbilled recovery job, a rate/invoice difference on a completed hookup, and a paid-status reconciliation discrepancy. The illustrative DOT/IRS document index includes expired or missing metadata; the example is **not** a determination of applicable records.
- **Oilfield:** flowback field ticket without a matching invoice; no regulations asserted.
- **Manager:** the first report contains stable `finding_id` values. To demonstrate review, add one item to the input's `review.decisions` array with that key, `decision: "ACKNOWLEDGED"`, and a synthetic note. Re-run. Findings and receipt are recomputed; there is **no** bill posting, money movement or regulatory attestation.
- **NVIDIA:** `nvidia_inference: "NOT RUN"` and deterministic explanations. No fake AI calls or implied live provider access.

## Acceptance criteria

1. Both examples execute deterministically; no network, credentials, external services, or actual customer input.
2. No unknown schema fields, unsupported sectors, duplicate reviews, fabricated approvals, or unrecognized review keys are accepted.
3. Every candidate finding retains source hashes or rule identifiers, a consistent ID, and `HUMAN_REVIEW_REQUIRED` meaning.
4. Missing or unreviewed requirements remain unknown, never certified PASS.
5. A synthetic reviewer may acknowledge, dispute, or refer findings but cannot approve payments, dispatch changes, filings or invoices.
6. No real NVIDIA inference and no model call unless a separately authorized, reviewed adapter with explicit spending and data controls is admitted.
7. Source, tests, exact PR SHA, and independent reviewer must pass existing mainline admission gates before merge.

## Next work to make a client-safe pilot

**Not included in this demonstration:** verified tenant identity, encrypted document storage, retention/legal hold, jurisdiction applicability, payroll/privacy controls, connector authorization, immutable source attachments, secure audit trail, restore/recovery testing, API auth + upload bounds, independent witness signatures, real-time UI, or live Railway/NVIDIA integration.

A later authorized owner-only read-only upload route should validate tenant identity from a verified server-side session, scan and bound inputs, persist encrypted originals, import only permit-granted data, and keep all effects on HOLD pending human review. A reviewer knowledgeable about tax and applicable FMCSA/state rules must define and approve versioned rule packs before the product describes compliance readiness.

**Suggested pilot sequence:** fictional demonstrations → independently reviewed offline reconciliation → test a synthetic UI↔API↔worker loop in segregated staging → obtain counsel/security review and consent → one authorized towing pilot and one oilfield pilot. Keep production/staging mutation, paid inference, payroll/invoicing writebacks, and real customer records on HOLD until admission is explicitly approved.

### Public-facing claim policy

Use: **DISPATER.AI — Revenue Intelligence & Audit Readiness**, powered by AUREX/OX (developmental). Industry-specific dashboards for towing and oilfield, plus future consulting for workflow automation and private, citation-based company knowledge search. Mark all visual dashboards **CONCEPT PREVIEW · FICTIONAL DATA · NOT LIVE**. Maintain existing Lovable Roman Dis Pater artwork and the two homepage rainbow orbit rings. The project does not offer IRS certification, DOT certification, tax or legal advice, secure production RAG, or live customer audit services yet.
