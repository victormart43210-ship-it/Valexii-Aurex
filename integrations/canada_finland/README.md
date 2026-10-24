# Optional Canadian / Finnish integrations

Source-only adapters on the existing CXXXII financial integration. No new financial engine, no replacement website/database, no service activation. Install test tools with `python -m pip install -e '.[dev]' -r acceptance/requirements.txt` from the repository root.

## Robot Framework (Apache-2.0)

`python -m robot --outputdir /tmp/aurex-robot acceptance/canada_finland.robot`

Runs existing canonical acceptance tests rather than duplicating financial contracts. Includes the real local HTTP supervisor/worker, SQLite persistence and restart, receipt corruption rejection, and optional integration tests. Temporary synthetic credentials only; no external providers or hosted calls. Results in Robot XML/HTML are technical test evidence, not independent financial certification.

`acceptance/website.robot` is a separate manual owner UI test, never included in CI. Requires Robot Framework Browser installed and Chromium initialized using its official installation instructions; browser binaries are NOT runtime dependencies. It refuses to open the site unless `AUREX_BROWSER_STAGING_ADMITTED=1` and `AUREX_OWNER_STORAGE_STATE` points to an operator-controlled authenticated browser storage-state file outside the repo. That file is a credential: never commit or upload it or browser artifacts. Do not place a Railway service bearer in it. The suite submits once, then reads only; missing UI/backend/auth fails. Selector compatibility with the live Lovable revision is NOT VERIFIED. It checks displayed receipt shape, not independent backend persistence or source truth. Keep admission unset until Railway volume isolation, rollback and existing-workbench mount are verified. Run with reports disabled for the credential-bearing session:

`python -m robot --output NONE --log NONE --report NONE acceptance/website.robot`

## Archivematica (upstream AGPL-3.0; no upstream code copied)

`python -m integrations.canada_finland.tools export --receipt /private/receipt.json --job-id job-<24 hex> --destination /private/new-bag`

Use a freshly retrieved authenticated receipt and its separately recorded submitted job ID. The exporter verifies the canonical receipt contract and SHA-256, then compares the observation bytes against the existing engine's fixed fictional fixture. Extra fields, real records, altered counts, authority promotion, cancelled jobs and digest mismatches fail before writes. The output is a BagIt 0.97 unzipped transfer folder with one payload (`data/receipt.json`), SHA-256 payload/tag manifests and explicit NONE/HOLD/NOT VERIFIED metadata. Parent directory must be trusted and private; existing destinations are never overwritten. Write errors remove incomplete output. Input file capped at 24KB.

Exporter does not authenticate the origin of a JSON file or prove job execution. GitHub recovery and canonical SQLite remain authoritative. Bag validity is not archival ingest success. In an isolated Archivematica instance, select **Unzipped bag**, ingest this directory, then record transfer/AIP IDs, storage location, fixity results and retrieval evidence. Actual ingest is NOT RUN: no instance configured. No customer records, automated uploads, credentials or databases are included. Do not install Archivematica's multi-service stack on the 2.7GiB Chromebook. Deployment/cost assessment remains required.

## Tailscale (core BSD-3-Clause; hosted control plane proprietary)

`python -m integrations.canada_finland.tools tailscale-policy --owner owner@example.com --host 100.64.0.10 --port 443`

Produces JSON only. Replace the example with the verified owner identity and staging device's Tailscale IPv4 address. Grants one owner TCP 443 (or explicitly 8443), empty legacy ACL/SSH sections and negative tests for other service ports. No broad selectors, routes, exit nodes, enrollment keys, daemon startup or public exposure. The generator cannot prove the IP belongs to staging or validate provider enforcement.

Use ONLY as a complete candidate for a dedicated staging tailnet after inventory, current-policy backup, provider policy validation, negative tests from a second identity and revocation test. Never overwrite an existing tailnet policy or append to existing allow-all rules. API owner authentication is still mandatory. A Tailscale address alone is not storage isolation. Hosted plan cost and Headscale feature compatibility are NOT VERIFIED. Headscale is a separate project; this generator has not been validated against it.

The wg-easy candidate in PR126 remains intact. Select one access mechanism after an operational comparison; do not deploy both by default. No VPN or tailnet changes were made here.

## Rollback and source references

Rollback source by reverting this PR's changes. No infrastructure/data migration to roll back. For later activation, back up tailnet policy separately; remove only newly enrolled staging devices and restore the verified prior policy. Archive files are independent copies; retain the SQLite source and never delete existing archives as rollback.

Reviewed 2026-10-24:
- https://github.com/robotframework/robotframework (acceptance tool pinned 7.4.2)
- https://github.com/MarketSquare/robotframework-browser (manual UI candidate; not installed/verified)
- https://archivematica.org/en/docs/archivematica-1.17/user-manual/transfer/transfer/ (unzipped BagIt transfer)
- https://github.com/artefactual/archivematica (AGPL-3.0)
- https://tailscale.com/docs/reference/syntax/grants
- https://tailscale.com/docs/reference/syntax/policy-file
- https://github.com/tailscale/tailscale

Open-source availability does not imply zero hosting cost or independent financial accuracy.
