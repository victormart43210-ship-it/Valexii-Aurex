# Cryptographic Evidence Verification

- **Module:** `aurex/experiments/admission.py`
- **Scheme:** Ed25519 signature verification over canonical JSON `fingerprint`
- **Rules:**
  - `SIGNED != VERIFIED`: An attestation signature verifies identity, not independent truth.
  - `VERIFIED != AUTHORIZED`: Independent verification is required before promotion.
  - Unsigned declarations return `NOT_VERIFIED`.
  - Mismatched verifier IDs or corrupted signatures return `HOLD`.
