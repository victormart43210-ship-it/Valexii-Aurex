# Headless CI runner recovery and reuse

Status: **NOT CONNECTED / NOT VERIFIED**. This change adds a manual smoke workflow only. It does not register or activate a runner.

## Historical leads (not proof of active host)
- GitLab MEDAURUS repository: `valexii-ai-medaurus-group/CoreGuard-Android`.
- Proposed Manus runner: `CUSTOS-Manus-Runner`, tags `medaurus,android,ubuntu`.
- Hetzner Ubuntu host was also proposed; no actual runner host or online state has been confirmed.
- Canonical AUREX repository remains GitHub `victormart43210-ship-it/Valexii-Aurex`.

## On the existing headless host (operator only)
1. Confirm machine identity and owner approval; do not reuse unknown/compromised hosts.
2. Check existing GitLab runner without exposing tokens: `sudo gitlab-runner list` and `sudo systemctl status gitlab-runner --no-pager` if installed. Inspect GitLab project Settings → CI/CD → Runners for last contact. Avoid printing config.toml or credentials.
3. Record OS, CPU/RAM/disk, network isolation, and whether the host is already executing MEDAURUS jobs. Keep MEDAURUS runner intact.
4. If host is suitable, use GitHub repo Settings → Actions → Runners → New self-hosted runner to obtain the **current** platform-specific installation and short-lived registration command. Install in a separate non-root directory/account. Never commit or paste registration tokens.
5. Assign labels `self-hosted`, `linux`, `x64`, `aurex-verification`. Do not attach production secrets or allow untrusted pull-request jobs. Configure dedicated service, restricted permissions, patching, and isolated job workspace.
6. After registration, confirm online status in GitHub. Manually dispatch `headless-runner-smoke.yml` on this branch. Preserve run URL, exact SHA, runner identity, logs and result.
7. Only after smoke PASS, plan a separate PR for offline Python/Bun tests with dependency pinning, caching, timeouts and independent verification. Do not add automatic deployment.

## Gates
- GitHub workflow exists ≠ registered runner.
- Queued workflow ≠ successful CI.
- Successful smoke ≠ Onyx live integration, OpenShell runtime containment, or production readiness.
- No production deploy, database migration, customer data, or privileged tokens.
- If the host is a low-memory Chromebook container, do not run full Onyx or concurrent builds there.
