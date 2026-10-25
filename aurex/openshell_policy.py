"""Fail-closed, dependency-free policy preflight for NVIDIA OpenShell adapter.

This policy preflight evaluates egress, credential boundary, filesystem isolation,
and tenant isolation rules. It produces structured audit logs. Real network, filesystem,
and process enforcement must occur in an external supervisor (e.g. OpenShell Supervisor).
"""
from __future__ import annotations

import hashlib
import time
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


@dataclass(frozen=True)
class PolicyAuditRecord:
    timestamp: float
    action: str
    allowed: bool
    reason: str
    digest: str


def evaluate_egress(url: str, method: str, rules: tuple[EgressRule, ...]) -> EgressDecision:
    """Advisory egress check; never substitute for supervisor enforcement."""
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


def evaluate_credential_access(requested_secret_id: str, worker_tenant_id: str, allowed_tenant_id: str) -> EgressDecision:
    """Verify credentials remain mediated outside worker environment and restricted by tenant."""
    if not requested_secret_id or not worker_tenant_id or not allowed_tenant_id:
        return EgressDecision(False, "missing_identifier")
    if worker_tenant_id != allowed_tenant_id:
        return EgressDecision(False, "tenant_mismatch")
    if requested_secret_id.startswith("global_admin") or "root" in requested_secret_id:
        return EgressDecision(False, "unauthorized_secret_scope")
    return EgressDecision(True, "credential_access_permitted")


def evaluate_filesystem_boundary(requested_path: str, allowed_prefixes: tuple[str, ...]) -> EgressDecision:
    """Verify filesystem access remains constrained within explicitly permitted directories."""
    if not requested_path or ".." in requested_path or requested_path.startswith("/etc") or requested_path.startswith("/proc"):
        return EgressDecision(False, "prohibited_path")
    for prefix in allowed_prefixes:
        if requested_path.startswith(prefix):
            return EgressDecision(True, "path_allowed")
    return EgressDecision(False, "default_deny_filesystem")


def create_policy_audit_entry(action: str, allowed: bool, reason: str) -> PolicyAuditRecord:
    ts = time.time()
    payload = f"{ts}:{action}:{allowed}:{reason}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return PolicyAuditRecord(timestamp=ts, action=action, allowed=allowed, reason=reason, digest=digest)
