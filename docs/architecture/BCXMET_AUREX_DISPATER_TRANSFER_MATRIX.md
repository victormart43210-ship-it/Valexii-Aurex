# BCXMET → AUREX/DISPATER Transfer Matrix

Source basis: the CCXXVIII directive's concept descriptions only. The APK was unavailable, so **no row claims fidelity to BCXMET code**. "Implemented" means implemented here from the specification.

| Concept | Status | Where | Notes |
|---|---|---|---|
| Evidence provenance / canonical digest | IMPLEMENTED (adapted) | `aurex/evidence_kernel.py` `EvidenceRecord`, `digest` | Canonical JSON SHA-256. RFC 8785 not implemented. |
| Independent evidence roots | IMPLEMENTED | `EvidenceGraph.roots/independent_root_count` | Derived copies share a root; missing parent = own unknown root; cycles rejected. |
| Freshness states | IMPLEMENTED | `freshness_of` | Six states, fail-closed. Max age is caller policy. |
| Claim qualification | IMPLEMENTED | `qualify` | Model cannot corroborate/verify; VERIFIED needs human reviewer + 2 roots + CURRENT. |
| JOSAI capability governance | IMPLEMENTED (library) | `Capability`, `authorize` | `EXECUTE_FINANCIAL` never grantable. **Not yet wired into API endpoints.** |
| EMET / KAGAMI challenges | PARTIAL | `challenge_finding` | Deterministic checks only. Not wired into the reconciliation engine. |
| WEST outcome chain | IMPLEMENTED (library) | `RecoveryClaim` | Not persisted; not wired to API or UI. |
| Signed history repair | IMPLEMENTED + WIRED | `dispater_store.finding_history` | Returns only MAC-verified report values; mismatch → `IntegrityError`. |
| Receipt export preservation | IMPLEMENTED | `website/src/lib/dispater-contract.ts` | Schema now keeps `receipt_auth`/`receipt_mac`/`created_at`. |
| KEKKAI containment / quarantine | NOT IMPLEMENTED | — | CSV formula neutralization already exists (`report_to_csv`). No quarantine store. |
| Shield lifecycle → job fencing | NOT IMPLEMENTED | — | No job queue on main to fence; needs design. |
| TamperGuard native analysis | UNVERIFIED | — | APK unavailable. Android native anti-tamper is not server-side security. |
| Android VPN / Compose code | REJECTED | — | Not applicable to the backend. |
