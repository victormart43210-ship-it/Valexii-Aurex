# Exact homepage artwork — 10 October 2026

## Status: EXACT ORIGINALS INSTALLED / HERO REPLACED

Both supplied public URLs resolved and their downloaded originals match the supplied
dimensions and byte counts: hero JPEG 1536×864 / 744703 bytes; portrait JPEG
709×1536 / 362454 bytes. No generated or stock substitute was used.
Homepage HomeHeroArt now imports the exact hero, not the previous lighter background.

## Prepared integration

Project asset pointers are stored in `public/assets/`:
- `bcxmet-celestial-comet-home.jpg.asset.json`
- `bcxmet-celestial-comet-home-mobile.webp.asset.json`
- `xaeli-editorial-portrait.jpg.asset.json`

Raw downloads were staged under /tmp and externalized through Lovable Assets,
as required for downloaded app media. The original bytes are served independently
of Floot via project asset URLs; no permanent Floot image requests or duplicate raw
repository binaries are required. Source SHA-256:
- Hero: `e6400f8c633b803219c7d500c86ed8d7ec605538571f727f45cb074a6d8de7e2`
- Portrait: `e5119d21b1c189372092fadaf56af4bad467ab6f588a94e1dc225cb1384737ba`

The mobile derivative is a 960×540 WebP / 175724 bytes, resized from the exact
original without removing its landscape content. Responsive picture selection uses
it below 640px. A semantic dark scrim and separate focal positions preserve contrast.

The exact portrait is exclusively for the external XAELI editorial section, labeled artistic
personification—not app UI. Every phone retains the abstract Orb.

## Guided experience

Both flagship previews remain ungated. Each can open a native editable evidence
tour: six desktop steps, five grouped mobile steps, Back/Next/Restart, source,
permissions, status, qualification and next-review content from shared fixtures.
All content is simulated, not scanning/blocking. No telemetry provider, retention
measurement, publication or domain change is added.