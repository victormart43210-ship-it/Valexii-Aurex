# XIX source-controlled frontend

This is the TanStack Start React/TypeScript application imported into Valexii-Aurex at c98ca176ee0fb0e2f4a79427d0ee225eca6b0305. It builds outside Lovable. Node 22, npm and package-lock.json are the reproducible development entry point:

```sh
cd website
npm ci --ignore-scripts
npx tsc --noEmit
npx vitest run
npm run build
npm run dev
```

The production build uses the existing Nitro/Cloudflare target. Do not deploy this as static files: protected server functions must execute server-side. Preview deployment, production secrets, provider adapter selection, domain change and rollback execution are NOT VERIFIED or authorized here. CI performs checks only; no deployment step exists. Dependency advisory failures are release blockers, not auto-upgrade authorization.

## Owner command configuration

Supply server-only `AUREX_SERVICE_URL` (HTTPS, non-loopback), `AUREX_SERVICE_TOKEN` (at least 32 characters), `AUREX_OWNER_USER_ID` (Supabase owner UUID), `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`. Only the public Supabase URL/key may have VITE_ equivalents. Never prefix the AUREX token with VITE_. Existing Supabase middleware validates the session and every command checks the configured owner server-side before contacting AUREX. Public visitors see a locked form; no service health, jobs, prompts, results or evidence are publicly projected.

The backend also needs its execution flag, worker, database and native inference configured. CONNECTED means an authenticated backend health/capability exchange; it is not proof of successful model execution. A local-inference submission fixes maxCostUsd to zero. Repeating an unchanged failed submission reuses the idempotency key. Polling stops on terminal states; results remain advisory and NOT VERIFIED. Evidence integrity is separate from truth. Regression scans are not enabled.

## Current-source reconciliation blocker

Lovable source at `24a5328ec63309b4bb0fdb335a0967acbfdfe32d` has substantive /aurex changes absent from the GitHub import: compact demo hero, a public live-status query/loader and proposed red/blue/purple lab. The new command component is additive on the pinned GitHub source; do not replace the live Lovable route with this older route. Before any publication, recover the complete latest Lovable export, reconcile the shared adapter/schema changes, and insert AurexCommand without removing newer content. GitHub synchronization branch, published SHA and equivalence remain NOT VERIFIED.

## Deployment and rollback gate

Build the reconciled source at a pinned SHA in an owner-controlled preview with separate preview credentials. Test owner login, rejected non-owner, real durable job creation, native inference, cancellation and actual evidence display. Record backend/frontend SHAs and run IDs. Preserve the current deployment; do not switch DNS until these gates and explicit production approval. Rollback must restore a known previous frontend artifact/configuration; database rollback is a separate non-destructive compatibility decision. No deployment or DNS was changed by this work.

## Local verification (2026-10-15)

On the isolated XIX website worktree, Node v24.19.0 (CI targets Node 22):

- `npx tsc --noEmit`: PASS, no TypeScript errors.
- `npx vitest run`: PASS, 22 files / 149 tests, including mocked owner-denial, zero-budget prompt bounds, terminal expiry, advisory-only result/evidence and corrupt-result rejection.
- `npm run build`: PASS, existing Nitro target; bundler warns that inlineDynamicImports is ignored when codeSplitting is configured.
- `npm audit --omit=dev --audit-level=high`: PASS, registry returned zero vulnerabilities. This excludes development dependencies and is not a complete security assessment.

Authenticated browser-to-Qwen execution, live Supabase login, hosted deployment and CI execution: NOT RUN. Local runtime differs from the CI Node version, so a green local build does not assert a green CI run. Owner dashboard and frontend analytics ingestion are NOT IMPLEMENTED in this change. Existing product layouts and public demonstration content are preserved. Only an additive owner command section is introduced.
