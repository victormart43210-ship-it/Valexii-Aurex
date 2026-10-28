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
