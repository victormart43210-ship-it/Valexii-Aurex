# AUREX public/private threat model (preview)

## Assets
Owner identity, AUREX service URL/token, budget, audit records, private research details.

## Boundaries
- **Public** `/aurex`: static registry (`toPublicCapabilities`, allowlisted fields), synthetic demo, public GitHub metadata, frosted placeholder cards built from synthetic text only. Never calls owner functions; live backend status is never used.
- **Private** `/admin/aurex-control` (client-only, noindex): every server function uses `requireSupabaseAuth`; every privileged handler calls `assertOwner` (rate limit 10/min per user per worker, owner UUID match against `AUREX_OWNER_USER_ID`, value-free audit log). Unset owner ⇒ deny.

## Threats and controls
| Threat | Control |
|---|---|
| CSS-blur leak | Blurred cards contain placeholder text only; no private data in DOM (tested). |
| Direct RPC bypass of UI | Server-side auth + owner check per handler (source-scan tests). |
| CSRF / cross-origin calls | TanStack CSRF middleware on server functions; bearer token required. |
| SSRF | Observe: fixed `https://valexii.com` paths, no redirects, 5s timeout. Service adapter: https, non-local hosts, fixed `/v1/health`. |
| Abuse / brute force | Per-user rate limit (best effort, per worker instance). |
| Request size | Privileged functions take no client input; public forms keep existing zod bounds. |
| Secret exposure | Secrets read only in server handlers; never returned; audit truncates actor id and strips values. |
| Self-approval | `approvalValid` requires distinct proposer/approver and owner approver; APPLY disabled in Phase 1. |
| Clickjacking / sniffing | CSP `frame-ancestors` (self + Lovable preview), `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`, nosniff, Referrer-Policy, Permissions-Policy. |
| Public writes | No public write endpoints added; existing forms are validated, rate-limited and service-role stored. |

## Known limits
- `script-src` not restricted: SSR hydration and JSON-LD rely on inline scripts. Nonce-based CSP is future work.
- Rate limiter is in-memory per worker; not a global guarantee.
- Audit logs go to server logs only; no durable audit store yet.
- Security testing is authorized, defensive self-testing of this site only.
