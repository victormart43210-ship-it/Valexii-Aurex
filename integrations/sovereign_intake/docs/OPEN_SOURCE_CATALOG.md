# Deep-dive open-source component map (evaluate and pin before use)

| Function | Candidate | Upstream |
|---|---|---|
| File signature | Siegfried | https://github.com/richardlehane/siegfried |
| MIME detection | libmagic / file | https://github.com/file/file |
| Format fallback | Apache Tika / Tika Pipes | https://tika.apache.org/ |
| Document structure | Docling | https://github.com/docling-project/docling |
| PDF OCR derivative | OCRmyPDF | https://github.com/ocrmypdf/OCRmyPDF |
| Spreadsheet read | openpyxl | https://openpyxl.readthedocs.io/ |
| Legacy XLS | xlrd | https://github.com/python-excel/xlrd |
| Office fallback | LibreOffice headless | https://www.libreoffice.org/ |
| Cloud sync (isolated acquisition) | rclone | https://rclone.org/ |
| Metadata DB | PostgreSQL | https://www.postgresql.org/ |
| S3 compatible vault candidate | SeaweedFS | https://github.com/seaweedfs/seaweedfs |
| Academic PDF optional | GROBID | https://github.com/kermitt2/grobid |
| Historical OCR optional | Kraken | https://github.com/mittagessen/kraken |
| Historical transcription optional | eScriptorium | https://gitlab.com/scripta/escriptorium |
| Antivirus candidate | ClamAV | https://www.clamav.net/ |

**Dependency policy:** No third-party source vendored. Check each license, security advisories, compatibility, model weights and data-use terms before installing. Prefer subprocess isolation for OCRmyPDF and LibreOffice; do not expose Tika directly to customers. Do not default to archived community MinIO without a fresh maintenance/license review. NVIDIA/Qwen adapters are optional and untrusted for audit authority.
