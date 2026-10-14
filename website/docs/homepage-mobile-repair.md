# Homepage mobile repair — 10 October 2026

## Cause and repair

At 393px the 960×540 landscape source covered a 393×1180 content stack.
Cover therefore rendered its width at approximately 2098px, cropping most of
the composition and enlarging the source above its intended pixel density.
There was no image blur filter or image transform.

The original artwork and asset pointers are unchanged. An independent 16:9
image layer uses contain, responsive 960w/1536w sources and a matching preload.
At 393px its rendered box is 393×221; all of the comet/city composition remains
visible. The gradient is a separate overlay. Mobile copy follows the artwork,
and the phone begins at approximately y=610 on a quiet dark field, visible within
the 852px first viewport. Desktop uses the original landscape without stretch.

## Editable motion and navigation

Native SVG filament dash motion and a restrained 8px/5px particle drift use
the shared visibility/reduced-motion lifecycle hook. The image itself never
scales, blurs or moves. No new rendering dependency or external editing service.

TanStack native view transitions animate content over 330ms with a .96–1 scale,
0–1px blur and a central luminous transition-only symbol. Links are never
intercepted; snapshots do not receive pointer events. Reduced motion disables
the native transition setting. Unsupported browsers keep normal navigation.
No visual supplies security authority.

## Actual checks

- Playwright Chromium at 320×852, 393×852 and 1280×1800: images loaded,
  no horizontal overflow and no runtime page errors.
- 393px menu navigation to BCXMET and browser Back passed.
- XAELI navigation completed with transition symbol opacity returning to zero.
- Phone XAELI remained Orb-only (zero image elements).
- Atmosphere active onscreen, paused at footer; reduced-motion animation none.
- Axe WCAG-tagged scans at 393px and desktop: zero violations.
- Focused ESLint passed; latest automatic preview build/typecheck: build OK.
- Screenshots inspected: `/tmp/browser/hero-repair/after-393.png` and
  `/tmp/browser/hero-repair/after-1280.png`.

Not performed: physical Samsung testing, production-target build, exhaustive
assistive-technology testing or external Canva/MagicPath editing. Nothing
published; no domain, payment, backend or security functionality changed.