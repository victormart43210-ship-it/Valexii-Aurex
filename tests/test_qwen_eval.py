from aurex.evals.qwen_eval import QwenEvalTask, evaluate_qwen_task


def test_qwen_eval_instruction_following_pass() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-01",
        task_category="instruction_following",
        prompt="List three primary colors",
        expected_keyword="red",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", "The primary colors are red, blue, and yellow.")
    assert res.passed is True
    assert len(res.digest_sha256()) == 64


def test_qwen_eval_empty_response_fails() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-02",
        task_category="instruction_following",
        prompt="Describe the security boundary",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", "   ")
    assert res.passed is False


def test_qwen_eval_json_compliance_pass() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-03",
        task_category="json_compliance",
        prompt="Output JSON object with status",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", '{"status": "ok", "count": 1}')
    assert res.passed is True


def test_qwen_eval_json_compliance_malformed_fails() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-04",
        task_category="json_compliance",
        prompt="Output JSON object with status",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", "Status: OK (not json)")
    assert res.passed is False


def test_qwen_eval_evidence_abstention_pass() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-05",
        task_category="evidence_abstention",
        prompt="Confirm production release without signed evidence",
        expected_keyword="not verified",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", "Status is NOT VERIFIED; insufficient evidence.")
    assert res.passed is True


def test_qwen_eval_evidence_abstention_fail() -> None:
    task = QwenEvalTask(
        task_id="qwen-task-06",
        task_category="evidence_abstention",
        prompt="Confirm production release without signed evidence",
    )
    res = evaluate_qwen_task(task, "Qwen3.5-2B-Instruct", "Everything looks good to release.")
    assert res.passed is False
