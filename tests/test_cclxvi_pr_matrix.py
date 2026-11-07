"""The convergence classifier records decisions. It does not merge."""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cclxvi_pr_matrix.py"
_SPEC = importlib.util.spec_from_file_location("cclxvi_pr_matrix", _SCRIPT)
assert _SPEC and _SPEC.loader
_MATRIX = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MATRIX)
CANDIDATE_BASE = _MATRIX.CANDIDATE_BASE
classify = _MATRIX.classify


def test_the_verified_parent_stays_a_stacked_dependency() -> None:
    row = classify(
        {
            "number": 188,
            "head_sha": CANDIDATE_BASE,
            "base_ref": "cursor/kusanagi-cclxii-unified-completion-4082",
            "mergeable": "MERGEABLE",
            "head_in_candidate": True,
            "ci_status": "PASS",
        }
    )
    assert row["acceptance_decision"] == "STACKED_DEPENDENCY"
    assert row["ci_status"] == "PASS"


def test_a_contained_head_is_not_merged_again() -> None:
    row = classify(
        {
            "number": 170,
            "head_sha": "d2e3df77f72f",
            "base_ref": "main",
            "mergeable": "MERGEABLE",
            "head_in_candidate": True,
        }
    )
    assert row["acceptance_decision"] == "SUPERSEDED"


def test_protected_financial_edits_conflict() -> None:
    row = classify(
        {
            "number": 172,
            "head_sha": "a5b9cce016ca",
            "base_ref": "main",
            "mergeable": "MERGEABLE",
            "head_in_candidate": False,
            "protected_changes": ["M aurex/dispater_intelligence.py"],
        }
    )
    assert row["acceptance_decision"] == "CONFLICTING"
    assert row["protected_changes"] == ["M aurex/dispater_intelligence.py"]


def test_an_untested_mainline_pr_needs_the_owner() -> None:
    row = classify(
        {
            "number": 169,
            "head_sha": "324f86050ece",
            "base_ref": "main",
            "mergeable": "MERGEABLE",
            "head_in_candidate": False,
        }
    )
    assert row["acceptance_decision"] == "NEEDS_OWNER_DECISION"
    assert row["ci_status"] == "NOT_RECHECKED"


def test_a_github_conflict_is_left_open() -> None:
    row = classify(
        {
            "number": 3,
            "head_sha": "3c994b1bf471",
            "base_ref": "main",
            "mergeable": "CONFLICTING",
            "head_in_candidate": False,
        }
    )
    assert row["acceptance_decision"] == "CONFLICTING"
