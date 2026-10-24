# Canada / Finland integration recovery
Resume from the enclosing Git checkpoint on work/aurex-canada-finland-integration.
Read RECOVERY.json first. Do not restart completed milestones.
Authoritative dependency: PR119 CXXXII CP008 at 2ce2f654b0d5d1f21786dd587d9137d77695f420.
Ruling: continue from CXXXII and target that branch as explicitly authorized by the user's operation; it overrides the generic main-base rule. Cost: candidate depends on unmerged PR119 and needs eventual mainline reconciliation.
Owned paths: integrations/canada_finland, tests/test_canada_finland.py, acceptance, docs/operations/canada-finland, optional CI workflow.
Contract: existing canonical receipts/jobs unchanged. Synthetic-only offline archive export; no new financial authority.
Plan: (1) Robot acceptance keywords use the real backend/worker with temporary SQLite. (2) Export a verified fixed-fixture receipt as a standard BagIt transfer folder for Archivematica, excluding all other data. (3) Generate Tailscale policy for one explicit operator and staging host/port, no enrollment/network writes. (4) full tests, fresh source review, remote checkpoint.
No production, paid inference, model downloads, customer data, main merge or automatic deployment. Keep wg-easy candidate intact; do not run competing VPNs.
Live website, Archivematica ingest, Tailscale enforcement, Railway isolation: NOT VERIFIED. Recovery and reviewed source are the deliverables until infrastructure admission gates pass.

Checkpoint 002: optional tools and Robot suites implemented. 18 new tests and 3 Robot tests passed; full suite needs proxy-free rerun (2 existing httpx SOCKS import errors). Next: fresh review, regression, checkpoint. No live activation.
