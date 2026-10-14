# BCXMET activation refinement — 10 October 2026

## Baseline, not a retention result
User-supplied Lovable dashboard snapshot, Oct 1–10: 25 visitors; 41 pageviews;
1.64 pageviews/visit; reported bounce rate 97%; session-duration total 37 (unit unknown).
Device figures: desktop 19, mobile 5, one potentially unclassified. Homepage 15
visit/page records versus BCXMET 2; record definitions are not independently confirmed.
Small sample, uncertain definitions and no controlled comparison: no established
retention improvement, preferences, efficacy or statistical significance.
This change targets activation; post-change results are NOT MEASURED.

## Official research context
- Google, **What's new in Android security and privacy in 2025**, May 13 2025:
  https://blog.google/security/whats-new-in-android-security-privacy-2025/
  In-call scam protections, app behavior, Play Protect and privacy context.
- Google, **New AI-powered scam detection features to help protect you on Android**, March 4 2025:
  https://blog.google/security/new-ai-powered-scam-detection-features/
  Social-engineering calls and messages. Device, region and rollout limitations matter.
- Google, **Android expands pilot for in-call scam protection for financial apps**, December 3 2025:
  https://blog.google/security/android-expands-pilot-in-call-scam-protection-financial-apps/
  Banking impersonation and risky in-call behavior; pilot is not universal availability.
- FTC data visualizations (user-provided starting point):
  https://www.ftc.gov/news-events/data-visualizations
  FTC Explore Data: https://www.ftc.gov/news-events/explore-data
  Unwanted call complaints: https://www.ftc.gov/reports/national-do-not-call-registry-data-book-fiscal-year-2025
  Consumer-report data is not a verified incident census or a BCXMET benchmark.

No specific 2026 Google release was independently confirmed during this refinement.
Do not manufacture a 2026 source or assert BCXMET exceeds Google's protections.

## What actually functions here
Website tabs, call/app fixture review, permission explanations, authored XAELI
proof text and decorative Orb presentation. Android call screening, malware detection,
blocking, scanning and efficacy are UNDER DEVELOPMENT / NOT VERIFIED.
No real phone numbers, inventories, messages, current counters or threat feeds.
Routine call preview has a subtle pulse. Comet assumes hypothetical qualified evidence,
not actual detection. Unknown ≠ Safe; missing/stale ≠ PASS; no self-witness;
Evidence → Qualification → Reality → Authority → Effect; motion authority NONE.

## Measurement boundary
`activation-events.ts` exposes an allowlisted, default-off browser adapter. No endpoint,
server, provider or analytics service is configured; events are not sent or buffered.
Explicit consent can be withdrawn. Only consent preference is stored by default;
with consent, a yes/no seen marker plus session flag supports return-session semantics
without visitor IDs. No numeric retention claim can be derived from this implementation.
Event names: hero_spam_click, hero_malware_click, demo_start, spam_card_open,
malware_card_open, xaeli_proof_click, opt_in_request, scroll_depth, page_exit,
return_session. Coarse page category and 25/50/75/100% scroll buckets only; no PII,
raw URLs, timestamps, user-agent or device-security information. Email click means a
requested draft, not subscription capture. Route departure/pagehide are signals,
not reliably delivered exit telemetry. Existing hosting dashboard is a separate service;
these hooks neither configure nor attest its consent compliance.

Before measuring: approve a provider/adapter and retention policy, review consent/legal
requirements and delivery, verify event deduplication and metric definitions, collect a
larger sample and predefine an activation outcome. No publication authorized.
