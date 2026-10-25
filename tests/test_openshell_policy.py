"""Synthetic policy-preflight regression tests."""
from aurex.openshell_policy import (
    EgressRule,
    create_policy_audit_entry,
    evaluate_credential_access,
    evaluate_egress,
    evaluate_filesystem_boundary,
)

RULES = (EgressRule("api.example.test", frozenset({"POST"}), "/v1/infer"),)


def test_explicitly_allowed_request():
    assert evaluate_egress("https://api.example.test/v1/infer", "POST", RULES).allowed


def test_default_deny_unknown_host():
    assert not evaluate_egress("https://untrusted.example/v1/infer", "POST", RULES).allowed


def test_default_deny_wrong_method():
    assert not evaluate_egress("https://api.example.test/v1/infer", "GET", RULES).allowed


def test_default_deny_path_confusion():
    assert not evaluate_egress("https://api.example.test/v1/inference", "POST", RULES).allowed


def test_default_deny_plaintext():
    assert not evaluate_egress("http://api.example.test/v1/infer", "POST", RULES).allowed


def test_default_deny_credentials():
    assert not evaluate_egress("https://u:p@api.example.test/v1/infer", "POST", RULES).allowed


def test_default_deny_bad_port():
    assert not evaluate_egress("https://api.example.test:8443/v1/infer", "POST", RULES).allowed


def test_default_deny_empty_rules():
    assert not evaluate_egress("https://api.example.test/v1/infer", "POST", ()).allowed


def test_credential_access_control():
    assert evaluate_credential_access("tenant_api_key", "tenant-a", "tenant-a").allowed
    assert not evaluate_credential_access("tenant_api_key", "tenant-a", "tenant-b").allowed
    assert not evaluate_credential_access("global_admin_key", "tenant-a", "tenant-a").allowed


def test_filesystem_boundary_control():
    allowed = ("/app/data/tenant-a", "/tmp/scratch")
    assert evaluate_filesystem_boundary("/app/data/tenant-a/file.json", allowed).allowed
    assert not evaluate_filesystem_boundary("/etc/passwd", allowed).allowed
    assert not evaluate_filesystem_boundary("/app/data/tenant-a/../tenant-b/file.json", allowed).allowed


def test_policy_audit_record_generation():
    rec = create_policy_audit_entry("egress_check", True, "allowlisted")
    assert rec.allowed is True
    assert len(rec.digest) == 64
