from datetime import date

from aurex.knowledge_trust import (
    PolicyDocument,
    PolicyStatus,
    check_source_independence,
    evaluate_policy_supersession,
)


def test_policy_supersession() -> None:
    doc_a = PolicyDocument(
        doc_id="policy-2022-v1",
        title="Towing Safety Policy 2022",
        effective_date=date(2022, 1, 1),
        superseded_by="policy-2026-v2",
        source_sha256="a" * 64,
    )
    doc_b = PolicyDocument(
        doc_id="policy-2026-v2",
        title="Towing Safety Policy 2026",
        effective_date=date(2026, 1, 1),
        superseded_by=None,
        source_sha256="b" * 64,
    )

    results = evaluate_policy_supersession((doc_a, doc_b), as_of=date(2026, 10, 26))
    res_map = {r.doc_id: r for r in results}

    assert res_map["policy-2022-v1"].status == PolicyStatus.SUPERSEDED
    assert res_map["policy-2022-v1"].can_authorize_current is False
    assert "preserved for historical evidence" in res_map["policy-2022-v1"].explanation

    assert res_map["policy-2026-v2"].status == PolicyStatus.CURRENT
    assert res_map["policy-2026-v2"].can_authorize_current is True


def test_source_independence() -> None:
    # Duplicate digests do not provide independent corroboration
    digests = ("a" * 64, "a" * 64)
    res = check_source_independence(digests)
    assert res["independent_corroboration"] is False
    assert "identical copies do not constitute" in str(res["duplicate_warning"])

    # Unique digests are independent
    unique_digests = ("a" * 64, "b" * 64)
    res_unique = check_source_independence(unique_digests)
    assert res_unique["independent_corroboration"] is True


def test_knowledge_trust_adversarial_and_negative_cases() -> None:
    # Future effective date policy cannot authorize current operations
    future_doc = PolicyDocument(
        doc_id="policy-2030-v1",
        title="Future Fleet Policy 2030",
        effective_date=date(2030, 1, 1),
        source_sha256="f" * 64,
    )
    res = evaluate_policy_supersession((future_doc,), as_of=date(2026, 10, 26))
    assert res[0].status == PolicyStatus.UNVERIFIED
    assert res[0].can_authorize_current is False

    # Ambiguous or non-existent superseded_by ID does not crash or mark as superseded
    invalid_ref_doc = PolicyDocument(
        doc_id="policy-broken-ref",
        title="Broken Ref Policy",
        effective_date=date(2025, 1, 1),
        superseded_by="non-existent-doc-id",
        source_sha256="c" * 64,
    )
    res_broken = evaluate_policy_supersession((invalid_ref_doc,), as_of=date(2026, 10, 26))
    assert res_broken[0].status == PolicyStatus.CURRENT
    assert res_broken[0].can_authorize_current is True
