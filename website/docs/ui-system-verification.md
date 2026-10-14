# Site-wide frontend verification

## Scope and files

Changed `src/components/site.tsx`, `src/components/ui/button.tsx`, `src/components/ui/card.tsx`, `src/components/section-illustration.tsx`, `src/components/spectrum-radar.tsx`, `src/routes/__root.tsx`, `src/router.tsx`, `src/styles.css`, `vitest.config.ts`, `AGENTS.md`, `roadmap.md`.
Added `src/components/ui-system.tsx`, `src/components/route-states.tsx`, `src/components/ui-system.test.ts`, `docs/ui-system.md`, and this verification record.

Existing art, Orb animation, canonical phone fixtures, support destinations, mailto flows and public research qualifications are preserved. AUREX and its existing internal links remain present; no new product route was necessary.

## Verification

- 19 Vitest tests across four suites, including seven new shared-component rendering/state tests.
- Automatic preview build reports `build OK` after exact-optional-prop fixes; no manually invoked build/typecheck.
- Focused ESLint: zero errors, three fast-refresh export warnings in existing shared modules.
- 21 route visits at each of 1280/320/360/390/430px: HTTP 200, no horizontal page overflow or runtime errors. Unique content metadata verified; intentional `/reasoning` alias excluded from title uniqueness.
- 19 axe WCAG-tagged scans: no violations on selected public routes and expanded phone controls. This is not exhaustive accessibility certification.
- 120 phone tab/state combinations, content-sized Activity, viewport reset, touch swipe, pause and critical decay.
- Additional keyboard Home/End checks, visible button bounds at least 44px, no button text overflow at all four mobile widths; canonical scan hue and radio fixture records; phone internal scrolling and reduced-motion static screen.
- Missing-route recovery displayed and Go home returned to `/`. Loading/error component semantics tested via rendered markup; no intentionally injected production crash.
- Screenshot evidence under `/tmp/browser/ui-system/`: activity pages, compact drawers, native phone states and missing-route recovery. Inspected Activity at 320px, drawer at 320px and desktop Orb.

## Routes preserved

`/`, `/about`, `/aurex`, `/bcxmet`, `/build-with-us`, `/contact`, `/decipherment`, `/decipherment-frontier`, `/dispater`, `/ecosystem`, `/evaluation`, `/privacy`, `/reasoning`, `/research`, `/security`, `/support`, `/system`, `/terms`, `/voynich`, `/xaeli`, `/xaita`.

## Boundaries

No DNS, payment, backend, analytics provider or subscriber store changes. UNKNOWN ≠ SAFE; missing/stale ≠ PASS; no sole self-witness; ORB MOTION AUTHORITY = NONE. Physical Android hardware, battery/GPU profiling and exhaustive screen-reader/cross-browser certification remain unperformed; external Lovable badge remains unchanged. Existing research artifact and legal/provider approvals are separate blockers, not solved by frontend tests.