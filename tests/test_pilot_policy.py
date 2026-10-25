from aurex.integrations.pilot_policy import review_synthetic_pilot


def test_fail_closed_by_default():
    assert not review_synthetic_pilot(
        synthetic=True, explicit_operator_approval=True, policy_response=None
    ).permitted_for_review


def test_no_non_synthetic_inputs():
    assert not review_synthetic_pilot(
        synthetic=False,
        explicit_operator_approval=True,
        policy_response={"result": {"allow": True}},
    ).permitted_for_review


def test_no_operator_approval():
    assert not review_synthetic_pilot(
        synthetic=True,
        explicit_operator_approval=False,
        policy_response={"result": {"allow": True}},
    ).permitted_for_review


def test_malformed_opa_response():
    for response in ({}, {"result": True}, {"result": {"allow": 1}}, {"result": {"allow": "true"}}):
        assert not review_synthetic_pilot(
            synthetic=True, explicit_operator_approval=True, policy_response=response
        ).permitted_for_review


def test_policy_pass_is_not_authority():
    decision = review_synthetic_pilot(
        synthetic=True,
        explicit_operator_approval=True,
        policy_response={"result": {"allow": True}},
    )
    assert decision.permitted_for_review
    assert decision.authority == "NONE"
