# AUREX existing-system improvement groundwork — 2026-10-15

Status: DESIGN/REVIEW ONLY. No new architecture, services, frameworks, runtime dependencies, deployments, or merge authority. This document scopes incremental changes on the existing PR #29 branch. All checks are NOT RUN until independently executed.

## Verified local source inventory (GitHub connector)
- PR #29 branch `work/kusanagi-xxxviii-convergence-staging` was based on PR #28's fenced worker/API/SQLite implementation, with the two scientific evidence files from PR #27 added.
- Existing modules: `aurex/worker.py` (`execute_claim`), `aurex/database.py` (`claim_job`, `heartbeat_job`, `finish_job`, `fail_job`, `record_evidence`), `aurex/api.py` (job, capability, budget, evidence endpoints), `aurex/scientific_evidence.py` (`execution_manifest`, `evaluate_exact`, `unsigned_statement`, `verify_manifest`).
- These modules exist; their interoperability and production correctness are NOT VERIFIED.

## Adopt techniques, not platforms

| Inspiration | Minimal change inside existing AUREX | Required negative test |
| --- | --- | --- |
| Temporal durable execution | Use existing SQLite conditional claim/heartbeat/finish logic with lease fencing and replay-safe idempotency. No Temporal service. | Expired lease or old worker token cannot finalize a new claim. |
| Inspect AI scoring | Feed real persisted worker output into existing `evaluate_exact`; distinguish incorrect output from missing/unscored execution; report evaluated count and coverage. No Inspect dependency. | Missing output cannot become PASS or be excluded silently from denominator. |
| REANA reproducibility | Bind existing `execution_manifest` to actual persisted input/output digests, environment identity and worker version. No REANA service. | Modified output or changed input fails integrity validation. |
| in-toto attestations | Keep `unsigned_statement` explicitly unsigned until a trusted authorized signer is configured; verify exact subject digest and predicate before any VERIFIED display. | Unsigned, untrusted, revoked, or tampered evidence never receives VERIFIED. |
| OPA authorization | Keep existing server-side owner/role checks as one consistent allow/deny decision; default DENY. No OPA deployment. | Browser token or unauthenticated user cannot read another owner's job. |
| LangGraph / CrewAI | Keep existing coordinator and bounded job transitions; log parent/child lineage only if existing schema supports it safely. No graph framework. | Cyclic/replayed job transition cannot grant authority. |
| MLflow / LangSmith / Langfuse / Phoenix | Reuse existing evidence/job identifiers as trace correlation IDs; capture timestamps, error class, and actual duration without secrets. No observability service. | Logs and responses never leak bearer tokens or prompts containing secrets. |
| Sigstore | Apply trusted-key allowlist, key ID, revocation and Ed25519 checks to existing evidence verifier if implemented. No Sigstore service. | Valid signature from untrusted key is rejected. |
| Frontend usability | Use existing API status to show CONNECTED, UNAVAILABLE, RUNNING, COMPLETED, VERIFIED, NOT VERIFIED accurately. No new dashboard product. | HTTP 200 alone never produces VERIFIED; 503 never produces success. |

## Work packages (no new architecture)

1. **Source and contract freeze:** reconcile PRs #19/#22/#26/#27/#28/#29 and locate Jules XXXVII exact SHA. List the authoritative frontend source. Keep a single canonical contract for `/health`, `/v1/capabilities`, `/v1/jobs`, `/v1/evidence`, and budgets. Avoid schema rewrites.
2. **Durability:** test and repair existing SQLite state transitions and evidence immutability; owner-scoped idempotency, bounded lease expiry, crash recovery, cancellation races. Reuse PR #26 improvements only after comparing with PR #28's different schema.
3. **Execution-to-evidence wiring:** add the smallest calls from real `execute_claim`/persisted results into `execution_manifest`, `evaluate_exact`, and statement generation; ensure worker crash/disabled returns honest non-PASS.
4. **Independent verification:** reuse existing trust registry if present; require key authorization, Ed25519 signature validity, input/output hash consistency, and independent scoring before VERIFIED. If absent, return NOT VERIFIED instead of inventing verification.
5. **Frontend bridge:** identify authoritative Lovable source; implement authenticated server-side proxy with secrets never in browser; map real backend state to existing UI. Test backend + proxy + browser against same job ID. Do not deploy.
6. **CUSTOS/CI:** run exact-head `python -m pytest -q`, `ruff check .`, `mypy aurex --strict`, applicable frontend tests/build and hosted CI; record real counts, URLs, hashes, failures and skips.

## Strict acceptance gates
- One authenticated real job round trip: frontend -> proxy -> API -> worker -> SQLite -> evidence -> independent verifier -> frontend.
- An unavailable worker produces HTTP 503 without persisted fabricated success.
- No synthetic success, no self-witness, no automatic authority escalation.
- Exact-head CI PASS for all required suites; adversarial cases PASS.
- No merge, deployment, DNS changes, paid inference, secrets, or production migrations without explicit owner authorization.
- Until all required evidence exists: RELEASE HOLD / NOT VERIFIED.

## Research provenance
- Temporal durable execution: https://docs.temporal.io/temporal
- Inspect AI scoring: https://inspect.aisi.org.uk/scoring.html
- in-toto attestation parsing and monotonicity: https://github.com/in-toto/attestation/blob/main/spec/v1/README.md
- REANA: https://reanahub.io
- OPA: https://www.openpolicyagent.org
These are design references, not newly installed packages.
