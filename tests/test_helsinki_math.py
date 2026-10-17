from aurex.helsinki_math import MathematicalProblem, evaluate_math_problem


def test_helsinki_math_evaluation_correct() -> None:
    prob = MathematicalProblem(
        problem_id="p-001",
        domain="algebra",
        prompt="Solve x = 2",
        solution_target="x = 2",
    )
    eval_res = evaluate_math_problem(prob, "x = 2")
    assert eval_res.correct is True
    assert eval_res.information_gain_bits == 1.0


def test_helsinki_math_evaluation_rejects_substring_collision() -> None:
    prob = MathematicalProblem(
        problem_id="p-002",
        domain="algebra",
        prompt="Solve target",
        solution_target="2",
    )
    eval_res = evaluate_math_problem(prob, "20")
    assert eval_res.correct is False
    assert eval_res.information_gain_bits == 0.0


def test_helsinki_math_evaluation_incorrect() -> None:
    prob = MathematicalProblem(
        problem_id="p-003",
        domain="calculus",
        prompt="Derive sin(x)",
        solution_target="cos(x)",
    )
    eval_res = evaluate_math_problem(prob, "tan(x)")
    assert eval_res.correct is False
    assert eval_res.information_gain_bits == 0.0
