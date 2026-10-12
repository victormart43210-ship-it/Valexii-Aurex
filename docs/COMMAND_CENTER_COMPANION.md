# AUREX Command Center — Companion Integration Contract

The desktop Command Center is an **optional local engineering companion**, not a replacement for `aurex.engine.AurexEngine`. It must never directly grant BCXMET or VALEXII product authority.

## Ownership

- Public repository: typed challenge protocol, independent evidence and evaluation engine, tests, open research.
- Optional local desktop companion: folder selection, local inventory, source-transfer preparation/verification, non-privileged task status, read-only Git inspection.
- Optional local tools: llama.cpp, Inspect AI, MobSF. They are independent adapters/services with separately verified install status and licenses.
- Private product repositories: remain isolated and must not be imported into public fixtures.

## Required interface

Every companion operation produces a structured task result: request ID, operation, execution state, start/end timestamps, evidence SHA-256 references, status (PASS/FAIL/NOT RUN/NOT VERIFIED), and explicit limitations. It never emits a product-authority grant.

For imports: verify manifest, path portability, per-file hashes, resource bounds and unique destination; reject overwrites; import into temporary staging; verify bytes again; and only then commit the new directory. Generated receipts may record local consistency, but they are self-issued and **not** independent attestations or digital signatures.

## Approval gates

Before making network calls, installing software, downloading models, pushing code, opening public issues containing submitted data, scanning external binaries, or incurring paid charges, display the scope and obtain explicit approval. Public-source transfers are **not full backups**, and automatic exclusion patterns cannot prove a bundle free of secrets.

## Integration status

The locally prepared V5 desktop prototype is a separate artifact and is **not included in this repository by this document**. Real Windows packaging, Chromebook/PC import, GitHub authentication/write workflows, installed model execution, and MobSF operations require separate implementation and validation.

See [CUSTOS test matrix](CUSTOS_TEST_MATRIX.md) for release evidence requirements.
