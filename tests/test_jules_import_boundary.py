"""The Jules recovery gate rejects diffs that rewrite current safeguards."""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "jules_import_boundary.py"
_SPEC = importlib.util.spec_from_file_location("jules_import_boundary", _SCRIPT)
assert _SPEC and _SPEC.loader
boundary = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(boundary)


def test_deleting_safeguards_is_rejected_and_a_new_file_is_only_reviewable() -> None:
    rejected = boundary.review_name_status(
        "D\taurex/egress.py\nD\taurex/evidence_kernel.py\nA\taurex/dispater_pipeline.py\n"
    )
    assert rejected["decision"] == "REJECTED"
    assert rejected["auto_merge"] is False
    assert "D aurex/egress.py" in rejected["protected_changes"]
    review = boundary.review_name_status("A\tdocs/operations/EXAMPLE.json\n")
    assert review["decision"] == "ACCEPTABLE_FOR_REVIEW"
    assert review["auto_merge"] is False
