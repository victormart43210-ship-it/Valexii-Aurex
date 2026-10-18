"""XCVI: only local, bounded text/UTF-8 files reach symbolic engines."""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from workstation.huruf_llull_cli import read_local_text, analyze_file, main


def test_cli_reads_document_and_ast_without_running_source(tmp_path: Path):
    doc = tmp_path / "test.md"
    doc.write_text("alpha omega alpha", encoding="utf-8")
    assert analyze_file(path=doc, mode="document")["status"] == "STRUCTURAL_PROFILE_ONLY"
    script = tmp_path / "sample.py"
    script.write_text("def abc():\n    return 1\n", encoding="utf-8")
    assert analyze_file(path=script, mode="python")["status"] == "STATIC_AST_ONLY"


def test_cli_refuses_pdf_binary_and_symlink(tmp_path: Path):
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    with pytest.raises(ValueError):
        read_local_text(pdf)
    file = tmp_path / "a.txt"
    file.write_text("test", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(file)
    with pytest.raises(ValueError):
        read_local_text(link)


def test_cli_refuses_invalid_utf8_and_oversized(tmp_path: Path):
    file = tmp_path / "bad.txt"
    file.write_bytes(b"\xff")
    with pytest.raises(ValueError):
        read_local_text(file)
    file.write_bytes(b"a" * 65537)
    with pytest.raises(ValueError):
        read_local_text(file)


def test_cli_wheel_has_no_file_or_model_inference(capsys):
    assert main(["--mode", "llull", "--wheel-offsets", "1", "2", "3"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["figure"] == "MODERN_9_POSITION_THREE_RING_ANALOGUE"
    assert r["authority"] == "NONE"


def test_cli_plain_document_is_content_addressed_without_echo(tmp_path: Path, capsys):
    file = tmp_path / "sample.md"
    file.write_text("symbol symbol mystery", encoding="utf-8")
    assert main(["--mode", "document", "--file", str(file)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data["source_sha256"]) == 64
    assert "symbol symbol mystery" not in json.dumps(data)


def test_cli_code_requires_python_extension(tmp_path: Path):
    file = tmp_path / "script.txt"
    file.write_text("print(1)", encoding="utf-8")
    with pytest.raises(ValueError):
        analyze_file(path=file, mode="python")


def test_cli_crosswalk_combines_methods_but_not_historical_claims(tmp_path: Path, capsys):
    file = tmp_path / "sample.txt"
    file.write_text("abracadabra", encoding="utf-8")
    assert main(["--mode", "crosswalk", "--file", str(file)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "MULTI_METHOD_HYPOTHESIS_ONLY"
    assert result["analysis"]["abjad_status"] == "NOT_RUN"
    assert len(result["analysis"]["llull_wheel"]["combinations"]) == 9
