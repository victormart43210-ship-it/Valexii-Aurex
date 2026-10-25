# Canonical integration contract

1. Verify repo identity, branch, clean working tree, and current SHA of Valexii-Aurex.
2. Review ZIP SHA256, manifest, paths, sizes, and test output. Dry run additive changes only.
3. Add intake routes behind existing bearer authentication and tenant authorization; do not create a second authentication or job system.
4. Map evidence metadata to existing EvidenceLedger and durable jobs; never replace existing schema blindly.
5. Use constrained isolated worker queue for every untrusted file; never invoke extraction directly inside API.
6. Add owner-only Sovereign Studio review UI; show HOLD / NOT VERIFIED for missing evidence.
7. Require separate reviewer identity, reviewer event and receipt verification; model reviewer ≠ independent witness.
8. Validate tenant isolation, ZIP bombs, symlinks, macros, idempotency, worker restarts, tamper, retries, upload caps and retention policy.
9. Test synthetic towing invoices, tow tickets, dispatch and payments, then oilfield tickets. No customer data in pilot until security sign-off.
10. Publish only after independent verification and explicit owner approval. Production remains HOLD.

Do not overwrite RECOVERY.json or RESUME.md; append reviewed checkpoint entries during integration.
