"""Fail-closed, dependency-free policy preflight for a future OpenShell adapter.

This does NOT claim to instantiate or enforce an OpenShell sandbox.
Real network/process enforcement must occur in an external supervisor.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class EgressRule:
    host: str
    methods: frozenset[str]
    path_prefix: str = "/"


@dataclass(frozen=True)
class EgressDecision:
    allowed: bool
    reason: str


def evaluate_egress(url: str, method: str, rules: tuple[EgressRule, ...]) -> EgressDecision:
    """Advisory policy check; never substitute for supervisor enforcement."""
    try:
        target = urlsplit(url)
        host = target.hostname
        port = target.port
    except (ValueError, TypeError):
        return EgressDecision(False, "invalid_url")
    if target.scheme != "https" or not host or target.username or target.password:
        return EgressDecision(False, "invalid_destination")
    if port not in (None, 443) or target.fragment:
        return EgressDecision(False, "unsupported_destination")
    if not method or method.upper() != method:
        return EgressDecision(False, "invalid_method")
    for rule in rules:
        if not rule.host or rule.host != host or not rule.path_prefix.startswith("/"):
            continue
        if method not in rule.methods:
            continue
        prefix = rule.path_prefix
        path = target.path or "/"
        if path == prefix or (prefix.endswith("/") and path.startswith(prefix)) or path.startswith(prefix.rstrip("/") + "/"):
            return EgressDecision(True, "allowlisted")
    return EgressDecision(False, "default_deny")
