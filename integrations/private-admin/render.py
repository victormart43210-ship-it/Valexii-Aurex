"""Render a disabled-by-default wg-easy candidate; never execute host commands."""
from __future__ import annotations

import argparse
import ipaddress
import json
import re


def image_digest(value: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise argparse.ArgumentTypeError("A reviewed sha256 image digest is required, not a tag")
    return value


def host_address(value: str) -> str:
    try:
        address = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        raise argparse.ArgumentTypeError("A specific host IPv4 address is required") from None
    if (address.is_unspecified or address.is_loopback or address.is_multicast
            or address.is_link_local or address.is_reserved):
        raise argparse.ArgumentTypeError("Wildcard, loopback, multicast and reserved binds refused")
    return str(address)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-digest", required=True, type=image_digest)
    parser.add_argument("--vpn-bind-ip", required=True, type=host_address)
    args = parser.parse_args()
    candidate = {
        "name": "aurex-private-admin",
        "services": {
            "wg-easy": {
                "image": "ghcr.io/wg-easy/wg-easy@" + args.image_digest,
                "profiles": ["admin-evaluation"],
                "restart": "no",
                "ports": [
                    f"{args.vpn_bind_ip}:51820:51820/udp",
                    "127.0.0.1:51821:51821/tcp",
                ],
                "environment": {
                    "INSECURE": "true",
                    "DISABLE_IPV6": "true",
                    "DISABLE_VERSION_CHECK": "true",
                },
                "cap_add": ["NET_ADMIN"],
                "security_opt": ["no-new-privileges:true"],
                "sysctls": {
                    "net.ipv4.ip_forward": "1",
                    "net.ipv4.conf.all.src_valid_mark": "1",
                },
                "volumes": ["wireguard_state:/etc/wireguard"],
                "networks": ["management"],
            }
        },
        "volumes": {"wireguard_state": {}},
        "networks": {"management": {"driver": "bridge"}},
    }
    print(json.dumps(candidate, indent=2))


if __name__ == "__main__":
    main()
