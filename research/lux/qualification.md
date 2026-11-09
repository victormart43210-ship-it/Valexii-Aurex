# VALEXII LUX — Source Qualification Contract

1. **Relevance:** each source must identify one or more VALEXII products and a concrete research question.
2. **Identity:** capture upstream institution/publisher, canonical URL, identifiers (DOI, ISBN, shelfmark, repository ID), authors and edition.
3. **Rights:** distinguish metadata-only, link-only, public-domain, open-license and restricted content. Public access does not imply redistribution permission. Check jurisdiction and each edition's rights before ingesting files.
4. **Evidence:** preserve retrieval date, exact source URL, checksums for authorized downloads, extraction method, page/folio and limitations.
5. **Qualification:** statuses DISCOVERED -> SOURCE_VERIFIED -> RIGHTS_REVIEWED -> INDEPENDENT_REVIEWED -> ADMITTED. Any failure -> WITHHELD.
6. **Research claims:** distinguish primary sources, peer-reviewed research, historical interpretation, hypotheses and speculation.
7. **Separation:** work, edition, physical artifact, dataset and scientific paper are distinct record types. Only independently verified physical artifacts may enter the curated 666 count.
8. **Security:** quarantine uploads, validate MIME and archive contents, enforce file limits, block active content, protect against SSRF, prompt injection, path traversal and CSV formula injection.
9. **Authority:** AUREX may analyze and recommend, but cannot approve its own findings or deploy modifications. Human approval and independent evidence are required.
10. **Operations:** no automatic external paid inference, no customer data, no unapproved publication, no production changes.
