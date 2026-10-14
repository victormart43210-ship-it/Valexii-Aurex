# Weekly Research Dispatch — integration checklist

Status: **NOT ACTIVE.** The form renders disabled ("Signup not yet active") until all server env vars below are set. No address is collected, stored locally, or sent anywhere while inactive.

## Functional now (no secrets)
- `NewsletterSignup` (src/components/newsletter-signup.tsx): footer on every page, plus /decipherment-frontier. Email, explicit consent checkbox, privacy link, unsubscribe note, honeypot, accessible status region.
- Server proxy (src/lib/newsletter.functions.ts): `getNewsletterStatus`, `subscribeNewsletter` → listmonk `POST /api/public/subscription`. Zod validation, honeypot, min-fill-time, best-effort per-isolate rate limit. Success copy says "confirm by email", never "subscribed".

## Server env vars (Project Settings → Secrets / host env)
| Var | Purpose |
|---|---|
| `LISTMONK_URL` | https base URL of self-hosted listmonk |
| `LISTMONK_LIST_UUID` | public list UUID (list type Public, opt-in **Double**) |
| `NEWSLETTER_SIGNUP_ENABLED` | must be `true` to open the form |
No API token is needed for the public endpoint; never put credentials in `VITE_*`.

## Blocked by external accounts (owner action)
1. Host listmonk (Docker + Postgres, e.g. VPS/Coolify). Enable public subscription + CAPTCHA/rate limit at the reverse proxy.
2. Create list: Public, Double opt-in; customize confirmation template.
3. SMTP: Resend (optional) as listmonk SMTP relay; verify a sending subdomain (e.g. `news.valexii.com`) with SPF, DKIM, DMARC (`p=none` → tighten). Do not touch apex MX / Namecheap forwarding to Gmail.
4. Reply-To: `developer@valexii.com`. From: address on the verified sending domain.
5. Update /privacy with provider, purpose, retention, confirmation, unsubscribe before enabling.
6. Set env vars, test on preview, then publish only with approval.

## Editorial workflow (monthly bank of 4 drafts)
Statuses: `DRAFT → REVIEWED → APPROVED → SCHEDULED → SENT`.
- AI may prepare DRAFTs only. A human moves to REVIEWED and APPROVED.
- Only APPROVED campaigns may be scheduled in listmonk (weekly slot). Nothing auto-schedules.
- Freshness check before send: re-verify every claim/link; anything stale returns to DRAFT.
- No fabricated or pre-announced future findings; label FINDING / HYPOTHESIS / OPEN QUESTION / HOLD / CORRECTION.
- Unsubscribe link (listmonk `{{ UnsubscribeURL }}`) and List-Unsubscribe header in every email; bounces/complaints → blocklist (suppression) via listmonk bounce processing.
