# XAELI verification — CLXXXIII

Branch work/kusanagi-clxxxiv-inference-guard; PR150; CP001 edf081138bd73204b29d2337d08db079fb4494c4. Final formatting/docs checkpoint identified by containing commit. No backend behavior changed since CP001.

PASS: real local HTTP integration in website/src/lib/aurex-nvidia-loopback.test.ts. It starts canonical aurex.api on an OS-assigned loopback port with synthetic service credential, temporary SQLite path, clean environment, paid inference flags off. The server helper uses a test-only transport redirect from the asserted fixed staging URL to loopback. Production adapter allowlist is unchanged.
Authenticated GET returns DISABLED_BY_POLICY; unauthenticated GET/POST return 401; authenticated ask returns 403 REMOTE_INFERENCE_DISABLED. The owner helper ask sends zero HTTP requests. No provider called. Secrets absent from helper result. Status reporting works without enable/approval flags.
This verifies helper-to-real-backend HTTP, not browser rendering, deployed Railway, live NVIDIA, or independent review. The test creates no inference evidence receipt because denied execution is not successful evidence. Runtime OpenShell NOT VERIFIED.

Reproduce from website after installing Python project/dev and frontend dependencies:
```
AUREX_TEST_PYTHON=/absolute/path/to/venv/bin/python ./node_modules/.bin/vitest run
./node_modules/.bin/tsc --noEmit
npm run build
```
Without AUREX_TEST_PYTHON the opt-in HTTP test is SKIPPED, never PASS. Actual run here: 155 passed, 23 files. TypeScript PASS. Build PASS. Focused ESLint PASS on four modified frontend files. Bun itself NOT RUN (not installed); Vitest executable used.

Lovable revision d11d8a6a3e2f6b43860092988bb198271ffe8308 was inspected. Standard preview edit failed: workspace out of credits (INVALID_ARGUMENT). No edit/publish happened. Canonical server helper is a prepared sync candidate; canonical main lacks the newer Lovable RPC/UI so copying only the helper into GitHub does not wire the hosted UI.
Next authorized preview action: apply website/src/lib/aurex-nvidia-owner.server.ts to existing Lovable src/lib/aurex-nvidia-owner.server.ts, retain requireSupabaseAuth plus owner check in RPCs, update old tests that expect paid POST, render DISABLED_BY_POLICY/AUTHORIZATION_DENIED/STAGING_SECRETS_MISSING/BACKEND_UNAVAILABLE. Never set READY from flags. Do not publish. Restore credits through owner action if desired; do not purchase automatically.
