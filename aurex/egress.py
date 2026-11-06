"""Deny-by-default outbound check for financial records.

This is an application guard. It is not a production network firewall and it
does not prove that the host blocks every socket.
"""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from aurex.customer_sovereignty import SovereigntyError, assert_no_effect

_APPROVED_LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})


def destination_allowed(url: str, *, purpose: str) -> bool:
    """True only for an explicit local inference hop. Financial export is never allowed."""
    assert_no_effect()
    if purpose != "LOCAL_INFERENCE":
        return False
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.username or parsed.password or parsed.query or parsed.fragment:
        return False
    return parsed.hostname in _APPROVED_LOOPBACK and parsed.port is not None


def connector_destination_allowed(url: str) -> bool:
    """True for loopback inference or a host named in AUREX_EGRESS_ALLOWLIST.

    An empty allowlist denies every non-loopback destination. This is an
    application check. It is not a container, host, or Railway firewall.
    """
    assert_no_effect()
    parsed = urlsplit(url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return False
    host = (parsed.hostname or "").casefold()
    # Loopback is not an implicit connector allow. Local inference uses destination_allowed.
    allowed = {
        item.strip().casefold()
        for item in os.environ.get("AUREX_EGRESS_ALLOWLIST", "").split(",")
        if item.strip()
    }
    return parsed.scheme in {"http", "https"} and bool(host) and host in allowed


def transmit_financial_record(url: str, payload: object) -> dict[str, object]:
    """Refuse every transmission of a financial record. Nothing is sent."""
    del url, payload
    assert_no_effect()
    raise SovereigntyError("FINANCIAL_EGRESS_PROHIBITED")
