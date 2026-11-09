# One Intelligence integration report

Status **PARTIAL**. A local browser exercised the existing website and backend with a synthetic PDF. The historical image passed offline measurement and OCR ran as a separate probe. Shared durable custody, qualification and a hosted research UI remain open.

- Existing DISPATER upload endpoint and receipt store reused. Duplicate PDF fields are rejected, malformed Base64 produces a client error, and the browser checks the fixed PDF's digest and page before display.
- Selected offline imaging code recovered from #193 onto current main. Optional Pillow supports PNG/JPEG admission, bounded transformations and pixel-region reports. The historical branch remains open.
- Code lanes were integrated serially. This branch does not activate #212's treasury, the Forge stack, or Qwen observability changes.
- Local test counts and exact-commit CI and review are recorded in the integration PR. Revert the candidate commit if a future owner-approved integration needs rollback. No migrations or deployment are part of this change.

Next gated slice is an isolated OCR worker that binds results to source and page and shows uncertainty. For manuscript work, freeze a reproducible annotation and independent control contract before adding interpretation or IIIF network access.
