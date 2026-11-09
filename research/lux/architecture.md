# Public upstream patterns — research only

- Imperial Library of Trantor: https://github.com/trantor-library/trantor — historical Go EPUB ingestion, search, cover extraction and chapter reader. Old code; do not vendor or deploy without license, dependency and security review. Its software license does not grant rights to its ebook collection.
- Project Gutenberg metadata: https://www.gutenberg.org/ebooks/offline_catalogs.html — use official machine-readable catalogue feeds, not page-by-page scraping.
- IIIF specifications: https://iiif.io/api/ — standardized manuscript images and presentation manifests.
- Mirador: https://github.com/ProjectMirador/mirador — manuscript viewer; check applicable package licenses.
- PsiTek: https://psitek.net/ — editorial inspiration for cover, description and read-now layout; do not copy copyrighted content or site assets.
- OpenAlex: https://openalex.org/ — publication/institution discovery, not a blanket full-text license.
- CERN Open Data: https://opendata.cern/ — research datasets with record-specific access and reuse conditions.
- CERN Repository: https://repository.cern/ — institutional records and linked publications.
- Zenodo: https://zenodo.org/ — research records and file-level licenses.

Suggested interface: `LUXSourceRecord` -> validate -> deduplicate by stable identifiers -> source/rights review -> independent review -> admitted read-only catalogue. Authorized files stored separately with content hashes; metadata references in Git. Do not create a second AUREX service or grant runtime authority.
