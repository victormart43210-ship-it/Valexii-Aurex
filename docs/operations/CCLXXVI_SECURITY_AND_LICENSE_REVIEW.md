# CCLXXVI security and license review

This review was written by the same session that implemented the change. It is not an independent approval. Status: `INDEPENDENT_REVIEW_PENDING`.

## Authority

The new routes call `assert_no_effect()` and `authorize_tenant()`. They do not use a service token as a tenant grant. A missing bearer is HTTP 401. A dataset for another tenant is not returned; the test reads the golden dataset hash as `tenant-a` and gets HTTP 404.

`POST /v1/dispater/relationships` reconciles with the existing engine and stores that report. Confirmed recovery in the response is the engine value `0.00`. A disposition of `APPROVED` is rejected before a link is stored. `RECORDED_APPROVAL` is kept as a label and does not change the dollars.

Explanations refuse a finding that has no evidence list. They do not accept an amount from the caller. They do not call XAELI staging or any paid endpoint.

## Documents

Spreadsheet and PDF values are copied from the file. `require_not_inferred` rejects a field marked inferred or empty. A one-pixel PNG still fails with the existing OCR-not-installed error. Docling was not imported. Its PyPI package license for 2.148.0 is MIT. Its model licenses were not reviewed.

pypdf 6.21.4 reports `BSD-3-Clause`. openpyxl 3.1.5 reports `MIT`. Both were already dependencies. No package was added to `pyproject.toml`.

DuckDB 2.0.0 and Polars 2.1.0 were installed in this session only long enough to measure them. DuckDB's PyPI classifiers include `License :: OSI Approved :: MIT License`. The Polars 2.1.0 license text is the MIT grant. Neither import was added to the application.

## Isolation and limits

Relationship rows are deleted and replaced only for the same tenant and dataset hash, inside a transaction. The DISPATER run tables were not altered. The body-size middleware already covers `/v1/dispater`. Optional collections use the existing 2000-row cap.

No customer file, secret, model weight, or payment instruction was added.

## Remaining limits

There is no independent labeled extraction corpus. Scanned handwriting is not read. A recorded approval is not a human session. The dashboard was not built. Anomaly scores were not added. Jules did not run.
