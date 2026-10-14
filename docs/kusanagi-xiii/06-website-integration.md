# Website investigation and patch

Lovable source: TanStack Start server functions, React 19, Vite, Supabase auth and integrations; package name tanstack_start_ts. Public /aurex uses labeled static synthetic data; owner console supplies diagnostics. No Ask AUREX production flow or real response pipeline is implemented.

The pinned source has two clients with incompatible expectations. The prepared patch changes only `src/lib/aurex-client.server.ts` and `src/lib/aurex-service.server.ts`: unify health/capability validation, require >=32-character service tokens, cancel oversized chunked responses while reading, and dispose of rejected response bodies. No UI, artwork, headline, navigation, research or analytics changes.

The patch is separately delivered to the owner, not committed into this public backend repository. It targets Lovable revision 8353b5e9ac32e6c5d983151acfabd02f29e46bd8. GitHub synchronization target is unknown; applying it to Valexii-nexus would modify the wrong repository. Website build/full tests are NOT RUN; focused patch tests are 3 PASS with mocked HTTP transport and real schema/adapter functions.

Remaining website gates: DNS-aware egress/SSRF controls (current URL checks are lexical), exact upstream allowlisting, authenticated owner/non-owner tests, response-timeout/outage tests, secret-bundle inspection, full build, mobile/a11y checks and correct sync/deployment mapping. Do not mark CONNECTED from the synthetic demo, repo existence, CI, or health alone when native inference is required.
