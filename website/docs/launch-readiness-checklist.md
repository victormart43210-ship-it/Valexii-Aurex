# Launch readiness checklist — preview audit, 13 Oct 2026

Statuses: PASS / FAIL / NOT VERIFIED / NOT APPLICABLE / BLOCKED. "Fixed" = changed in this pass. Nothing was published, deployed, or changed in DNS, billing, backend, auth or the owner console.

| # | Item | Status | Evidence / notes |
|---|------|--------|------------------|
| 1 | Privacy policy | PASS (owner/legal review required) | `/privacy` renders; describes stored inquiries, early-access double opt-in, off-by-default activation events, disabled newsletter, external Cash App link. Hosting-level analytics noted as separate. Not legally reviewed. |
| 2 | Terms | PASS (owner/legal review required) | `/terms` renders, developmental/no-warranty framing, no fabricated legal claims. Not legally reviewed. |
| 3 | Secrets off frontend | PASS | Only publishable backend key in client env (`VITE_*`). Secret names appear only in server functions/`*.server.ts` reading `process.env` inside handlers. No secret values printed. |
| 4 | HTTPS enforced | NOT VERIFIED (this pass) | Earlier session observed www → apex redirect over TLS; no hosting/DNS settings changed. Re-check after next publish. |
| 5 | Cookie consent | PASS / NOT APPLICABLE for banner | No third-party trackers or advertising cookies in source. Optional activation events are off by default with Allow / Decline controls in the footer and a persisted preference; no events are sent (no adapter). A full-screen banner is not needed for current behavior. Unused shadcn sidebar cookie is not rendered on public pages. Jurisdictional review by owner. |
| 6 | Unique titles/descriptions | PASS | Prior browser check: 23 public routes, 23 unique titles, descriptions + OG title/description present. |
| 7 | Social preview image | FIXED → PASS (homepage) | Added `public/og-valexii.jpg` (1200×630, ~247 KB, crop of existing comet artwork) and `og:image`/`twitter:image` on `/` only. Other routes fall back to hosting preview. Live only after next publish. |
| 8 | Favicon | PASS | `public/favicon.ico` 256×256 icon, linked in root head. Branding fit: owner confirm. |
| 9 | sitemap / robots | FIXED → PASS | Sitemap lists public apex URLs only. Added `Disallow: /admin/` for `User-agent: *`. Admin and confirm routes also carry `noindex`. robots.txt is not access control; admin is protected server-side. |
| 10 | Alt text | PASS | All `<img>` in routes carry descriptive `alt`; decorative SVG layers are `aria-hidden`. |
| 11 | Image optimization | PASS | No file in `src/assets`/`public` over 300 KB; large originals load via responsive srcset (960w mobile webp) and lazy loading below fold. |
| 12 | Page speed | NOT VERIFIED | No Lighthouse/field data run; no numbers claimed. Mitigations in place: hero preload, fixed image dimensions (CLS), static ambience on mobile/reduced-motion, lifecycle-paused animation. Owner: run PageSpeed Insights after publish. |
| 13 | Contrast | PASS | Prior pass: 110 rendered samples, minimum 9.70:1, motion on/off. |
| 14 | Mobile | PASS | Prior pass: 23 routes at 393 / 1280 px no overflow; homepage checked 320–430 px; min-height 44 px touch targets on primary controls. |
| 15 | 404 page | PASS | `RouteNotFound`: H1 "Page not found", noindex, "Go home" link; dev server returns HTTP 404 for unknown paths. |
| 16 | Internal links | PASS | Prior crawl: 28 internal paths/anchors, no broken links. |
| 17 | Form validation | PASS | Shared Zod schemas client-side (`inquiry-forms.tsx`) and server-side (`inquiries.functions.ts`); UI states whether email was actually sent. |
| 18 | Spam protection | PASS | Honeypot field, minimum fill time, server-side rate limits and dedupe; service-role-only storage. No captcha (none needed at current volume). |
| 19 | Analytics | PASS | No analytics script installed; consent-gated adapter shows "TELEMETRY NOT CONNECTED / NOT MEASURED". No metrics claimed. Hosting-level traffic stats are outside site code. |
| 20 | Primary homepage CTA | PASS | One `hero` variant button "Explore BCXMET" → `/bcxmet#command-center` (real route); others are secondary glass style. |

## Outstanding owner decisions
- Legal review of Privacy and Terms (1, 2, 5).
- Measure real page speed after publish (12) and re-confirm HTTPS (4).
- Publish to make items 7 and 9 live.
