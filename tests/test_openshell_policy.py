"""Synthetic policy-preflight regression tests."""
from aurex.openshell_policy import EgressRule, evaluate_egress

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
def test_evaluate_filesystem_access() -> None:
    from aurex.openshell_policy import FilesystemAccessRule, evaluate_filesystem_access

    rule = FilesystemAccessRule(
        allowed_read_paths=("/app", "/tmp/audit"),
        allowed_write_paths=("/tmp/audit",),
    )

    # Valid read
    res = evaluate_filesystem_access("/app/aurex/api.py", "read", rule)
    assert res.allowed is True
    assert res.reason == "path_allowlisted"

    # Valid write
    res = evaluate_filesystem_access("/tmp/audit/job1.json", "write", rule)
    assert res.allowed is True

    # Path traversal block
    res = evaluate_filesystem_access("/app/../etc/passwd", "read", rule)
    assert res.allowed is False
    assert res.reason == "path_traversal_attempt"

    # Unallowed path block
    res = evaluate_filesystem_access("/etc/shadow", "read", rule)
    assert res.allowed is False
    assert res.reason == "default_deny_filesystem"
