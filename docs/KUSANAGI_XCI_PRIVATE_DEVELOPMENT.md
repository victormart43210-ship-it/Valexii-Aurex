# KUSANAGI XCI — Private AUREX Development Staging

**Status: SOURCE-ONLY. NOT DEPLOYED. NO PUBLIC ROUTES CREATED.**

This PR provides an independent **read-only local frontend** and isolated local **canonical AUREX FastAPI backend** in the existing repository. It does not replace or publish the existing Lovable 'Valexii Ai' website. No Railway, Cloudflare, DNS, or production credentials change.

## 1. Bootstrap on Linux / Raspberry Pi 5 / Chromebook / laptop

Requirements: 64-bit Linux, Git, Python 3.12+. A Pi 5 with 8–16 GB RAM and SSD can run this, but a Pi is optional.

Commands, execute one line at a time:

    git clone https://github.com/victormart43210-ship-it/Valexii-Aurex.git
    cd Valexii-Aurex
    git fetch origin feature/kusanagi-xci-private-dev-server
    git switch --track origin/feature/kusanagi-xci-private-dev-server
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -e '.[dev]'
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_private_dev_gateway.py
    bash scripts/run_private_dev.sh

Open http://127.0.0.1:8788 on the *same machine*. Username: 'aurex'. View the locally generated Basic password with:

    cat ~/.local/state/valexii-aurex/dev/preview-password

Never paste secrets into GitHub, ChatGPT, browser JavaScript, or public logs. The private state directory has restricted permissions and a dev-only token isolated from production. Both servers bind loopback: FastAPI :8766; read-only gateway :8788. Lab worker disabled, default budget $0, separate local SQLite. Never publish raw :8766 or workstation/app.py because those may include write/model functionality.

## 2. Cloudflare Access BEFORE Cloudflare Tunnel (owner action required)

Default local mode is **not safe to connect to a tunnel**. First create a Cloudflare Zero Trust **Self-hosted Access application** on a dedicated hostname such as dev-ox.valexii.com (only if the hostname is part of an active zone you control through Cloudflare). Configure explicit Allow → Emails → single owner's email policy; NO public Everyone, Bypass, or broad company-domain policy. Use verified login (MFA where supported) and short sessions. Obtain the Access app **AUD** and team domain.

Stop bootstrap with Ctrl+C. Restart in origin-verified Access mode:

    export CF_ACCESS_TEAM_DOMAIN='<team>.cloudflareaccess.com'
    export CF_ACCESS_AUD='<Access application AUD>'
    export CF_ACCESS_OWNER_EMAIL='<authorized email>'
    AUREX_PREVIEW_MODE=access bash scripts/run_private_dev.sh

In access mode the preview demands BOTH (1) a random HTTP Basic password created in the private state directory and (2) a signed Cloudflare Access RS256 JWT header matching the configured team domain issuer, audience, expiry, validity window, and owner email. Any missing/malformed credentials fail closed.

ONLY after Access works should you create a Cloudflare Tunnel published application route from the staging hostname to **http://127.0.0.1:8788**. In Tunnel settings enable **Protect with Access** where offered. Run cloudflared using the Cloudflare dashboard's private install instructions. Keep the tunnel token locally and never check it into GitHub. The source change alone does not create or activate a tunnel.

Samsung phone verification: unauthenticated access must be blocked; wrong email must be blocked; owner login should go through Access then HTTP Basic; read-only five-GET summary appears after successful authentication. Test negatives first. If any protection is missing, stop tunnel immediately.

## 3. Actual VALEXII.COM frontend is separate (KNOWN GAP)

This PR's preview is an independent minimal dashboard, **not** the original Lovable TanStack/Vite frontend. To edit that actual frontend from the laptop/Pi, obtain an authorized checkout/export of the existing Lovable project. Run its verified local build/dev commands without creating a competing production website. Protect any separate frontend staging hostname with Cloudflare Access; do not expose unrestricted Vite HMR or admin routes.

The published Lovable source 'src/lib/aurex-service.server.ts' presently rejects local and private HTTP URLs and requires HTTPS. Therefore its server-only backend client does **not** automatically connect to http://127.0.0.1:8766. A separately reviewed **development-only loopback exception** is needed in that project's server code to integrate the actual frontend with the local AUREX instance; preserve production restrictions and keep AUREX_SERVICE_TOKEN server-only.

## 4. Independent testing and rollback

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_private_dev_gateway.py
    ruff check tools/private_dev_gateway.py tests/test_private_dev_gateway.py
    mypy --strict tools/private_dev_gateway.py
    bash -n scripts/run_private_dev.sh
    ss -lntp

Required: both ports loopback, unauthenticated response 401, wrong Basic 401, invalid Access JWT 403 in access mode, POST to /api/status returns 405, malformed or oversized backend response HOLD, $0 budget visible. All five synthetic GETs may show **local PASS only**; the response still says independentVerification: NOT VERIFIED. Full canonical suite, real Pi, and remote Cloudflare phone checks NOT VERIFIED until run.

Stop processes with Ctrl+C. Disable/remove Cloudflare Tunnel route and Access application to retire exposure. DO NOT MERGE or deploy until independent source review and owner admission.

**Evidence → Qualification → Reality → Authority → Effect.** The system may never be its own sole witness.

Official docs:
https://developers.cloudflare.com/cloudflare-one/setup/secure-private-apps/private-web-app/
https://developers.cloudflare.com/tunnel/get-started/
https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/application-token/
