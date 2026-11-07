# DISPATER.AI — AUDIT PACKAGE SPECIFICATION
**Engine Module:** `aurex/dispater_audit_package.py`
**Schema:** `dispater.synthetic.audit_package.v1`
**Statutory Scope:** U.S. Department of Transportation / FMCSA (49 CFR Parts 390-396)

---

## I. REGULATORY REQUIREMENTS CATALOG

1. **49 CFR § 391.51 — Driver Qualification File (DQF)**
   - Medical Examiner Certificate (MCSA-5876).
   - Annual Motor Vehicle Record (MVR) review.
   - Commercial Driver's License (CDL) validity.
2. **49 CFR § 395.8 — Hours of Service & Records of Duty Status**
   - Electronic Logging Device (ELD) or paper log retention.
3. **49 CFR § 396.11 — Driver Vehicle Inspection Reports (DVIR)**
   - Pre-trip and post-trip commercial equipment safety checks.
4. **49 CFR § 396.17 — Periodic Annual Vehicle Inspection**
   - Annual comprehensive mechanical safety inspection covering brakes, coupling, lighting, steering.
5. **49 CFR § 387.9 — Financial Responsibility & Towing Cargo Insurance**
   - Form BMC-91/BMC-91X commercial auto and on-hook towing cargo liability.

---

## II. EVIDENCE MANIFEST SPECIFICATION
Each generated audit package contains an immutable `manifest` array:
```json
{
  "artifact": "docs/DOC-TRUCK1-INSP.json",
  "category": "ANNUAL_INSPECTION",
  "sha256": "4a71b...e92"
}
```
The SHA-256 hash of the sorted manifest array is stamped as `manifest_sha256`.
The entire package (excluding the receipt key) is hashed as `package_receipt_sha256` for tamper-detection.

---

## III. UNRESOLVED EXCEPTIONS & LIMITATIONS
Missing records are classified as `UNRESOLVED` audit exceptions with assigned corrective actions. In accordance with AUREX doctrine, missing evidence in a synthetic sample does not conclusively establish a regulatory violation.
