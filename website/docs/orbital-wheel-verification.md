# Orbital instrument enhancement — 11 October 2026

## Scope and authority
- Enhances the existing Orb and phone, not a replacement of artwork, research, newsletter or routes.
- Instrument ticks, concentric arcs and the scan readout share `getDemoTelemetry` in the authored phone fixture module. Both use one demo-phase state: idle → review → returning → complete; 0/40/80/100 are storyboard progress, not measured scan coverage.
- Call evidence references the same authored Command Center fixture; permission evidence references the same Home fixture. The readout includes the corresponding screen-card summary.
- Current status always UNKNOWN / NOT VERIFIED; last-check age unknown, freshness unverified, historical CLEAR not established. Completing the storyboard is HOLD, never clearance, fresh evidence or a protection result.
- No device data, backend, analytics change, authority return path, DNS or payment changes. ORB MOTION AUTHORITY = NONE.

## Presentation safeguards
- Concentric cyan/gold wheels rotate at 150/180-second periods; idle axial flow slowed to 160 seconds.
- Deliberate critical demo: bounded 4.2-second slingshot approach, layered ribbons, six vortex wisps, twelve delayed particles and fluid shear. RETURN dissipates the wake in 2.2 seconds; total demo returns to REST in 6.5 seconds. Routine remains restrained and completes in 2.7 seconds.
- CSS/SVG only, no frame loop, physics claim or WebGL. Coarse-pointer/mobile views disable the inner rotating wheel and animated wisps, display at most six delayed particles, and remove idle meridian motion.
- Existing visibility/document lifecycle suspension and play/pause apply to all rings and subject motion. Reduced motion keeps meaningful text/progress and static SVG. No flashing animation.
- Manual state changes cancel pending demo timers; component teardown clears timers. Existing hidden phone panels preserve scrolling.

## Observed preview evidence
- Three Vitest unit tests passed: no status/freshness/authority promotion; same fixture references; synchronized phases/progress/Orb state.
- Focused ESLint passed; automatic preview build/typecheck: build OK.
- Browser E2E: twenty existing routes at 1280/393px and four relevant routes at 360/412px, no horizontal overflow or page errors; canonical/social metadata retained and section artwork decoded.
- Six axe WCAG-tagged scans (Home, BCXMET, Frontier at 1280/393px) returned zero violations. Automated checks are not a comprehensive WCAG certification.
- E2E verified routine/critical progression, approach transform changes, RETURN wake decay, wheel pause/resume, manual-state timer cancellation, tour dialog, all five tabs, phone scroll restoration, offscreen suspension and static reduced motion.
- Screenshot evidence inspected: idle mobile, critical approach mobile, critical desktop, reduced-motion mobile. Evidence scripts/logs/screenshots are under `/tmp/browser/orbital-wheel/`.
- Physical Android battery/GPU profiling and complete cross-browser/assistive-technology testing remain unperformed; safeguards are implementation evidence, not measured battery/performance claims.

## Release
Publication explicitly authorized through the supported website publication flow; confirm live instrument markup and interaction separately from source SHA. No existing research, legal, measurement or newsletter evidence gate is promoted to PASS.