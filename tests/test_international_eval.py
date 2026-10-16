from aurex.international_eval import (
    Case,
    adversarial_cases,
    compare_models,
    evidence_support,
    regression_signals,
    run_cases,
)


def test_evidence_is_conservative():
    assert evidence_support("hello", ["Say hello there"]) is True
    assert evidence_support("invented", ["hello"]) is False
    assert evidence_support("hello", []) is None


def test_bounded_runner_and_error():
    cases = [Case("a", "one", "one"), Case("b", "two", "two")]
    assert len(run_cases(cases, lambda p: p, max_cases=1)) == 1
    result = run_cases(cases, lambda p: 1)
    assert all(x.error == "TypeError" and not x.exact_match for x in result)


def test_comparison_is_not_authority():
    results = compare_models(
        [Case("a", "q", "answer", ("answer is supported",))],
        {"local": lambda _: "answer"},
    )
    assert results["local"]["exact_matches"] == 1
    assert results["local"]["verification_status"] == "UNVERIFIED"


def test_regression_signals():
    data = regression_signals(
        [{"group": "api", "passed": True}, {"group": "api", "passed": False}]
    )
    assert data["api"]["failure_rate"] == 0.5
    assert len(adversarial_cases()) == 3
