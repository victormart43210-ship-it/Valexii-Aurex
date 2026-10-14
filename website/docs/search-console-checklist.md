# Search Console setup, baseline and 30-day roadmap

## Production evidence (2026-10-13 01:06 UTC, from sandbox)
| Check | Result |
|---|---|
| https://valexii.com/ | PASS 200, text/html, IP 185.158.133.1, Cloudflare, HSTS |
| https://valexii.com/sitemap.xml | PASS 200 application/xml |
| https://valexii.com/robots.txt | PASS 200 text/plain |
| http://valexii.com/ | PASS 301 → https://valexii.com/ |
| https://valexii-ai.lovable.app/ | PASS 302 → https://valexii.com/ |
| TLS | PASS CN=valexii.com, Google Trust Services WE1, valid to 2027-01-09 |
| www.valexii.com | FAIL — does not resolve (A + _lovable TXT missing; DNS not changed) |
The reported external 502 was NOT reproduced. Possible causes: transient edge error, a checker hitting `www`, or a bot challenge (Cloudflare sets `__cf_bm`). Re-test from Search Console URL Inspection (live test).

## Setup steps (owner)
1. Search Console → add **URL-prefix** property `https://valexii.com/` (META tag verification; Domain property optional, needs DNS TXT).
2. Sitemaps → submit exactly `https://valexii.com/sitemap.xml` (22 URLs).
3. URL Inspection → live test `/`, `/bcxmet`, `/voynich`, `/rongorongo`, `/linear-a`; request indexing for those only.
4. Check Pages report weekly for "Crawled – not indexed", "Duplicate" (expect /reasoning → /system canonical).
5. Do not claim indexing until URL Inspection says "URL is on Google".

## Analytics cautions
- Do not add Google Analytics / tags without a consent banner that blocks them until opt-in; existing activation events stay default-off.
- Search Console needs no cookies and no consent.

## Baseline (Lovable hosting analytics, 2026-09-14 → 2026-10-13, all traffic incl. owner/tests)
- 62 visits, 190 pageviews, 58% bounce.
- Sources: Direct 35, google.com 22 (search channel 22 visits, 100% bounce, 1 page/visit), Google app 2, Gmail 1.
- Search landing pages: / 11, /support 3, /bcxmet 2, /dispater 2, others 1.
- Cannot separate owner/bot traffic; organic = "search" channel only.

## 30-day content roadmap (priority order, quality over volume)
1. Week 1: publish current changes; submit sitemap; record GSC baseline (impressions, queries).
2. Week 2: refine /bcxmet copy against actual GSC queries; add one evidence-backed explainer only if queries show demand (e.g., "how to check app permissions Android").
3. Week 3: Voynich — add a sourced "methods and null models" explainer section once internal artifacts can be linked.
4. Week 4: Rongorongo/Linear A — expand only with cited scholarship; first newsletter issue archive page once a real issue exists.
No pages without new evidence; no thin keyword variants.
