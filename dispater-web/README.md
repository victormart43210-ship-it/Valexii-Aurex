# DISPATER.AI — Isolated Vercel Preview

This is a **separate static website** hosted by Vercel from the **same canonical GitHub repository** (`victormart43210-ship-it/Valexii-Aurex`), with Vercel Root Directory `dispater-web`.

## Status and boundaries

- Public site / buttons / visual: a proposed business product.
- **Interactive synthetic preview**: deterministic JavaScript reconciling fictional towing and oilfield jobs, example rates, invoices, payments and illustrative IRS/DOT document-index gaps.
- **AUREX production or staging backend: NOT CONNECTED.** This is not the PR #123 Python AUREX runtime; do not imply it is.
- **NVIDIA inference: NOT RUN.** Text is authored/deterministic.
- **No user accounts, uploads, financial actions, payroll, dispatch, legal opinions, tax advice, regulatory assessments, or certified compliance.**
- Source references in demo reports point only to fictional local fixture identifiers; they are not immutable proof or independent witnesses.
- Roman hero art is referenced from the owner's existing public VALEXII.COM artwork route. Do not remove that original asset from the parent website.
- `valexii.com` must retain current DNS/hosting; never attach that production apex domain to this preview.

## Commands

```bash
cd dispater-web
npm test
npm run build
```

Build produces `dist/` without network dependencies, and Vercel should set **Root Directory** `dispater-web`, **Build Command** `npm run build`, **Output Directory** `dist`.

Do not merge until a reviewed exact-head build and browser smoke test are documented. Verify that the Roman artwork loads, buttons function, preview copy is accurate and reports cannot grant authority.

## Proposed deployment and commercial progression

1. Keep the app on a `.vercel.app` preview URL with project deployment protection as appropriate.
2. Independently verify website rendering, tests, and origin/source SHA.
3. Optionally choose and register `dispater.app` or use free `dispater.valexii.com`; **domain purchase and DNS changes are separate, owner-approved actions.**
4. Add authorized links from `valexii.com/dispater` after testing without disrupting homepage artwork.
5. Connect **segregated synthetic-only** Railway AUREX backend through reviewed server-to-server adapter, not public unauthenticated endpoints.
6. Never permit real customer uploads until isolated identity, tenancy, consent, encryption, regulatory rule applicability, and independent security review pass.

A premium `.ai` domain is not required. Avoid additional Vercel team seats or uncontrolled usage; set spending alerts.
