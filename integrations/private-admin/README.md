# AUREX private administrator access — source candidate

HOST DEPLOYMENT HOLD. This optional wg-easy service manages WireGuard peers;
it is separate from AUREX's API, financial engine and receipt authority.
No server accessed, image pulled, firewall changed or resource provisioned.

## Provenance

Reviewed upstream v15.4.0:
- https://github.com/wg-easy/wg-easy/releases/tag/v15.4.0
- https://github.com/wg-easy/wg-easy/blob/v15.4.0/docs/content/advanced/config/optional-config.md
- https://github.com/wg-easy/wg-easy/blob/v15.4.0/docker-compose.yml
- https://github.com/wg-easy/wg-easy/blob/v15.4.0/LICENSE

Upstream is AGPL-3.0-only. No upstream implementation is vendored here.
Review license/provenance before modifying or redistributing upstream software.
Obtain a reviewed, platform-compatible registry digest for the selected release.
Digest syntax validation does not prove provenance or vulnerability status.

## Offline renderer

Python 3.12+, standard library only. No network, Docker or subprocess execution.

    python integrations/private-admin/render.py --image-digest sha256:<reviewed-64-hex-digest> --vpn-bind-ip <verified-host-IPv4> > /tmp/aurex-private-admin.compose.json

Replace placeholders; no default image/host is supplied. JSON is Compose input.
Never pass credentials or private keys as arguments. This only renders to stdout.
An admitted host operator can validate the result using Docker Compose config:

    docker compose -f /tmp/aurex-private-admin.compose.json --profile admin-evaluation config --quiet

Docker validation/startup is NOT RUN here. The explicit profile avoids ordinary
compose up activation; it is not an authorization boundary against Docker users.
Restart is disabled during evaluation. No automatic updates are configured.
NET_ADMIN applies to the container network namespace. No privileged mode, host
network, Docker socket, AUREX database or service bearer is supplied.
Host WireGuard support must already be loaded: unlike upstream module-loading
configuration, SYS_MODULE and /lib/modules are omitted. Reduced-capability boot
requires an actual host test before admission; it is currently NOT VERIFIED.

## Management boundary

TCP 51821 is published only on host 127.0.0.1. INSECURE=true permits HTTP for
this loopback-only UI, never a public binding. Bootstrap through an authenticated
SSH local tunnel to host loopback; open http://127.0.0.1:51821 on that client.
Use the Chromebook if no verified phone SSH tunnel is available. Do not open
TCP 51821 in the cloud firewall. No unattended setup/password bypass is supplied;
complete upstream onboarding through the protected tunnel.
Other trusted host processes/containers may still reach the service. A compromised
Docker host is outside this boundary; localhost binding cannot protect against it.

Only UDP 51820 binds the supplied IPv4 address. Verify that the address is actually
assigned on the host and whether NAT/cloud rules are required. IPv6 VPN support is
disabled initially; host IPv6 exposure must be tested separately.

DO NOT enroll peers until routing/firewall rules are reviewed. Upstream generated
defaults are NOT an AUREX authorization policy. Define exact allowed target IPs
and admin ports, deny all other peer-to-host/peer-to-peer/forwarded traffic, and
test enforcement before enrollment. Client AllowedIPs are routing instructions,
not a server-side access boundary. Do not advertise a default route or a whole
production subnet. Account for Docker forwarding and both IP families.

Start with one disposable peer, then separate revocable Chromebook/phone peers.
Never store private keys, QR codes or live state backups in GitHub/chat/logs.
Back up the new WireGuard state to an encrypted access-controlled destination;
it contains keys and configuration. AUREX owner authentication, worker leases,
bearer boundary and receipt checks still apply. Public VALEXII.COM continues using
its server-side adapter. Never share SQLite files/volumes through this VPN.

## Required host admission evidence

1. Exact Hetzner host/account ownership, OS/architecture, Docker version, kernel
   support and out-of-band console access.
2. Read-only inventory of services, ports, routes and firewall; collision-free VPN
   and Docker address ranges; no production exposure.
3. Reviewed image digest, Compose validation and actual reduced-capability boot.
   Confirm unauthenticated remote setup is inaccessible.
4. Encrypted backup plus restore rehearsal and pre-change firewall/routing capture.
5. Deny-by-default server policy; off-host TCP 51821 blocked; unauthorized clients,
   unrelated targets and peer-to-peer traffic denied; revocation tested.
6. Restart/reconnect, DNS and IPv6 exposure tests; record sanitized evidence with
   timestamp, source/image digest and exact commands.
7. Admit only a bounded staging pilot after the above pass. Production excluded.

All host checks currently NOT VERIFIED. A VPN is not an air gap and cannot certify
financial accuracy, tenant isolation or independent review.

## Rollback and recovery

Before activation record the new container/volume names and exact firewall diff.
On failure stop only the new service, revoke test peers, revert only documented
new routes/rules, and use the out-of-band console if needed. Preserve the new
volume for investigation; never use down -v or prune existing host resources.
No activation or firewall-change command is automated by this repository.

Run `python -m pytest -q tests/test_private_admin_candidate.py` for CLI rejection
and configuration tests. These do not prove runtime confinement. Read RECOVERY.json
and RESUME.md before resuming. n3n and model training remain deferred; the existing
staging financial demonstration remains the main integration priority.
