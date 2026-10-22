# AUREX / VALEXII — Coolify Cloud + Renovate onboarding

**Status: PREPARED / NOT INSTALLED OR CONNECTED / NOT DEPLOYED.**
This guide makes no production change and does not authorize subscription purchases, key sharing, a protected-main merge or a new server.

## Canonical architecture and safety

- Canonical backend source: `victormart43210-ship-it/Valexii-Aurex`; protected merge target: `main`.
- Railway remains the existing **production** AUREX API; do not repoint the Railway source, deploy staged variables, or modify public routing.
- Lovable remains the actual published VALEXII.COM frontend; GitHub `website/` is a potentially older snapshot. It is initially excluded from Renovate until exact source parity and frontend CI are established.
- Existing Hetzner CPX12 Ubuntu server: **1 vCPU, 2 GB RAM, 40 GB storage**. Do **not** purchase another VM or install a heavy management control plane on this small host. Use Coolify **Cloud-managed** control plane, with this existing server only as a lightweight dev/test worker after validation.
- Do not expose AUREX workstation, Qwen/Ollama, SQLite, privileged Docker socket, or production credentials to the internet.
- Keep self-hosted GitHub/GitLab runners isolated from arbitrary public PR code and production secrets.

## Coolify Cloud — manual owner actions

Official instructions:
- https://coolify.io/docs/start-with-cloud
- https://coolify.io/docs/core/infrastructure/servers/add-server
- https://coolify.io/docs/core/security-model

1. Sign in or register at https://app.coolify.io/register. Coolify Cloud lists **$5/month** base for two connected server slots (separate from existing Hetzner VM charges). **Owner must approve any checkout**; do not select "Buy & Create Server".
2. Before changing the server, inspect its existing workloads, disk, RAM, Docker/GitLab runner state, SSH and firewall. Snapshot/backup first. Coolify validation can install or restart Docker, interrupting existing workloads.
3. In Coolify Cloud, navigate **Keys & Tokens → Private Keys → Generate ED25519**. Copy only the PUBLIC key to the trusted Hetzner console. Never paste the private key into chat, a repository, or a public log.
4. Using an existing secured admin session, append the key to the selected SSH user's `~/.ssh/authorized_keys`. Ensure `~/.ssh` permissions 700 and file permissions 600; don't remove existing working keys. Restrict SSH ingress to necessary sources; do not make all ports public.
5. Choose **Servers → New server → IP address or domain** and provide the *existing* machine IP from the Hetzner dashboard, SSH port, user and the selected Coolify private key. Avoid Coolify's new-server purchase workflow.
6. Validate the server only after verifying Docker restart impact; capture the resulting connection status. Initially use only for low-memory, non-production work.
7. Keep Railway, Lovable, DNS, live secrets and automated production deployment unchanged. Review resource caps, monitoring, backups and rollback before adding persistent services.

### Hetzner read-only host preflight

Run locally inside the existing Hetzner console, share sanitized output only:

```sh
hostnamectl
free -h
df -h /
systemctl is-active ssh || systemctl is-active sshd || true
command -v docker && docker ps --format '{{.Names}} {{.Status}}' || true
command -v gitlab-runner && gitlab-runner --version || true
ss -lnt
```

Do not paste passwords, private SSH keys, API tokens, environment dumps or secrets into chat or GitHub.

## Renovate — manual GitHub App installation

Official app: https://github.com/apps/renovate
Documentation: https://docs.renovatebot.com/

1. Owner signs in to GitHub and selects **Install** on the Renovate app. Choose **Only select repositories** and authorize the existing `victormart43210-ship-it/Valexii-Aurex` repository. Review requested permissions.
2. Review any bot-created onboarding PR and this repository's `renovate.json`. Do **not** merge duplicated configurations. Merge this reviewed configuration only after exact-head CI and authorized protected-main admission.
3. The config opts out of **ALL AUTOMERGE**, limits regular update PRs to **2 concurrent**, and schedules creation to Friday afternoon/evening America/Chicago. Review bot PRs manually.
4. Initially exclude `website/`, `integrations/`, `examples/`, and snapshots to avoid modifying disconnected historical copies. Later enable website dependencies only when Lovable source parity and TypeScript build checks have been verified.
5. Never treat dependency PRs, passing unit tests, or a successful Docker build as proof of production safety.

## Admission / status

- Renovate source configuration: **STAGED ON REVIEW PR**; app installation: **NOT VERIFIED**.
- Coolify Cloud login/subscription: **NOT VERIFIED**; Hetzner SSH authorized: **NOT VERIFIED**.
- Coolify server validation: **NOT RUN**; Railway/Lovable production deployment changes: **NONE**.
- AUREX financial/security authority: **HOLD**.
