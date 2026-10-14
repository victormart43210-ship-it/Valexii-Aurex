# Mobile BCXMET repair and AUREX verification

## Repair
- Activity's fixed 365px screen created dead space; conflicting legacy minimum-height rules affected short screens. The first scan button also inherited a 44px-only width, causing icon/text overflow.
- One bounded `.phone-viewport` owns phone scrolling. Panels remain mounted, but viewport scroll resets on screen changes and deliberate demo triggers. Short screens use content height; site scrolling chains normally at boundaries.
- Radix accessible top tabs replace manual navigation. Explicit whitespace-free per-instance IDs prevent invalid ARIA references from the Command Center name. Redundant screen pagination removed; contextual evidence Back/Next still changes topics, not screens.
- Demo controls are in an initially collapsed outside drawer, with two-column wrapping buttons and >=44px heights. Phone footer stays in normal flow with safe-area spacing. Site header, browser chrome and platform badge were not altered.
- 220ms panel entrance; reduced-motion static fallback. Existing canonical fixtures, wheels, radar and semantic zoom preserved.

## AUREX
- `/aurex`: experimental evidence-first research and reasoning evaluation lab; reproducible questions, adversarial testing, limits and abstention.
- Internal links from navigation, /system, /evaluation and /research. No external official AUREX URL invented; no benchmark numbers or claimed manuscript solutions added.
- Independently verified results not established. Phone authority remains separate; no self-witness, UNKNOWN != SAFE, missing/stale != PASS, visualization authority NONE.

## Evidence
- 12 Vitest tests passed, including repeated view traversal immutability, unknown/authority boundaries, accessible phone structure and research claims.
- Playwright Chromium: 320/360/390/430 CSS px; five tabs x six modes = 120 combinations. Additional keyboard arrows/Home/End, scroll reset, boundary page scrolling, touch swipe, button bounds, pause and reduced-motion/critical decay checks passed.
- 21 routes (including alias), each at 1280/320/360/390/430: HTTP 200, metadata and no horizontal overflow/runtime page errors.
- 19 axe WCAG-tagged scans: zero violations (six pages at desktop/320/390 plus opened controls at 320).
- Focused lint: zero errors, two existing shared-export warnings. Automatic preview build OK.
- Screenshots under `/tmp/browser/mobile-repair/`; Activity before/after and desktop/mobile evidence inspected.

## Limits
Physical Android hardware/browser-chrome, native pinch behavior, battery/GPU profiling, exhaustive screen-reader and cross-browser certification not performed. Touch swipe was Chromium emulation; native pinch is not intercepted outside explicitly opted-in universe gestures. The external Lovable badge was not removed or reconfigured. Analytics-provider approval, research artifacts and legal review remain existing separate blockers; no DNS/payment/backend changes.

Publication explicitly authorized after QA; verify release separately at https://valexii.com/bcxmet and https://valexii.com/aurex.
