# AUREX/OX — Four Dimensions of Engineering Ambition

**Canonical user-approved development principles:** **SPEED · ALTITUDE · DEPTH · RANGE**

**Locked:** 2026-10-17. **Applies to:** VALEXII.AI / AUREX-OX engineering, website UX, API/backend, governed agent development, BCXMET integrations, DISPATER.AI, research and the private financial-evidence program.

This document defines *how to prioritize, implement, and independently assess future work*. It does **not** assert that unshipped AUREX capabilities are live, guarantee business outcomes, or change the security and authorization architecture.

## I. The four dimensions

| Dimension | Operational interpretation | Minimum credible evidence |
| --- | --- | --- |
| **SPEED** | Shorten time-to-useful-result, reduce repetitive work, latency, excessive rendering, CPU/battery consumption, CI feedback time, and outage recovery time. | Comparable before/after measurements; a performance regression test; functionality and accessibility retained. |
| **ALTITUDE** | Prioritize the *result that matters*—a responsive interface, reliable integration, completed independently reviewable task, or paying customer's measurable outcome—over a high count of tickets, agents, PRs or visual effects. | A named end-user or business outcome, observable acceptance criteria, verified end-to-end measurement and clear owner signoff. |
| **DEPTH** | Go beneath symptoms: inspect code, data, runtime state, root causes, trust boundaries, adversarial cases and domain-specific failure modes. | Reproduction, differential diagnosis, independent verification, provenance, controlled negative tests, unresolved risks recorded. |
| **RANGE** | Combine disciplines—AI governance, Android cybersecurity, UX, oilfield operations, finance, deployment, privacy, accessibility, mathematics and commercialization—through explicit bounded contracts. | Integration tests across boundaries, data-minimization evidence, cross-discipline expert/independent review, security and cost gates. |

**Interpretation:** These dimensions are complementary priorities; they do not confer execution authority or constitute four new AI subsystems. A task that is fast but insecure is **FAIL/HOLD**, not success. More disciplines integrated without proof is not more intelligence.

## II. Altitude: four primary AUREX/OX outcomes

### Outcome A — Responsive and usable AUREX/OX

User perceives prompt page interaction, especially on modest Android devices.

- **Immediate P0**: optimize the Ouroboros/Orb projection before adding OX features; static-by-default/reduced-motion, on-screen lifecycle, controlled animation, render isolation, and mobile readability.
- **Measure**: before/after long tasks and browser CPU samples under matched 4× throttling, real mobile usability when available, first interaction responsiveness, keyboard/focus behavior, viewport/scroll integrity, reduced-motion fidelity.
- **Evidence constraint**: one previous 6.5s synthetic browser sample detected 260 SVG paths and one 101ms long task; it is **not** verified real-device FPS. No speedup claim without matched after-measurement.
- **Gate**: current Lovable credits had blocked applying the prepared P0 patch; source-level fix, measured improvement and published website status remain **NOT VERIFIED**. Tracking: Issue #71.

### Outcome B — Secure, authenticated website-to-canonical-backend integration

VALEXII.COM's *published* server-side proxy completes all five read-only GET requests from a verified production backend:

`/v1/health`, `/v1/capabilities`, `/v1/evidence`, `/v1/budgets`, `/v1/jobs`.

- Keep service credentials server-only; strict schemas; reject redirects, credential exfiltration and invalid payloads; owner endpoints gated by real session and role/owner identity.
- A healthy network response does **not** establish independent proof of AUREX intelligence, activity, or system authority.
- **Evidence:** endpoint-by-endpoint status, exact deployment source SHA, timestamp, backend identity, privacy-safe owner-only diagnostic, repeatable rollback.
- **Gate:** current Railway service is an older read-only bridge, not the canonical worker/DB backend; source-code proxy exists but live website-origin authenticated five-endpoint proof is still **NOT VERIFIED**. Tracking: Issue #65, draft PRs #66 and #72.
- Do not paint the screenshot's static progress bars as live telemetry.

