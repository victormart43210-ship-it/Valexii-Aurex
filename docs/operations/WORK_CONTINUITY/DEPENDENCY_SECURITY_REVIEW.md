# Dependency review — CCXXXVI

Work adds no runtime dependency, parser or model. This is an inventory/security observation; no automatic upgrades.

## Candidate parser dependencies
Cursor #174 adds pypdf >=6.21.4,<7 and openpyxl >=3.1.5,<4 to runtime dependencies. Tested installed versions are 6.21.4 and 3.1.5, transitive et-xmlfile 2.0.0. Installed metadata license evidence is in PYTHON_COMPONENT_INVENTORY.json. No original BCXMET Kotlin source copied. Its historical MIT/LICENSE vs Apache/README conflict remains recorded in the superseded source-recovery archive.

Only digital labeled-text PDF and text-cell XLSX are represented by actual code. PNG/JPEG/image-only PDF and OCR are rejected. Parser presence does not validate arbitrary forms, tables or financial truth. Workbook ZIP expansion is bounded, numeric cells rejected, macros rejected. Source review/probes remain authoritative for gaps. No country attribution or unverified international adapter counts as working software.

## Current JavaScript advisory scan
`cd review-171/website && npm audit --json` executed against the committed package-lock. Exit 1: 14 reported vulnerabilities (2 high, 12 moderate; 0 critical). Direct high entries include vite and zod. Exact advisory objects, ranges, dependency paths and fix hints: evidence/npm-audit-website.json. The website package-lock is byte-identical in #171/#172/#174. These are registry advisory reports, not proof of exploitation; no upgrade or runtime change performed. Review compatibility and rerun tests on a separately owned fix.

Python vulnerability scanner: NOT_RUN. Installed metadata is license/version evidence, not a vulnerability scan. License expression alone is not a complete legal review; distribution notices and deployment packaging still require review. No commercial/legal clearance claimed.

Deployment remains HOLD. Runtime dependencies are broad version ranges rather than a reproducible Python lock. Test environment versions are recorded, but future installs may resolve differently. No hosted deployment, paid inference, external OCR/model download or customer data used.
