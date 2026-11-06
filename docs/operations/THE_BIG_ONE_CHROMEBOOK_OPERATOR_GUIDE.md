# THE BIG ONE — LOCAL CHROMEBOOK EXECUTION PROCEDURE
## Secure Real-Company Validation Guide for Product Owner

**Classification:** STRICTLY PRIVATE / OWNER-OPERATED / AIR-GAPPED OR LOCAL ONLY
**Customer Data Status:** PROHIBITED IN PUBLIC REPOSITORY
**Financial Authority:** NONE
**Inference Spend:** $0.00 (External Paid Inference OFF)

---

## 1. Operating Doctrine

1. **Originals are Inviolable:** Original files on the Chromebook or external drive are mounted read-only. The system never renames, mutates, or deletes any original file.
2. **Zero Cloud Egress:** All inventorying, text parsing, and deterministic reconciliation execute locally. No raw company records or unredacted outputs may be committed to public GitHub.
3. **Truth over Claims:** If a document cannot be parsed or requires OCR that is not installed locally, DISPATER records it as `REQUIRES_OCR` or `WITHHELD`. It never invents findings.

---

## 2. Step-by-Step Operator Instructions

### Step 1: Open Terminal on Chromebook
Ensure Python 3.12+ and dependencies (`valexii-aurex`, `pypdf`, `openpyxl`) are active:
```bash
python3 --version
```

### Step 2: Run Read-Only Local Discovery
Execute the read-only discovery scanner against your private company records folder:
```bash
python3 -c "
from aurex.the_big_one import scan_local_directory
import json

# Replace with the path to your USB drive or local Chromebook directory
REPORT_DIR = '/path/to/the_big_one_records'
TENANT_ID = 'the-big-one-operating-co'

report = scan_local_directory(REPORT_DIR, tenant_id=TENANT_ID)
print('Discovery Complete!')
print(json.dumps(report.to_summary(), indent=2))
"
```

### Step 3: Review Categorization
The scanner will output:
- `total_files_discovered`: Total file count.
- `eligible_digital_files`: Digital PDFs, XLSX, CSV, JSON ready for direct parsing.
- `files_requiring_ocr`: Scans/images that need local OCR runtime before extraction.
- `rejected_files`: Macro workbooks (.xlsm) or unsupported formats rejected for safety.
- `inventory_manifest_sha256`: Cryptographic seal of the scanned inventory.

### Step 4: Execute Deterministic Ingestion & Reconciliation
For eligible digital files, run the batch ingestion pipeline:
```bash
python3 -c "
from aurex.dispater_documents import extract_pdf, extract_xlsx
# Reconstruct economic events and reconcile against contract rates
print('Ready for local audit execution.')
"
```

### Step 5: Preserve Privacy
When reporting results back to engineering, provide **only** aggregate metrics (counts, execution times, error classes, manifest hash). **Do not paste customer names, proprietary line items, or employee identities.**
