# SEO audit — Oct 13 2026 (preview only, not published)

Domain verified: https://valexii.com is the active primary custom domain (www drifted; not used).

| Check | Before | After |
|---|---|---|
| Server-rendered HTML (TanStack Start SSR) — crawlable without JS | PASS | PASS |
| Unique title/description per route (20 routes) | PASS (/reasoning intentionally canonicalizes to /system) | PASS |
| Descriptions ≤ ~160 chars | FAIL (system 196, support 186, aurex 180, contact 166) | PASS (≤162) |
| Self-referencing canonical + og:url on valexii.com | PASS | PASS |
| One h1 per page; all images have alt | PASS | PASS |
| Organization + WebSite JSON-LD | FAIL (none) | PASS (root, factual fields only) |
| 404 returns 404 + noindex | PARTIAL (404, no noindex) | PASS |
| sitemap.xml / robots.txt on valexii.com | PASS | PASS (unchanged) |
| SoftwareApplication JSON-LD | — | Intentionally omitted: BCXMET not released |
| og:image per route | — | Omitted: host supplies preview; no sized absolute images |
| Core Web Vitals on production | NOT VERIFIED (requires published field data) |
| Google indexing / Search Console | NOT VERIFIED (not connected) |

Files: src/routes/__root.tsx, src/components/route-states.tsx, src/routes/{system,aurex,support,contact}.tsx, src/components/domain-directions.test.ts (stale assertion updated for approved hero art).
Live site changes only after an approved publish.

## Phase 2 — topic content (Oct 13 2026, preview only)
- New SSR routes: /linear-a, /rongorongo (own title, description, canonical, og:url; in sitemap; linked from /decipherment, /research, /voynich).
- Visible FAQ + external sources added to /bcxmet (Android phishing & permissions; states demos are simulated, no protection claim) and /voynich (Beinecke MS 408 link; not deciphered).
- Shared: src/components/topic-guide.tsx, topic-guide-content.ts. No FAQPage JSON-LD added (visible content only).
- Source URLs checked returning 200 at build time; Wikipedia used only as labelled overview.
- PASS: 200 status, single h1, self canonical, sitemap 22 URLs, 33 tests, build OK. NOT VERIFIED: indexing/ranking (requires publish + Search Console).

## Phase 3 — quality pass (Oct 13 2026, preview only)
- Playwright 360px sweep of 22 routes + 404: 0 horizontal overflow, 1 <main> each, 0 images missing alt, 0 broken images, 0 heading skips, 0 page errors.
- Fixed: home sr-only h2 (h1→h3 skip); /about and /security titles/descriptions; /bcxmet decorative backdrop now alt="" with width/height.
- Added BreadcrumbList JSON-LD (Home › Research › topic) on /voynich, /rongorongo, /linear-a.
- Open: "ROTAS / Reverse review" heading on home awaits owner decision; Core Web Vitals and indexing NOT VERIFIED.
