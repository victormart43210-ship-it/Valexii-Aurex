# Lovable handoff — VALEXII.COM / AUREX integration (credit-efficient)

**Goal:** Refine the existing VALEXII.COM website, not build a duplicate repository. User prefers no more than 10 Lovable credits; one consolidated implementation request, then one review pass. First identify canonical website repo and exact main SHA; confirm whether `Valexii-nexus` is website source or a historical fork. Preserve current branding and working pages.

## Deliverable
- Premium restrained VALEXII visual language; mobile-first dashboard with accessible typography, keyboard controls, readable statuses, loading, empty, unauthorized, unavailable, and retry states.
- AUREX job activity shows only `id`, `kind`, `state`, `createdAt`, `updatedAt`; nextCursor pagination. Clearly label `PENDING_APPROVAL`, `APPROVED`, `RUNNING`, `COMPLETED`, `FAILED` and do not turn missing/stale data into success. No made-up results, metrics, usage, customer counts, or verified AI claims.
- **Production must use a server-side endpoint**, e.g. `/api/aurex/jobs`, which authenticates the logged-in website user, enforces owner/tenant permissions, and forwards to the protected AUREX service with a server-side secret. Do not expose bearer tokens in HTML, JavaScript, VITE_*, NEXT_PUBLIC_*, localStorage, logs, or browser requests. No unauthenticated cross-tenant access. Confirm real identity provider and session architecture before implementation.
- Proxy supports timeout, controlled 401/403/429/503, schema validation, rate limiting, correlation IDs without secrets, no caching sensitive responses, and an allowlisted API URL. Avoid browser direct calls to Railway or localhost.
- Read-only in first release: no Approve, Execute, Delete, or Spend buttons. Distinguish health of gateway vs verified execution state. Clearly show when database is unavailable.
- Ensure `npm run build`, relevant lint/tests, Playwright or equivalent browser smoke checks, desktop/mobile checks, and evidence screenshots at real routes. Document exact branch, PR, commit SHA, and CI results. Do not publish until explicit approval.

## Integration contract
GET `/api/aurex/jobs?limit=20&cursor=...` -> `{jobs:[{id,kind,state,createdAt,updatedAt}], nextCursor:string|null}`. Return `503` for backend unavailable; `401` unauthenticated; `403` unauthorized; `400` invalid cursor; do not fabricate empty arrays on error.

## Definition of done
Website source PR against canonical main, working server-side proxy with auth/tenancy, real persisted job retrieval, no client secret, production-safe error states, independent security review, and user-approved deployment. Until then mark NOT VERIFIED.
