# Document processing end-to-end verification

**Local PDF browser flow passed. Hosted candidate and OCR route remain unverified.**

The fixture `website/src/lib/dispater-invoice-fixture.json` contains a generated one-page PDF with invoice `I-PDF-DEMO`, job `MISSING`, amount `10.00` and status `open`. SHA-256 `c1fdbd390764b0c06a0fd8a7460f7fc998cda7adfe355dca89017dee73eeeef0`.

1. Run the existing FastAPI app with Uvicorn on loopback and Vite in development mode on a second loopback port. Use a temporary SQLite database, randomly generated service token, tenant grant and receipt/anchor keys. Keep them server-side.
2. Open `/dispater` and select **Process synthetic invoice PDF**. The real browser called the website server function, which posted the PDF to `/v1/dispater/documents`. The backend extracted page-one fields, reconciled the invoice and read back the persisted report.
3. Chromium 153 driven by Playwright showed the synthetic document label, filename, digest prefix and page 1 at desktop width 1280 and mobile width 390 with no horizontal overflow. The orphan invoice yielded **$10.00 unverified exposure and $0.00 confirmed recovery**. This fixture does not establish an independently confirmed rate mismatch.

Direct API tests cover cross-tenant denial, malformed Base64, duplicate PDF fields and page provenance. Existing CSV and golden-ledger paths remain in the regression suite.

## Scanned document

Tesseract 5.3.4 ran locally on a generated 1200×350 PNG with the known text `SYNTHETIC INVOICE / Invoice ID: I-OCR-001 / Amount: 10.00`. The command was `tesseract synthetic-scan.png stdout --psm 6 tsv`. It returned text boxes, `10.00` with confidence 96.53 and the incorrect ID `|-OCR-001` with confidence 58.66. The scan is an offline capability probe. The deployed ingestion contract still rejects PNG/JPEG and image-only PDF for financial interpretation. An OCR worker with resource limits, a review threshold and original-versus-extracted UI remains open.
