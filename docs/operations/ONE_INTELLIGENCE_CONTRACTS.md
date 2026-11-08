# One Intelligence evidence contracts

This slice preserves the existing `dispater.ingestion.v1` and `aurex.manuscript_forensics.report.v1` boundaries. The names below describe the versioned mapping for future shared use. They do not introduce new persisted tables or endpoints.

| Record | Current versioned representation | Qualification boundary |
| --- | --- | --- |
| DocumentRecord | DISPATER tenant, source SHA-256, filename, format and parse outcome. Offline image report has source SHA-256, decoded dimensions and format. Record a source URL, license and derivation separately for historical inputs. | Received-byte identity does not authenticate the author or grant tenant access. Durable document IDs and original-byte custody are pending. |
| EvidenceRecord | DISPATER page or source row, field, extraction method/version, source digest and extraction qualification. Image layers and regions carry method parameters, bounds and individual content digests. | Extracted observations and pixel regions remain unverified evidence. Layer hashes do not identify glyphs. |
| AnalysisFinding | Existing DISPATER finding ID, category, evidence and explanation. The UI adds the PDF source hash prefix and page from the validated response. | Suspected exposure stays separate from confirmed recovery. Any future manuscript hypothesis must carry limitations and evidence IDs. |
| VerificationRecord | Existing DISPATER report receipt verifies persisted report integrity. Separate reproduction is recorded in the integration review. | No mutable browser control or model output can qualify a finding. A persisted independent witness record and contradiction workflow remain pending. |

The browser selects only a server-owned CSV or PDF fixture, with the tenant chosen server-side. Credentials remain in the server function. The PDF response must match the selected source digest and contain amount provenance for page 1. The report must agree with the stored run before the UI shows the result. OCR, models and research evidence do not write financial or qualification state.
