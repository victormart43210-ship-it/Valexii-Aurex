# Public legal and claims review

10 October 2026 · implementation review, not legal advice or lawyer approval.

## Checklist

| Area | Status | Review / remaining action |
| --- | --- | --- |
| Voluntary contributions | PASS | Existing Cash App recipient retained; suggested $50 founding contribution, any amount welcome, not a purchase price; explicit "not investment, equity, purchase, subscription or pre-order" disclosure. No receipt confirmation by site. 11 Oct 2026: founding-support messaging replaced per approved copy; three access formats (APK planned, QR planned, USB by request) all gated on verification; homepage band reconciled. Counsel review still advised for donation/payment characterization, tax, consumer law, refunds, privacy and security-software distribution. |
| USB archive | PASS | Optional public-material request only; availability/fulfillment confirmation required, no delivery entitlement or Android protection device. |
| Annual access | PASS | Future optional vision only, subject to finalized terms; support includes no license, 12 months, subscription or access. |
| APK / QR | NOT VERIFIED | None offered. Signed artifact, published SHA-256, release notes, compatibility/risk disclosures and independent physical-device testing required. No release date promised. |
| Android capabilities | NOT VERIFIED | This repository is a web demonstration, not an Android manifest/build/release. Call/app/network/privacy capabilities remain roadmap; simulation labels retained. Removed unsubstantiated active-beta release implication from BCXMET metadata/copy. |
| Call screening / distribution | PASS | Official Android supports user-selected call screening and website distribution with opt-in. Neither distribution path bypasses OS sandbox, permissions or lawful obligations. |
| Play compliance / separate builds | NEEDS COUNSEL | Review actual build, store rules, lawful distribution, user data and deceptive behavior policies before release. No certification asserted. |
| Communications | PASS | Email drafts only, explicit weekly opt-in request and confirmation, withdrawal by email; no automated sending/capture. |
| Privacy / hosting | NEEDS COUNSEL | Default-off coarse website adapter has no provider; hosting analytics and rights-request/retention practices need review. Draft notice clarifies voluntarily sent email. |
| Terms / IP | NEEDS COUNSEL | Draft only. No lawyer approval, patent registration, exclusivity or infringement conclusion asserted. Legal text no longer calls the existing website unpublished. |
| Evidence / efficacy | NOT VERIFIED | No live protection, neutralization or measured detection promise. Unknown ≠ Safe; stale/missing evidence ≠ PASS. Mock numerical snapshots stay explicitly internal/evidence-required, not official HLE. Research artifact attachment and independent replication outstanding. |
| Marketing | PASS | Value-before-ask call demo, factual FAQ, transparent limitations, plain action links; no testimonials, invented customers, coercion or scarcity. No affiliation with Red Hat claimed. |
| Metadata | PASS | All 18 content pages inspected, unique authored titles/descriptions and social tags. Self-referencing canonical/og:url use the user-specified https://valexii-ai.lovable.app; /reasoning remains an alias. No invented share artwork. |

PASS means the website wording/implementation met this limited review, not that
law, security efficacy or a release has been independently verified. Counsel must
review contribution/fulfillment, consumer disclosures, privacy, IP and future
commercial terms for applicable jurisdictions before product activation.

## Official sources checked

- https://developer.android.com/reference/android/telecom/CallScreeningService
- https://developer.android.com/develop/connectivity/telecom/dialer-app/screen-calls
- https://developer.android.com/distribute/marketing-tools/alternative-distribution
- https://support.google.com/googleplay/android-developer/answer/16559646
- https://support.google.com/googleplay/android-developer/answer/9888077
- https://support.google.com/googleplay/android-developer/answer/10144311

These are platform requirements, not evidence of BCXMET release/compliance.
Play-distributed apps cannot use external executable updates to evade Play's
mechanism; website distribution must not be described as a permission bypass.

## Release boundary

Preview changes only; no republish, DNS/payment destination changes, backend,
subscription, APK or scannable QR creation. No live Figma/Canva/MagicPath asset
editing claimed. Existing exact artwork and editorial-only portrait preserved.

## Preview verification

Support screenshots inspected at 393px and 1280px; timeline stacks / separates
without overflow. FAQ five answers open and match five JSON-LD entries; Cash App
destination and archive mailto confirmed; call-demo CTA reaches
`/bcxmet#command-center`, browser Back returns to Support; no APK/download links.

All 18 content pages plus /reasoning alias loaded with valid authored metadata,
exactly one canonical, no broken loaded images or horizontal overflow at 393px.
WCAG 2/2.1/2.2 AA-tagged axe scans: zero violations on all pages and desktop
Support. Runtime page errors: zero. Automated checks are not legal approval or a
comprehensive assistive-technology audit. Physical Android testing not performed.

Full ESLint: 0 errors, 10 warnings (9 existing export warnings, 1 shared FAQ export
warning). Automatic preview build/typecheck diagnostics recovered and latest
entry at 19:49:12 UTC reports build OK; standalone production build/typecheck
not run. No unit-test script is configured. All eight Orb states verified,
tail visible only in DEFEND; filament motion pauses offscreen and is absent
under reduced motion. Final 393×852 Support and DEFEND screenshots inspected.

Actual changed files: all 18 content `src/routes/*.tsx` (canonical/og:url
alignment; Support, BCXMET, About, Contact, Build With Us, Privacy and Terms also
have the described copy changes); `src/components/support-roadmap.tsx` (new),
`src/components/presentation-orb.tsx`, `src/components/orb-laboratory.tsx`,
`src/styles.css`, `AGENTS.md`, `roadmap.md` and this checklist. Project visual
memory records the user's contribution/release boundaries. Original artwork
and asset pointers unchanged. Temporary QA screenshots/scripts are under
`/tmp/browser/support-review/`.

Metadata changes reach the live URL only on the next user-approved publish.
Server SEO scanners currently report NOT SCANNED; no findings were marked fixed.
Share image tags remain omitted where existing artwork URLs are relative asset
pointers: no unsized original or unrelated image is advertised as a share asset.