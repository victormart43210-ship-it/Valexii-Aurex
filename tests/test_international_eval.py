from aurex.international_eval import evaluate_international_response


def test_evaluate_international_response_pass() -> None:
    obs = evaluate_international_response(
        benchmark_id="bench-001",
        prompt="Explain quantum entanglement",
        response_text="Quantum entanglement is a physical phenomenon...",
        expected_pattern="phenomenon",
    )
    assert obs.passed is True
    assert len(obs.digest_sha256()) == 64


def test_evaluate_international_response_fail() -> None:
    obs = evaluate_international_response(
        benchmark_id="bench-002",
        prompt="Explain relativity",
        response_text="Gravity affects spacetime.",
        expected_pattern="speed of light",
    )
    assert obs.passed is False
