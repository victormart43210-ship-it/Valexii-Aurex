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
@dataclass(frozen=True)
class FilesystemAccessRule:
    allowed_read_paths: tuple[str, ...]
    allowed_write_paths: tuple[str, ...]


@dataclass(frozen=True)
class FilesystemDecision:
    allowed: bool
    reason: str


def evaluate_filesystem_access(
    path: str, mode: str, policy: FilesystemAccessRule
) -> FilesystemDecision:
    """Advisory filesystem preflight check before supervisor Landlock/OFS enforcement."""
    if not path or not path.startswith("/") or "\x00" in path or "\\" in path:
        return FilesystemDecision(False, "relative_or_invalid_path")
    if ".." in path.split("/"):
        return FilesystemDecision(False, "path_traversal_attempt")
    if mode not in ("read", "write"):
        return FilesystemDecision(False, "invalid_mode")

    targets = policy.allowed_read_paths if mode == "read" else policy.allowed_write_paths
    if any(
        not root.startswith("/") or "\x00" in root or "\\" in root
        or "//" in root or any(part in (".", "..") for part in root.split("/"))
        for root in targets
    ):
        return FilesystemDecision(False, "invalid_policy_path")
    for allowed_prefix in targets:
        if path == allowed_prefix or path.startswith(allowed_prefix.rstrip("/") + "/"):
            return FilesystemDecision(True, "path_allowlisted")

    return FilesystemDecision(False, "default_deny_filesystem")
