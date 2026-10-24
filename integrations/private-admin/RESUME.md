# AUREX private administrator access candidate
Resume from the enclosing Git commit. Fetch branch work/aurex-private-admin-candidate and reconcile newer work before editing.
Scope: integrations/private-admin plus its focused tests. This is an optional infrastructure configuration generator, not a second backend.
Plan: write rejection tests; implement offline JSON Compose renderer; verify full Python suite; review; publish draft PR. No provisioning or VPN startup in this session.
The renderer must require a digest and specific IPv4 bind address, bind UI to localhost, require explicit Compose profile, and include no secrets, Docker socket or AUREX storage.
Ruling: keep host activation HOLD because host identity, kernel, firewall, routes and console recovery are not verified. Cost: requires host validation before use.
Dependency: upstream wg-easy v15.4.0; no upstream implementation copied. See upstream AGPL-3.0 license before modification or redistribution.
No network connectivity or air-gap claim. Existing AUREX authentication, financial receipt authority and release holds remain.
