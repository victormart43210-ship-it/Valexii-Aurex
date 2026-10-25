# Trust boundaries and components

Client / DISPATER.AI → authenticated AUREX FastAPI API → quarantine job → immutable originals vault → type identification → isolated extraction workers → structured assertions → reconciliation → independent challenge → human approval → signed/canonical receipts → Sovereign Studio.

Production separation: API never parses hostile uploads in-process; workers use resource limits, no outbound network, filesystem confinement, malware scanning, decompression caps, timeout, and least privilege. Persist originals in versioned object storage with independently validated retention controls; PostgreSQL for tenant-scoped metadata; durable queue for jobs. SQLite only for local reference demo.

R13 intake & preservation; R14 document intelligence; R15 business reconciliation; R16 audit workspace. Each phase requires independent acceptance evidence.

Evidence graph: original bytes → SHA-256 → acquisition provenance → derivative → extractor/version → field assertion → cross-source comparison → candidate finding → challenger → human-reviewed finding → canonical receipt.

No automated financial authority, compliance certification, or production release.
