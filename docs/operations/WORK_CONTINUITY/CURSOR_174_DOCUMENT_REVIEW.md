# Cursor #174 document parser review

**Disposition — HOLD financial use of the document endpoint.** On candidate `2d0b62400e0ad40f2780f51b26ba0d09261cd724`, two contradictory amounts in a single source produced one accepted financial value. Importing a payment reversal discarded its direction and changed the findings. The fixtures below used local synthetic records, an ephemeral database and an in-process FastAPI client. No customer data or production deployment was involved.

| Input or claim | Observed result | Practical consequence |
|---|---|---|
| Digital PDF with invoice fields and repeated amount lines 10.00 then 999.00 | The normalized invoice contains 999.00. Both strings appear in the field provenance. | An ambiguous record can generate a financial finding without a conflict or review flag. The parser accepts one labeled key/value record per page. General invoice layouts require separate validation. |
| XLSX with the required amount header twice, with 10.00 and 999.00 underneath | Final amount is 999.00. The returned field provenance is empty. | Column order resolves a material conflict. The row locator and source hash cannot explain which conflicting cell supplied the winning amount. |
| Valid payment with kind REVERSAL | Import retained only payment_id, invoice_id and amount. In a complete synthetic invoice, the normalized reversal introduced SPLIT_OR_DUPLICATE_PAYMENT_UNRESOLVED. Passing the same row with its explicit reversal kind removed that finding. | Restoring the payment semantics changes the financial result. All document normalizers project to the required keys, so optional financial fields need explicit preservation. |
| XLSX formula cell acting as a payment ID | The returned identifier has a leading apostrophe. | Ordinary formula text was neutralized in this case. Macro-name detection is case-sensitive. An inert uppercase VBAPROJECT.BIN ZIP member passed admission. This probe exercised filename policy only. No executable macro was created or run. |
| Bad archive, blank PDF | Both raise IngestError. | Keep these controlled rejection behaviors. Image-only documents require OCR according to the explicit failure response. |
| 1,000,001-byte digital PDF | Accepted by the parser and returned HTTP 200 for the authorized tenant with local synthetic signing keys. | The advertised 1,000,000 source-byte limit is only applied by the CSV/JSON decoder. API base64 and HTTP body caps provide different limits. |
| Malformed authenticated base64 | HTTP 500. Same request for an unauthorized second tenant yielded 403. | The authorization gate precedes parsing. A malformed authenticated upload should return a client error. |
| XLSX and ZIP/PDF resource constraints | Source inspection shows summed ZIP member sizes, sheet and row caps. No explicit worksheet column/dimension cap or per-page decoded PDF text limit exists at the application boundary. | Memory, CPU and compressed-stream limits need worker-level qualification. No large decompression or denial-of-service test was run. |

Source anchors are `aurex/dispater_documents.py` (_pages_from_text, extract_pdf, extract_xlsx), `aurex/dispater_ingest.py` (REQUIRED, _decode, ingest_source), `aurex/dispater_api.py` (DocumentRequest, ingest_document), and `aurex/dispater_intelligence.py` (signed payment amount). The API returns ingestion_authenticated=false and keeps the ingestion evidence in a response wrapper outside the stored report. The returned XLSX processor identifies the generic ingestion schema. PDF provenance identifies the pypdf version. Source-byte custody and authenticated extraction-to-report lineage require additional work.

## Dependency evidence

The candidate declares pypdf and openpyxl in the regular project dependencies in pyproject.toml. The tested distributions were pypdf 6.21.4 (BSD-3-Clause), openpyxl 3.1.5 (MIT), and transitive et-xmlfile 2.0.0 (MIT), according to their installed distribution metadata. The pypdf distribution listed its license text in package records. The declared versions are ranges, so future installations may resolve differently. This review did not independently verify upstream package signatures, security advisories or the license disposition of every transitive component.

## Reproduction

From the clean detached review-174 checkout:

```sh
PYTHONPATH=. ../Valexii-Aurex/.venv/bin/python ../ccxxxvi/scripts/verification/ccxxxvi_cursor_174_documents.py
```

The [document probe](../../../scripts/verification/ccxxxvi_cursor_174_documents.py) guards the exact candidate SHA and loaded source path and emits JSON. **13 of 13 observations matched** in Python 3.12.14, exit 1 by design to signal reproduction of candidate defects. Exit 2 flags changed observations. The authorized-input 500 logged a base64 exception. The 403 control and synthetic SQLite report used temporary state. Developer tests and the other review lanes are separate evidence. No product files were changed.