### Outcome C — Independently reviewable governed execution, with $0 default spend

On an explicitly authorized, owner-only test environment, a bounded offline request follows:

`Owner request → permission/budget/lease check → fenced worker → durable SQLite → evidence record → website review`.

- **Measure:** idempotency, cancellation, lease expiry/revocation, restart recovery, durable readback, independent ground truth, error/failure containment and zero unauthorized network cost.
- **Evidence:** redacted request ID, exact SHA, timestamps, job state transitions, evidence integrity, and at least one independent adversarial check; no model self-attestation.
- **Gate:** mainline code contains the building blocks, but current production worker + live persistent DB + evidence → website are **NOT VERIFIED**. No write-probe or job submission without explicit owner approval.

### Outcome D — Demonstrable customer value and ethical monetization

AUREX Financial Evidence Review initially investigates oilfield-service invoices, tickets, purchase orders, credits and payments, with human-reviewed discrepancy evidence.

- **Measure:** document text availability and labeled extraction accuracy, reconciliation precision/recall, false positives and misses, time saved, fully loaded per-customer costs, revenue collected and customer retention.
- **Market proof:** consented paying pilots and independent outcome review; public site does not claim customer traction before evidence.
- **Privacy:** local USB originals and financial SQLite data remain private; no automatic uploads, financial transfers or unaudited web exposure.
- **Gate:** 9.9/10 commercial potential remains an **ASPIRATIONAL TARGET**, not an achieved/independently substantiated rating. Tracking: Issues #68/#69 and draft PRs #67/#70.

## III. Mandatory evaluation card for every significant change

Create a short record (PR body, issue or release evidence entry) with these fields:

1. **Outcome and owner**: user or business benefit; which Outcome A–D.
2. **Dimensions**: Speed, Altitude, Depth and/or Range, with a concrete explanation.
3. **Baseline and expected change**: measured values with source/time, or `UNKNOWN`.
4. **Implementation scope and blast radius**: files, APIs, users, secrets, data flows and deployment boundaries.
5. **Evidence**: tests run, before/after metrics, exact SHA, reproducible procedure, external witness and limitations; label `PASS`, `FAIL`, `NOT RUN` or `NOT VERIFIED` for each claim.
6. **Security and privacy**: authentication, least privilege, sensitive data, independence of reviewer, user consent, retention.
7. **Costs**: one-time and recurring cloud/model/compute costs, default **$0**, actual approval before any charge.
8. **Rollback and residual blockers**: non-destructive fallback, state/data safety, who can approve effect.

**Scoring discipline:** Do not manufacture percentages, test counts, commercial numbers, claimed speed improvements or "green" integration gates. If source, deployment and end-to-end observations conflict, the less favorable current authority wins.

## IV. Unchanged security constitution

**Evidence → Qualification → Reality → Authority → Effect.**

- **No self-witness:** a model, heuristic, generated score, test runner or status endpoint cannot independently certify its own correctness.
- **Unknown ≠ healthy; missing/stale/failed evidence ≠ PASS.** Treat it as **HOLD** until resolved.
- **ORA/Orb/Ouroboros: ORB MOTION AUTHORITY = NONE.** Animation, UX glyphs and status decorations must never drive security or financial decisions.
- Human/owner authority, server-side authentication, independent Policy/World/Adversarial review, bounded budgets, and reversible deployment gates remain mandatory.
- Research/finance/security evidence stays privacy-minimized; no unsupported production, AGI, patent, security, revenue, partner, benchmark or certification claims.
- **No merge to protected main, live Railway patch acceptance, Lovable publication, purchase, enabled worker, or private document upload** by merely adopting this framework. Such operations require separate documented authorization and evidence.

## V. What "locked" means

These four dimensions are now the **default engineering prioritization and review framework** for work on VALEXII-AUREX/OX.

Locking the methodology is not implementing the desired outcomes. Changes to this framework require an explicit review and the owner's direction. Keep product identities, private/public boundaries, other approved architecture contracts and no-self-witness rules intact.
