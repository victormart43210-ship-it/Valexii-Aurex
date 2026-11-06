from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from aurex.evidence_integrity import (
    EvidenceAssessment,
    EvidenceGraph,
    EvidenceNode,
    EvidenceState,
    Qualification,
    TrustedCallerContext,
    evaluate_capability,
    evaluate_evidence,
    stripped_cross_domain_candidate,
)
from aurex.provenance import sha256_hex

NOW = datetime(2026, 11, 5, tzinfo=UTC)


def node(name: str, parents: tuple[str, ...] = (), *, content: str | None = None,
         tenant: str = "t", domain: str = "finance",
         observed: datetime | None = NOW, expiry: datetime | None = None,
         claimed: Qualification = Qualification.OBSERVATION) -> EvidenceNode:
    return EvidenceNode(node_id=name, tenant_id=tenant, domain=domain,
                        content_digest=sha256_hex((content or name).encode()),
                        parent_ids=parents, observed_at=observed, expires_at=expiry,
                        claimed_qualification=claimed)


def assess(nodes: tuple[EvidenceNode, ...], target: str = "end") -> EvidenceAssessment:
    return evaluate_evidence(EvidenceGraph(nodes=nodes), target, tenant_id="t",
                             domain="finance", now=NOW)


@pytest.mark.parametrize("reverse", [False, True])
def test_walks_all_transitive_parents_and_collapses_identical_content(reverse: bool) -> None:
    nodes = (node("a"), node("alias", content="a"), node("b"),
             node("left", ("a", "alias")), node("right", ("b", "a")),
             node("end", ("left", "right", "left")))
    result = assess(tuple(reversed(nodes)) if reverse else nodes)
    assert result.root_digests == tuple(sorted((sha256_hex(b"a"), sha256_hex(b"b"))))
    assert result.structural_root_count == 2
    assert result.state == EvidenceState.PARTIAL
    assert result.qualification == Qualification.CALCULATED
    assert not result.independently_verified


@pytest.mark.parametrize("parents", [("absent",), ("a", "absent"), ("absent", "a")])
def test_any_missing_parent_invalidates_all_roots(parents: tuple[str, ...]) -> None:
    result = assess((node("a"), node("end", parents)))
    assert result.state == EvidenceState.UNAVAILABLE
    assert result.structural_root_count == 0
    assert result.qualification == Qualification.HYPOTHESIS


@pytest.mark.parametrize("nodes", [
    (node("end", ("end",)),),
    (node("a", ("end",)), node("end", ("a",))),
    (node("a"), node("b", ("end",)), node("end", ("a", "b"))),
    (node("a"), node("a", content="different"), node("end", ("a",))),
    (node("a", tenant="other"), node("end", ("a",))),
    (node("a", domain="medicine"), node("end", ("a",))),
])
def test_malformed_and_foreign_lineage_fails_closed(nodes: tuple[EvidenceNode, ...]) -> None:
    result = assess(nodes)
    assert result.state == EvidenceState.DEGRADED
    assert result.structural_root_count == 0
    assert not result.independently_verified


@pytest.mark.parametrize(("observed", "expiry", "expected"), [
    (None, None, EvidenceState.UNKNOWN),
    (NOW.replace(tzinfo=None), None, EvidenceState.UNKNOWN),
    (NOW + timedelta(microseconds=1), None, EvidenceState.UNKNOWN),
    (NOW - timedelta(days=30), None, EvidenceState.STALE),
    (NOW - timedelta(days=29), NOW, EvidenceState.STALE),
    (NOW, NOW.replace(tzinfo=None), EvidenceState.UNKNOWN),
    (NOW, NOW - timedelta(seconds=1), EvidenceState.UNKNOWN),
    (NOW, NOW + timedelta(seconds=1), EvidenceState.PARTIAL),
])
def test_clock_boundaries(observed: datetime | None, expiry: datetime | None,
                          expected: EvidenceState) -> None:
    assert assess((node("end", observed=observed, expiry=expiry),)).state == expected


@pytest.mark.parametrize("label", list(Qualification))
def test_caller_labels_never_promote(label: Qualification) -> None:
    result = assess((node("end", claimed=label),))
    assert result.qualification == Qualification.OBSERVATION
    assert result.state == EvidenceState.PARTIAL
    assert not result.independently_verified


def test_immutable_nested_data_and_strict_inputs() -> None:
    original = node("end")
    with pytest.raises(ValidationError):
        original.node_id = "changed"
    with pytest.raises(ValidationError):
        EvidenceGraph(nodes=[original])  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        EvidenceNode(node_id="a", tenant_id="t", domain="finance", content_digest="claimed")


def test_deep_graph_does_not_depend_on_python_recursion_limit() -> None:
    nodes = tuple(node(str(i), (str(i - 1),) if i else ()) for i in range(1500))
    assert assess(nodes, "1499").structural_root_count == 1


def test_conflict_and_invalid_evaluation_clock() -> None:
    graph = EvidenceGraph(nodes=(node("end"),))
    result = evaluate_evidence(graph, "end", tenant_id="t", domain="finance", now=NOW,
                               conflict=True)
    assert result.state == EvidenceState.HIGH_CONFLICT
    for now, age in [(NOW.replace(tzinfo=None), timedelta(days=1)), (NOW, timedelta(0))]:
        result = evaluate_evidence(graph, "end", tenant_id="t", domain="finance", now=now,
                                   max_age=age)
        assert result.state == EvidenceState.UNKNOWN


@pytest.mark.parametrize("hold", [True, False])
@pytest.mark.parametrize("capability", ["read", "analyze", "export", "pay", "refund", "", "READ"])
def test_capability_allowlist(capability: str, hold: bool) -> None:
    context = TrustedCallerContext(tenant_id="t", domain="finance", authenticated=True,
                                   capabilities=frozenset({capability}), production_hold=hold)
    result = evaluate_capability(capability, context=context, tenant_id="t", domain="finance")
    assert result.permitted == (capability in {"read", "analyze", "export"})


@pytest.mark.parametrize("context", [
    None,
    TrustedCallerContext(tenant_id="t", domain="finance", capabilities=frozenset({"read"})),
    TrustedCallerContext(tenant_id="other", domain="finance", authenticated=True,
                         capabilities=frozenset({"read"})),
    TrustedCallerContext(tenant_id="t", domain="medical", authenticated=True,
                         capabilities=frozenset({"read"})),
    TrustedCallerContext(tenant_id="t", domain="finance", authenticated=True),
])
def test_capability_missing_or_foreign_context(context: TrustedCallerContext | None) -> None:
    assert not evaluate_capability("read", context=context, tenant_id="t",
                                   domain="finance").permitted


def test_cross_domain_candidate_contains_no_source_or_authority() -> None:
    candidate = stripped_cross_domain_candidate(target_domain="medical")
    assert candidate.model_dump() == {"target_domain": "medical",
                                      "qualification": Qualification.HYPOTHESIS,
                                      "state": EvidenceState.UNKNOWN}
