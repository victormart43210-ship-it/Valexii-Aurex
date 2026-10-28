# CLII local industrial preview

From repository root, Python3.12+ and Node24:

```sh
python -m pip install -e '.[dev]'
(cd website && npm ci --ignore-scripts)
python scripts/clii_sandbox.py --ui-port 4173
```

Open http://127.0.0.1:4173. Run fictional towing, repeat, then select oilfield. Stop with Ctrl-C. This is a local React preview of the same IndustrialAudit component prepared for the existing owner workbench, not another hosted website. It calls the canonical `aurex.api:app` endpoint through a loopback Vite server-side proxy. Fresh random synthetic bearer stays server-side. Only explicit sandbox environment variables and PATH are passed; production credentials/model keys/proxies are not inherited. SQLite path points into a fresh temporary directory but this endpoint is stateless and makes no ledger writes. The launcher does not mount Railway volumes. This is process/credential isolation, not a hostile-code security container: it runs trusted checked-in source and is not a customer-upload execution environment.

API: `POST /v1/industrial/audit/demo`, bearer authentication, JSON exactly `{"fixture":"towing_v1"}` or `{"fixture":"oilfield_v1"}`, 128-byte streaming body limit, gate AUREX_ENABLE_INDUSTRIAL_DEMO=1 plus AUREX_DEPLOYMENT_SCOPE=sandbox or staging. Fixed as-of date2026-10-24; no historical changes/verified receipt claims. Existing canonical auth reused; single-owner service bearer is not multi-tenant isolation.

Website server RPC requires authenticated owner ID, exact Origin https://valexii.com, rate limit, and default-off AUREX_STAGING_INDUSTRIAL_ENABLED=1 with server-only AUREX_STAGING_SERVICE_URL/TOKEN. Destination fixed to existing staging host, redirects refused, 5-second timeout and16KB streamed response bound. Invalid/downstream authority-promoted responses become NOT_VERIFIED.

## Existing Lovable workbench mount (not published)

Read-only inspection of Lovable42731ae295377800fb81dd4cc8f1cadb21817750 confirmed src/routes/admin.sovereign-studio.tsx has owner-guarded Financial Audit tab and AurexAuditWorkbench. Canonical website mirror lacks that newer route: do NOT replace the route with an older file. Copy the new industrial component/contract/server-function files and add only:

```tsx
import { IndustrialAuditOwner } from '@/components/industrial-audit-owner';
// Inside existing tab === 'audit' fragment, after the existing workbench:
<AurexAuditWorkbench />
<IndustrialAuditOwner />
```

Preserve local oilfield workbench, artwork, authentication and other tabs. Origin allowlisting intentionally refuses arbitrary previews; approved preview origin must be separately configured/reviewed before a connected hosted preview. No live mount/publish performed. Lovable read access works; current credit balance not exposed by available connector, so no build credits requested.

## Evidence and rollback

Ledger integration NOT VERIFIED: existing job/receipt source on this baseline cannot yet persist industrial results safely. No new ledger/schema/receipt authority introduced. Stateless results are advisory only; repeatability is not durable persistence or independent certification. Continue through existing canonical worker/receipt integration as a separately tested change.

Rollback: stop both sandbox child processes with Ctrl-C; temporary data is removed. Revert the isolated source changes if needed. No production deployment, database migration or volume action occurred. Production HOLD, no payments or paid inference.
