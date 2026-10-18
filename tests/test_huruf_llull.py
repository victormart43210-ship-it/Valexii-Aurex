"""XCVI: offline deterministic historical/combinatorial static-research checks."""
import json
import pytest

from aurex.huruf_llull import (
    ABJAD_MAP, abjad_calculate, caesar_candidates, caesar_transform,
    combined_research, inspect_python, llull_wheel, profile_document,
)


def test_abjad_classical_table_28_letters():
    assert len(ABJAD_MAP) == 28
    assert list(ABJAD_MAP.values()) == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60,
        70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
    ]


def test_abjad_known_positive_control_not_translation():
    result = abjad_calculate("اب")
    assert result["analysis"]["total"] == 3
    assert result["status"] == "CALCULATION_ONLY"
    assert result["authority"] == "NONE"
    assert result["decipherment"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("text", ["پ", "اچ", "آب", "Latin", "🜂"])
def test_abjad_unknown_characters_fail_closed(text):
    result = abjad_calculate(text)
    assert result["status"].startswith("HOLD")
    assert result["analysis"]["total"] is None


def test_abjad_orthography_opt_in_not_silent():
    strict = abjad_calculate("آب")
    normalized = abjad_calculate("آب", normalize_alef=True)
    assert strict["status"] == "HOLD_UNMAPPED_CHARACTERS"
    assert normalized["analysis"]["total"] == 3
    assert normalized["source_sha256"] == strict["source_sha256"]


def test_llull_wheel_9_positions_with_three_contexts():
    result = llull_wheel()
    assert len(result["combinations"]) == 9
    assert result["combinations"][0] == {
        "letters": "BCD", "terms": ["goodness", "concordance", "of what"],
    }
    assert result["figure"] == "MODERN_9_POSITION_THREE_RING_ANALOGUE"
    assert result["decipherment"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("offsets", [(1, 9, 2), (-1, 0, 1), (True, 1, 2), (1, 2)])
def test_bad_wheel_offsets_hold(offsets):
    with pytest.raises(ValueError):
        llull_wheel(offsets=offsets)


def test_unknown_llull_domain_rejected():
    with pytest.raises(ValueError):
        llull_wheel(domains=("cybersecurity", "relation", "question"))


def test_suffix_first_does_not_reverse_document():
    result = profile_document("alpha beta alpha omega gamma delta omega")
    assert result["analysis"]["token_count"] == 7
    assert result["analysis"]["unique_tokens"] == 5
    assert result["analysis"]["reading_order"] == "UNCHANGED_SUFFIX_ANALYZED_FROM_RIGHT_EDGE"
    assert result["analysis"]["test_limitations"].startswith("single deterministic")
    assert "alpha beta" not in json.dumps(result)


def test_suffix_null_deterministic():
    t = "one two there here were here three"
    assert profile_document(t) == profile_document(t)


@pytest.mark.parametrize("width", [0, 4, True])
def test_invalid_suffix_width_rejected(width):
    with pytest.raises(ValueError):
        profile_document("sample", suffix_width=width)


def test_oversized_and_binary_rejected():
    with pytest.raises(ValueError):
        profile_document("x" * 70000)
    with pytest.raises(ValueError):
        inspect_python("print('hello')\x00")


def test_known_caesar_positive_control_and_no_unkeyed_plaintext():
    plaintext = "HELLO WORLD"
    encrypted = caesar_transform(plaintext, 3, decode=False)
    assert encrypted == "KHOOR ZRUOG"
    assert caesar_transform(encrypted, 3) == plaintext
    result = caesar_candidates(encrypted)
    assert result["status"] == "CANDIDATES_ONLY_NO_KEY"
    assert len(result["analysis"]["candidates"]) == 26
    assert plaintext not in json.dumps(result)
    assert result["analysis"]["candidate_selection"] == "NONE_NO_CLAIM_OF_PLAINTEXT"


@pytest.mark.parametrize("shift", [-1, 26, True])
def test_invalid_caesar_shift(shift):
    with pytest.raises(ValueError):
        caesar_transform("abc", shift)


def test_python_ast_only_no_code_execution(monkeypatch):
    import subprocess
    monkeypatch.setattr(
        subprocess, "run",
        lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("EXECUTED SOURCE")),
    )
    source = 'import os\n\ndef alpha():\n    return eval("1+2")\nclass C:\n    pass\n'
    result = inspect_python(source)
    assert result["status"] == "STATIC_AST_ONLY"
    assert result["analysis"]["functions"] == ("alpha",)
    assert result["analysis"]["classes"] == ("C",)
    assert "os" in result["analysis"]["imports"]
    assert "eval" in result["analysis"]["potentially_sensitive_call_patterns"]
    assert "VULNERABILITY_VERDICT" in result["analysis"]["interpretation"]
    assert result["authority"] == "NONE"


def test_malformed_python_holds():
    assert inspect_python("def f(: pass")["status"] == "HOLD_PARSE_FAILED"


def test_excessively_complex_python_holds():
    assert inspect_python("x = 1\n" * 3000)["status"] == "HOLD_PARSE_FAILED"


def test_crosswalk_has_no_historical_link_or_decipherment():
    result = combined_research("اب")
    assert result["status"] == "MULTI_METHOD_HYPOTHESIS_ONLY"
    assert result["analysis"]["abjad"]["total"] == 3
    assert result["analysis"]["llull_wheel"]["combinations"][0]["letters"] == "BCD"
    assert result["analysis"]["method_relationship"].endswith("NOT_A_HISTORICAL_LINK")
    assert result["decipherment"] == "NOT_ESTABLISHED"


def test_crosswalk_python_static_isolation():
    result = combined_research("def f():\n    return 42\n", kind="python")
    assert result["analysis"]["python_status"] == "STATIC_AST_ONLY"
    assert result["analysis"]["abjad_status"] == "NOT_RUN"
    assert result["authority"] == "NONE"


def test_crosswalk_invalid_python_holds_subcomponent():
    assert combined_research("def f(: pass", kind="python")["analysis"]["python_status"] == "HOLD_PARSE_FAILED"
