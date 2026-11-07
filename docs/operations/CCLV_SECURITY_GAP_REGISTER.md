# CCLV security gap register

Sourced from the integrated Cursor records (CCLII evidence anchor / privacy matrix) and this review; not independently re-proven here.

| Gap | Level | Status |
|-----|-------|--------|
| Rows + sidecar + checkpoint deleted together are undetectable | Application | OPEN (unresolved assurance gap) |
| Holder of both server keys can rewrite history | Threat model | OPEN, documented |
| Server HMAC is not independent attestation; external anchor | — | NOT VERIFIED |
| Received-byte verification: source identity UNVERIFIED | Application | OPEN |
| Egress allowlist is application-level only, no host/Railway firewall | Application vs Deployment | OPEN |
| AES-GCM covers report blob only; findings plaintext; not zero-knowledge | Application | Disclosed |
| Deletion/retention requests recorded, not executed | Application | OPEN |
| Independent human assurance | Organizational | OPEN (agent reviews are same-machine) |
| XAELI live staging connection | — | XAELI_LIVE_CONNECTION_NOT_VERIFIED (not attempted) |
| Secret scan (detect-secrets, heuristic): hits in tests/fixtures (e.g. aurex/ox/registry.py, several tests) | — | Not triaged; likely fixtures; a human must confirm |
| Dependency review / untrusted model loading review | — | Not performed in CCLV |
