# CCLXX full-stack beta report

Code SHA `64dadbfd673186fbe65bc653a4658d866178ca8a`. Base `f381db7cd121d76f0df9f67a8a5e2547733fe33d` (pull request 192). `main` is `34cda4bd8f207f5b1284093b87e4760d782a4903`.

## Scores by scope

These are not a single product grade.

- DISPATER synthetic ledger: the golden test still expects identified 385.00, withheld 150.00, and confirmed 0.00. This change does not edit that engine. The restricted-beta path is still blocked by staging, independent review, and the unmerged stack. That scope is not 95 percent ready.
- XAELI live model: blocked. `http://127.0.0.1:8080/v1/models` returned URLError. The imaging laboratory does not call it.
- Manuscript forensics: tier 1 works on synthetic fixtures. Historical OCR, IIIF, RTI, photogrammetry, Hoku, and artwork instrument files are not integrated. This scope is a first laboratory, not 95 percent of the requested forensics product.
- VALEXII.AI as a whole: not 95 percent. The unfinished forensics tiers are not counted as done, and the DISPATER tests are not counted as the whole platform.

## What was verified

- `python3 -m pytest -q`: 781 passed, 1 skipped, in 7.91 seconds.
- `python3 -m ruff check .`: pass.
- `python3 -m mypy aurex`: pass, 119 files.
- Website `npx vitest run`: 169 passed.
- Website `npx tsc --noEmit`: pass.
- Website `npm run build`: pass. The forensics client chunk is 7.28 kB, gzip 2.97 kB.
- In-process faint-stroke examination averaged 0.0479 seconds over 10 calls.
- Mobile headless Chrome completed one synthetic examination. Confirmed recovery was not part of that page. The page said no recovered text.

## What was not verified

GitHub Actions on this SHA. Local Docker. A click of every layer. A human manuscript. Independent review. Staging. WCAG conformance.
