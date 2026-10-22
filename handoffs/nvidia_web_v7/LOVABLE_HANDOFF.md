# KUSANAGI XXVI: Lovable 1-change handoff — NVIDIA owner-only staging UI

## Precise current architecture (verified 2026-10-22)
- Lovable workspace project: `Valexii Ai`, project ID `811ffc43-2c8b-4c88-ab4c-4de668d089cb`.
- Existing protected route: `src/routes/admin.sovereign-studio.tsx`, tab `Models / NVIDIA`, existing owner check `checkAurexOwner` and Supabase auth middleware.
- Existing server-owner pattern: `src/lib/aurex-control.functions.ts` uses `requireSupabaseAuth`, `isOwner`, and `createRateLimiter`.
- Existing Railway staging URL is `https://aurex-api-aurex-staging.up.railway.app` with strict bearer authentication.
- Existing staging backend Python `/v1/agent/status` and guarded `/v1/agent/ask` exist and currently have **NVIDIA disabled**.
- Existing website NVIDIA pages are research/descriptive, not live inference.

## What to implement in Lovable using bundled source files
1. Add `src/lib/aurex-nvidia-owner.functions.ts` from this ZIP, inspect/adjust imports to match current TanStack Start project version.
2. Add `src/components/aurex-nvidia-owner-console.tsx` from this ZIP.
3. Import the console **only** in the existing `/admin/sovereign-studio` `Models / NVIDIA` tab, below the parent `checkAurexOwner` permission gate. Do not add it to the public `/aurex/ox` route.
4. Ensure code is server-only: `AUREX_STAGING_SERVICE_TOKEN` and future NVIDIA secrets must never enter browser JS, HTML, logs or errors. No direct browser-to-Railway or browser-to-NVIDIA calls.
5. Build and run tests. Verify unauthenticated and ordinary-user requests are denied even by direct server function invocation. Verify flags absent or `false` block POST; mock provider errors and response-size limits.
6. Do NOT set new feature flags to true; do NOT set provider credentials, deploy to public site, or use paid model calls in this operation.
7. The site may continue to publish clearly labeled *research only* NVIDIA sections. Avoid false `DEMO LIVE` labels until a real owner-approved provider call works.

## Required deliberate activation gates (all initially OFF)
**Website secrets (server-side):**
- `AUREX_STAGING_SERVICE_URL` (the pinned HTTPS Railway staging URL with trailing slash).
- `AUREX_STAGING_SERVICE_TOKEN` (existing bearer token; never paste into chat or public code).
- `AUREX_OWNER_USER_ID` (existing Supabase owner identity).
- `AUREX_NVIDIA_SITE_ENABLED=false` (new).
- `AUREX_NVIDIA_OPERATOR_TEST_APPROVED=false` (new separate manual gate).

**Railway staging secret/configuration (future authorization only):**
- `AUREX_LLM_PROVIDER=nvidia`.
- `AUREX_NVIDIA_MODEL=<actual supported NVIDIA build model ID>` (validate at activation time).
- `AUREX_NVIDIA_API_KEY=<secret obtained by owner>`.
- `AUREX_LLM_ENABLED=false`, `AUREX_LLM_ALLOW_BILLING=false` until explicit approval.

**No production changes**, no public chat, and no text egress until the owner authorizes a bounded paid or free-quota model call. Backend `reserve_llm_call` limits 4/minute and 20/day **but is not a dollar billing cap**. Provider-side spend limits and a measured test budget are separately required.

## Audit and correctness requirements
- Repeat tests with fixture-only prompts and synthetic evidence. Treat model output as `UNVERIFIED_NVIDIA_NARRATIVE`; `authority=NONE`, `release=HOLD`.
- Inspect provider response, NVIDIA API errors and request status without logging tokens.
- Do not imply affiliation with NVIDIA or University of Helsinki; both are publicly documented technology/learning references.
- No self-witness; one response is not proof of efficacy or production readiness.
