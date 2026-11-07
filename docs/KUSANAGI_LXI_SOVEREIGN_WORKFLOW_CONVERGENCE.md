# KUSANAGI LXI — Sovereign Workflow Convergence

Status: FOUNDATION CANDIDATE; no production admission. Date: 2026-10-16.
Owner: VALEXII.AI. Canonical backend repository: `victormart43210-ship-it/Valexii-Aurex`, protected `main`.

## Inventory and boundaries

- **AUREX**: canonical FastAPI API, fenced worker, SQLite evidence and $0 budget. Source of backend execution truth; no model or worker may self-certify.
- **AUREX/OX**: VALEXII.COM Lovable frontend, server-side authenticated proxy, owner experience, evidence status. Presentation and user intent, NOT execution authority.
- **Railway**: production `aurex-api` is online but runs the OLD read-only integration bridge; no live volume. Persistent `/data` patch staged, not live. Docker candidate PR #47 passed prior CI but remains unmerged.
- **BCXMET**: Android client is a separate product/repository, never an alternative AUREX backend; V42 development, V43 planned beta, V44 planned Play release. Public claims must remain evidence-bounded.
- **Other owner GitHub repos inspected by metadata**: `CoreGuard-Android` (private), `cli`, `log-dog-android-sdk`, `vigilant-engine`, `Valexii-nexus` (minimal), plus an empty malformed-name repository. No evidence any is a replacement AUREX backend. Full code review of these repos NOT RUN.
- **Legacy AUREX PRs**: many open PRs (#3–#48), overlapping older branches. Treat as evidence/review inputs, never bulk-merge or rebase new work on them. PR #48 contains agent knowledge and curated Firecrawl findings, pending independent checks.

## Invariants: one directed authority flow

`Evidence → Qualification → Reality → Authority → Effect`; reverse audit `ROTAS`.
- No self-witness; `UNKNOWN != HEALTHY`; unverified observations cannot promote authority.
- ORB MOTION AUTHORITY = NONE; website graphs and visualizations are presentation only.
- Backend tokens never appear in browser bundles. All website requests cross a server-side authenticated proxy.
- Production execution HOLD; default external spend $0; no live fuzzing, scraping-as-execution or unapproved model downloads.
- Versioned contract and deployment SHA required; code passing CI does not prove deployed capability.

## Canonical integration sequence

```text
Browser /aurex/ox
  -> Lovable server-side authenticated proxy (owner session; bearer secret stays server-side)
  -> AUREX canonical /v1/capabilities and /v1/jobs
  -> budget/authorization gate (default $0; offline regression_scan only when explicitly enabled)
  -> atomic SQLite job + fenced worker lease generation/token
  -> digest-bound evidence (RECORDED, UNVERIFIED until independent witness)
  -> /v1/jobs and /v1/evidence readback
  -> website state: HOLD | NOT VERIFIED | FAILED | independently PASS
```

## Source-derived tool adoption (reviewed references, not copied code)

| Origin | Candidate | Concrete AUREX benefit | Gate |
| --- | --- | --- | --- |
| Astral docs / global Python 2026 | uv | Reproducible faster dependency install | Benchmark against pip; pin version/lockfile; no unreviewed dependency churn |
| Astral docs | uv audit | Known dependency vulnerability reporting | Validate command/version in actual pinned uv release; compare pip-audit; triage rather than auto-upgrade |
| Astral | Ruff, ty | Fast lint/type feedback | Keep existing Ruff/Mypy blocking; ty nonblocking benchmark until equivalent diagnostics proven |
| Schemathesis | OpenAPI schema-based adversarial API tests | Catch malformed input, auth and contract mismatches | Disposable local DB, synthetic credentials, fixed runtime/seed, never production |
| Hypothesis | Property-based state machine tests | Lease, revocation, idempotency, concurrent claim invariants | Deterministic reproductions; independent review |
| pytest-xdist | Parallel independent tests | Reduce CI wall time | Isolate SQLite paths and ports; serial lease-race suites |
| OpenTelemetry | End-to-end trace IDs | Diagnose proxy/API/worker/evidence gaps | Token/PII redaction and sampling, no automatic paid exporters |
| Jason Scott / TEXTFILES.COM | simple process lifecycle, archive index, browser compatibility | Restart/backup runbook, durable knowledge index, cross-browser tests | Historical context, NOT executable security guidance |
| Book of Secret Knowledge | operations/security reference index | Diagnostic checklists | Verify individual sources and licenses; do not execute archive scripts |
| GitHub gitignore | secret/artifact hygiene | Prevent accidental DB/key tracking | Review tracked history; never hide source/evidence |
| Ghostfolio | UI/API separation design study | Clear API ownership and accessible states | AGPLv3: architecture study only; do not copy source |
| Greek Apertus | optional multilingual model eval | Future language benchmarking | Independent benchmark, model/license review; no default inference |

## Immediate dependency DAG (serialized authority, parallel only where safe)

**Gate A — inventory and freeze:** record exact `main` SHA, relevant PR heads, current Lovable commit and deployed Railway source SHA; freeze OpenAPI schema and auth/error response fixtures. Resolve conflicting PRs by cherry-picking verified patches only.

**Gate B — isolated Python acceleration:** measure baseline `pip install`, Ruff, Mypy and pytest on same CI runner; separately trial pinned uv/uv audit, nonblocking ty, bounded Schemathesis/Hypothesis tests. No production dependencies changed until verified.

**Gate C — backend release candidate:** independently review PR #47 Docker image, `PORT`, non-root, SQLite `/data`, restart persistence, migrations, worker fencing and $0 gate. Require exact-head CI, security and rollback checks before proposing merge.

**Gate D — staged infrastructure:** reconcile Railway source root and staged volume/variables with the reviewed release SHA. Never accept/deploy staged changes until owner authorization and independent checks.

**Gate E — frontend integration:** match Lovable proxy routes, payload casing, auth and HTTP error semantics to the *deployed* API. Add a synthetic owner-only $0 probe, evidence readback, honest capability states, mobile/cross-browser and reduced-motion checks.

**Gate F — independent production admission:** health/version/source SHA, 401 without bearer, scoped authenticated request, durable readback after restart, lease revocation and negative cases, full browser → API → worker → evidence proof. Record evidence and rollback. If any fail: HOLD.

## Metrics (baseline before improvement claims)

Record install duration, lint/type duration, unit/API suite duration, reproducible failure rate, E2E pass rate, deployment recovery time, cost, and exact SHAs. Never invent percentage gains or show a public progress bar as measured without numerator, denominator, criteria, timestamp and evidence.

## References

- https://docs.astral.sh/uv/
- https://astral.sh/blog/uv-audit
- https://docs.astral.sh/ty/
- https://schemathesis.readthedocs.io/en/stable/
- https://hypothesis.readthedocs.io/
- https://pytest-xdist.readthedocs.io/
- https://opentelemetry.io/docs/languages/python/
- https://ascii.textfiles.com/archives/819
- https://ascii.textfiles.com/archives/776
- https://ascii.textfiles.com/archives/4501
- https://github.com/trimstray/the-book-of-secret-knowledge
- https://github.com/github/gitignore
- https://github.com/ghostfolio/ghostfolio

**Release disposition: NOT VERIFIED / HOLD.** This document is a convergence contract, not evidence of completed integration.
