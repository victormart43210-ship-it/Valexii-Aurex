# AUREX private administrator access candidate
Resume from the enclosing Git commit. Fetch branch work/aurex-private-admin-candidate and reconcile newer work before editing.
Scope: integrations/private-admin plus its focused tests. This is an optional infrastructure configuration generator, not a second backend.
Plan: write rejection tests; implement offline JSON Compose renderer; verify full Python suite; review; publish draft PR. No provisioning or VPN startup in this session.
The renderer must require a digest and specific IPv4 bind address, bind UI to localhost, require explicit Compose profile, and include no secrets, Docker socket or AUREX storage.
Ruling: keep host activation HOLD because host identity, kernel, firewall, routes and console recovery are not verified. Cost: requires host validation before use.
Dependency: upstream wg-easy v15.4.0; no upstream implementation copied. See upstream AGPL-3.0 license before modification or redistribution.
No network connectivity or air-gap claim. Existing AUREX authentication, financial receipt authority and release holds remain.

Checkpoint002: implementation and focused/full suite complete; see TEST_RESULTS.txt. Separate source review pending. No Hetzner connector or host session is available. Fetch branch head, read review, then resolve host admission. No credentials should be pasted into chat. Do not rerun completed development just because context was lost.

Checkpoint003: draft PR126; fresh reviewer finished, no draft blocker. Read REVIEW.md for limitations and deferred test coverage. Source code unchanged since checkpoint002. Remote source snapshot dea2c6d7ccbbe9caacc84f72f29e25422cfe688c verified. Current checkpoint identity is enclosing commit; do not treat source hash as its own commit. Deployment HOLD, production unchanged.
