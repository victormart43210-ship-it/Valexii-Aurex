"""Kernel checks whose expected values are written here, not copied from the engine."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from aurex.ascendancy.adversarial import corrupt_decimal, independence_challenge
from aurex.ascendancy.constraints import (
    ClaimedTotal,
    IdentityConstraint,
    SumConstraint,
    evaluate_constraints,
)
from aurex.ascendancy.graph import corroboration
from aurex.ascendancy.hypothesis import Hypothesis, score_hypotheses
from aurex.ascendancy.manuscript_adapter import (
    HOLDOUT,
    TRAIN,
    hypotheses,
    kite_rule,
    memorize_train,
    unlabeled_status,
)
from aurex.ascendancy.provenance import registry
from aurex.ascendancy.reproducible import computation_manifest
from aurex.ascendancy.temporal import IntervalRecord, covering
from aurex.evidence_kernel import EvidenceGraph, EvidenceRecord

NOW = datetime(2026, 11, 6, tzinfo=UTC)


def _record(eid: str, source: str, parents: tuple[str, ...] = ()) -> EvidenceRecord:
    return EvidenceRecord(eid, "tenant-asc", "doc", source, "ab" * 32, NOW, parents=parents)


def test_shared_document_is_one_root_and_the_baseline_overcounts() -> None:
    graph = EvidenceGraph(
        "tenant-asc",
        [
            _record("pdf", "ticket-1"),
            _record("ocr", "ticket-1-ocr", ("pdf",)),
            _record("row", "ticket-1-row", ("ocr",)),
        ],
    )
    report = corroboration(graph, ("pdf", "ocr", "row"))
    assert report.independent_roots == 1
    assert report.baseline_record_count == 3
    assert report.baseline_overcount == 2
    assert report.shared_ancestry is True
    challenge = independence_challenge(graph, ("pdf", "ocr", "row"), required_roots=2)
    assert challenge.survived is False


def test_complexity_penalty_rejects_the_memorizer() -> None:
    labeled = ((("A",), True), (("B",), False), (("C",), False))
    chosen = score_hypotheses(
        (
            Hypothesis("short", 1, lambda sequence: sequence == ("A",)),
            Hypothesis("memorize", 3, lambda sequence: sequence == ("A",)),
        ),
        labeled,
        penalty=True,
    )
    assert chosen[0].hypothesis_id == "short"
    assert chosen[0].score > chosen[1].score


def test_constraints_catch_a_cent_and_a_conflicting_total() -> None:
    original = Decimal("40.00")
    corrupted = corrupt_decimal(original)
    intact = evaluate_constraints(
        sums=(SumConstraint("cash", (original, Decimal("60.00")), Decimal("100.00")),)
    )
    broken = evaluate_constraints(
        sums=(SumConstraint("cash", (corrupted, Decimal("60.00")), Decimal("100.00")),),
        identities=(IdentityConstraint("job", "J1", "OTHER"),),
        claims=(
            ClaimedTotal("I1", Decimal("100.00")),
            ClaimedTotal("I1", Decimal("90.00")),
        ),
    )
    assert intact.satisfied is True
    assert broken.satisfied is False
    assert broken.violations == ("cash", "job")
    assert broken.contradictions == ("I1",)


def test_successor_retires_only_the_named_predecessor() -> None:
    history = (
        IntervalRecord("R-OLD", date(2026, 1, 1), date(2026, 12, 31)),
        IntervalRecord("R-NEW", date(2026, 3, 1), date(2026, 12, 31), supersedes="R-OLD"),
        IntervalRecord("R-OTHER", date(2026, 1, 1), date(2026, 12, 31)),
    )
    assert covering(history, date(2026, 1, 15)) == ("R-OLD", "R-OTHER")
    assert covering(history, date(2026, 4, 15)) == ("R-NEW", "R-OTHER")
    assert any(row.record_id == "R-OLD" for row in history)


def test_manifest_is_stable_and_changes_when_money_changes() -> None:
    first = computation_manifest("audit", {"amount": "100.00"}, {"exposure": "10.00"})
    second = computation_manifest("audit", {"amount": "100.00"}, {"exposure": "10.00"})
    changed = computation_manifest("audit", {"amount": "100.01"}, {"exposure": "10.00"})
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["manifest_sha256"] != changed["manifest_sha256"]
    assert first["financial_authority"] == "NONE"


def test_calibration_language_holdout_and_unpublished_scripts() -> None:
    penalized = score_hypotheses(hypotheses(), TRAIN, penalty=True)
    unpenalized = score_hypotheses(hypotheses(), TRAIN, penalty=False)
    assert penalized[0].hypothesis_id == "kite-rule"
    assert unpenalized[0].hypothesis_id == "memorize-train"
    holdout_rule = sum(kite_rule(sequence) is label for sequence, label in HOLDOUT)
    holdout_memory = sum(memorize_train(sequence) is label for sequence, label in HOLDOUT)
    assert (holdout_rule, len(HOLDOUT)) == (4, 4)
    assert (holdout_memory, len(HOLDOUT)) == (2, 4)
    for corpus in ("Voynich", "Linear A", "Rongorongo"):
        status = unlabeled_status(corpus)
        assert status["status"] == "NOT_EVALUATED"
        assert status["decipherment_claimed"] is False
    assert unlabeled_status("synthetic-unlabeled")["status"] == "INSUFFICIENT_EVIDENCE"
    assert any(row.classification == "UNVERIFIED_CLAIM" and row.algorithm_id == "ancient-decipherment" for row in registry())
