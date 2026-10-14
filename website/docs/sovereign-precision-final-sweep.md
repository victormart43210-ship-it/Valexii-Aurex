# Sovereign Precision preview sweep — 10 October 2026

## Actual file changes

- `src/styles.css`: locked base #070F19, surface #0B1927, cyan #00D4E7,
  teal #008C9B, gold #C8A86B and foreground #F3F9FC shared semantic tokens;
  secondary/popover/accent derive from them. Distinct alert colors retained.
  Separate hero scrim now derives from base; 2px focus outlines, restrained
  CTA hover/tap feedback, cyan outline for Malware Shield, accessible tour styles.
- `src/components/orb-evidence-tour.tsx`: new three-step What changed? / Why? /
  Show proof tour, using shared Home fixtures and focus-managed Radix dialog.
  Back/Next/Done, Escape, focus restoration, simulation and authority labels.
  Consent-gated existing proof_view event only; no external service or new data.
- `src/components/visuals.tsx`: Home/XAELI phone Orbs open the new tour; displayed
  state and motion remain unchanged by the tour.
- `src/routes/__root.tsx`: browser theme color matches the locked base.
- `src/routes/index.tsx`: remove internal codename from public reverse-verification
  heading; reverse-verification explanation and evidence doctrine preserved.
- `AGENTS.md`, `roadmap.md`, project visual memory and this report: constraints
  and verification updated. No artwork or asset pointer replaced.

## Actual verification

- Home Chromium screenshots inspected at 320×852, 393×852, 768×1024,
  1440×1800. No horizontal overflow; four WCAG-tagged axe scans: zero violations.
- 18 content routes plus /reasoning redirect returned 200; all required rendered
  metadata present. Mobile image checks found no broken loaded images.
- All 18 content routes at 393px: zero WCAG-tagged axe violations; at 1440px:
  no horizontal overflow. Existing canonical host configuration not changed.
- Orb tour: all three steps, Done, keyboard Enter/Escape and focus restoration
  passed; dialog axe scan zero violations. Screenshot of proof step inspected.
- Both first-fold demo CTAs reached their correct existing section targets.
  Menu → BCXMET and browser Back passed; reduced-motion shimmer none,
  atmosphere offscreen state paused, no runtime page errors in full route pass.
- Two adjacent featured Command Center cards, both scenario starts, all three
  XAELI review actions, five categories, all phone tabs, quiz completion and all
  eight Orb states passed. Sequence advanced REST → AWARE; Pause passed.
- Test-only event adapter: zero before consent, one allowlisted name/page event
  after consent, no additional event after withdrawal. Adapter removed after test.
  Production telemetry remains NOT CONNECTED / NOT MEASURED.
- Phone tabs measured 58×63px at 393px. Exact editorial portrait loaded 709×1536
  outside phone; XAELI phone had zero image elements. No Floot resource requests.
- Hero image rendered 393×221 with contain, no blur or transform. Single local
  two-second unthrottled homepage observation: layout-shift sum 0.000313.
  This is not field CLS, audited performance or representative device evidence.
- Full ESLint: 0 errors / 9 existing react-refresh warnings. Latest automatic
  preview build/typecheck: build OK. Standalone production build not run.

## Limits and remaining blockers

Figma colors came from the user's exact specification; no active desktop-local
Figma session or claim of live integration. No Canva editing or MagicPath import.
No publishing, DNS, payment, backend, contact delivery or Android app changes.

Physical Samsung, comprehensive assistive technologies, cross-browser native
transition coverage and field Core Web Vitals remain untested. Independent
research/evaluation evidence and legal review remain outstanding. No measurement
provider is approved; activation/retention are not measured. No security efficacy
is established by this website.

Screenshots and scripts: `/tmp/browser/sovereign-sweep/` (temporary QA artifacts).