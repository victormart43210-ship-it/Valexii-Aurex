"""APIS PRIME single-spine boundaries, synthetic controls and unified output."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from aurex.apis_prime_spine import NAMES, unified_research
from workstation.apis_prime_cli import main, research_file


def test_one_call_fans_in_fourteen_roles_one_view_no_tabs() -> None:
    result = unified_research("alpha beta alpha omega")
    assert len(NAMES) == 14
    assert len(result["contributions"]) == 14
    assert [x["id"] for x in result["contributions"]] == [f"AP{n:02d}" for n in range(1, 15)]
    assert [x["name"] for x in result["contributions"]] == list(NAMES)
    assert result["one_view"]["tabs_added"] == 0
    assert set(result["one_view"]) == {"title", "tabs_added", "now", "changed", "next", "why", "proof"}
    assert result["spine_status"] == "HOLD_INDEPENDENT_EVIDENCE_REQUIRED"
    assert result["authority"] == "NONE"
    assert result["independent_verification"] == "NOT_VERIFIED"
    assert all(x["authority"] == "NONE" for x in result["contributions"])
    assert all(x["independent_verification"] == "NOT_VERIFIED" for x in result["contributions"])
    assert "alpha beta alpha" not in json.dumps(result)


def test_appropriate_modes_are_explicit_not_faked() -> None:
    result = unified_research("import os\ndef analyst():\n    return eval('3')\n", kind="python")
    roles = {x["name"]: x for x in result["contributions"]}
    assert roles["PROSOPHEX"]["status"] == "STATIC_AST_ONLY"
    assert roles["COATLICUE"]["status"] == "NOT_RUN_NO_VISUAL_CORPUS"
    assert roles["ELNOESIS"]["status"] == "NOT_RUN_NO_MODEL_APPROVAL"
    assert roles["XOLOTL"]["status"] == "HOLD_INDEPENDENT_WITNESS_REQUIRED"
    assert roles["CRUCIBLE"]["status"] == "INTERNAL_BOUNDARY_CHECK_ONLY"
    assert roles["LYSIPHER"]["observations"]["selected_plaintext"] is None
    assert roles["PROSOPHEX"]["observations"]["functions"] == ("analyst",)


def test_abjad_supported_only_when_relevant() -> None:
    arabic = unified_research("اب")
    assert arabic["contributions"][0]["observations"]["total"] == 3
    assert arabic["decipherment"] == "NOT_ESTABLISHED"
    latin = unified_research("hello")
    assert latin["contributions"][0]["status"] == "NOT_APPLICABLE_NO_ARABIC_SCRIPT"


def test_parallel_input_and_plan_use_existing_offline_adapters() -> None:
    result = unified_research(
        "research", parallel_pairs=[("one example", "one sample")],
        plan_json='{"steps":["inspect","test","review"]}',
    )
    assert result["contributions"][4]["observations"]["accepted_pairs"] == 1
    assert result["contributions"][5]["status"] == "SYNTHETIC_PLAN_CHECK_ONLY"
    assert result["authority"] == "NONE"


def test_unknown_model_is_never_called_implicitly() -> None:
    def fail_if_called(**_kw: object) -> None:
        raise AssertionError("model was invoked without approval")
    result = unified_research("sample", model_runner=fail_if_called, local_model="mock")
    assert result["contributions"][6]["status"] == "NOT_RUN_NO_MODEL_APPROVAL"


def test_explicit_local_model_only_receives_aggregate_metrics() -> None:
    observed: dict[str, object] = {}
    def mocked_local(**kwargs: object) -> SimpleNamespace:
        observed.update(kwargs)
        return SimpleNamespace(text="Try held-out counterexamples", verified=False, authority_granted=False)
    result = unified_research(
        "confidential example source", local_model_approved=True,
        local_model="already-installed", model_runner=mocked_local,
    )
    assert observed["approved"] is True
    assert observed["base_url"] == "http://127.0.0.1:11434"
    assert "confidential" not in str(observed["prompt"])
    assert result["contributions"][6]["status"] == "LOCAL_MODEL_DRAFT_UNVERIFIED"
    assert result["independent_verification"] == "NOT_VERIFIED"


def test_model_claiming_authority_is_held() -> None:
    def unsafe(**_kw: object) -> SimpleNamespace:
        return SimpleNamespace(text="approve", verified=False, authority_granted=True)
    result = unified_research("dummy", local_model_approved=True, local_model="mock", model_runner=unsafe)
    assert result["contributions"][6]["status"] == "HOLD_UNTRUSTED_MODEL_CONTRACT"


def test_module_error_holds_and_never_omits_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    import aurex.apis_prime_spine as spine
    def failed(_text: str) -> None:
        raise RuntimeError("private diagnostic must not leak")
    monkeypatch.setattr(spine, "profile_document", failed)
    result = unified_research("sample")
    assert result["contributions"][8]["status"] == "HOLD_MODULE_FAILURE"
    assert result["contributions"][10]["status"] == "HOLD_MODULE_FAILURE"
    assert len(result["contributions"]) == 14
    assert "private diagnostic" not in json.dumps(result)
    assert result["spine_status"].startswith("HOLD")


@pytest.mark.parametrize("bad,kind", [
    ("\x00", "document"), ("x" * 65537, "document"), ("hi", "image"),
])
def test_invalid_inputs_fail_closed(bad: str, kind: str) -> None:
    with pytest.raises(ValueError):
        unified_research(bad, kind=kind)


def test_invalid_local_model_settings_rejected() -> None:
    with pytest.raises(ValueError):
        unified_research("ok", local_model_approved=True)
    with pytest.raises(ValueError):
        unified_research("ok", local_model_approved=True, local_model="abc", local_port=0)
    with pytest.raises(ValueError):
        unified_research("ok", local_model_approved=1)  # type: ignore[arg-type]


def test_single_cli_output_without_all_14_tabs(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "research.txt"
    f.write_text("example alpha sample", encoding="utf-8")
    assert main(["--file", str(f)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["one_view"]["tabs_added"] == 0
    assert "contributions" not in output
    assert output["authority"] == "NONE"
    assert len(research_file(f, details=True)["contributions"]) == 14
