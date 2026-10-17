"""Non-financial, synthetic tests for source-only Chromebook integration intake."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.financial_source_preflight import (
    REQUIRED_MODULES,
    SOURCE_LIMIT_BYTES,
    inspect_local_source,
    inspect_source,
)


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in REQUIRED_MODULES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("from __future__ import annotations\nVALUE = 1\n", encoding="utf-8")
    return root


def test_manifest_is_source_only_and_has_sha256(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    result = inspect_local_source(root)
    assert result["status"] == "PASS_SOURCE_INVENTORY_ONLY"
    assert result["required_ok"] is True
    assert result["source_file_count"] == len(REQUIRED_MODULES)
    assert len(result["report_sha256"]) == 64
    assert all(e["status"] == "PASS" for e in result["entries"])
    before = (root / REQUIRED_MODULES[0]).read_bytes()
    expected = hashlib.sha256(before).hexdigest()
    assert result["entries"][0]["sha256"] == expected
    assert result["production_integration"] == "NOT VERIFIED"
    assert result["authority"] == "NONE"


@pytest.mark.parametrize("missing", REQUIRED_MODULES)
def test_missing_required_module_holds(tmp_path: Path, missing: str) -> None:
    root = make_repo(tmp_path)
    (root / missing).unlink()
    report = inspect_local_source(root)
    assert report["status"] == "HOLD"
    assert report["required_ok"] is False
    assert any(e["path"] == missing and e["status"] == "HOLD" for e in report["entries"])


def test_syntax_error_holds(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / REQUIRED_MODULES[0]).write_text("def broken(:\n")
    report = inspect_local_source(root)
    assert report["status"] == "HOLD"
    assert any("syntax-invalid" in e.get("reason", "") for e in report["entries"])


def test_file_size_bound_prevents_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_repo(tmp_path)
    target = root / REQUIRED_MODULES[0]
    target.write_bytes(b"x" * (SOURCE_LIMIT_BYTES + 1))
    original = Path.read_bytes

    def guarded_read(path: Path) -> bytes:
        if path == target:
            raise AssertionError("Oversized code should never be read")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    report = inspect_local_source(root)
    assert report["status"] == "HOLD"


def test_symlinked_module_is_not_read(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    outside = tmp_path / "external_private_document.py"
    outside.write_text('PRIVATE = "not to read"\n')
    target = root / REQUIRED_MODULES[0]
    target.unlink()
    target.symlink_to(outside)
    report = inspect_local_source(root)
    assert report["status"] == "HOLD"
    assert "PRIVATE" not in json.dumps(report)
    assert report["entries"][0]["reason"] == "Non-source or unsafe symlink/path"


def test_optional_safe_source_and_tests_are_inventoried(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    extra = root / "aurex/financial/pdf_reconcile.py"
    extra.write_text("A = 42\n")
    tests = root / "tests/test_financial_synthetic.py"
    tests.parent.mkdir()
    tests.write_text("def test_synthetic(): assert True\n")
    report = inspect_local_source(root)
    assert report["source_file_count"] == len(REQUIRED_MODULES) + 2
    assert report["status"] == "PASS_SOURCE_INVENTORY_ONLY"


def test_usb_contents_never_opened_or_listed(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    usb = tmp_path / "USB DRIVE"
    usb.mkdir()
    secret = usb / "Highly Confidential Invoice 2026.pdf"
    secret.write_bytes(b"REAL_FINANCIAL_RECORD_DO_NOT_UPLOAD")
    result = inspect_local_source(root, usb)
    rendered = json.dumps(result)
    assert result["usb_mount_present"] is True
    assert secret.exists()
    assert secret.read_bytes() == b"REAL_FINANCIAL_RECORD_DO_NOT_UPLOAD"
    assert "Confidential" not in rendered
    assert "REAL_FINANCIAL_RECORD" not in rendered
    assert len(list(usb.iterdir())) == 1


def test_not_a_repository_is_hold(tmp_path: Path) -> None:
    result = inspect_local_source(tmp_path)
    assert result["status"] == "HOLD"
    assert result["authority"] == "NONE"


def test_direct_inspection_rejects_file_outside_source(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("VALUE=7")
    with pytest.raises(ValueError):
        inspect_source(root, outside)
