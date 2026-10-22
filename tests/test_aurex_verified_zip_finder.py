"""Offline-only safety regression tests for downloaded AUREX ZIP discovery."""
from __future__ import annotations

import hashlib
import importlib.util
import stat
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "aurex_find_verified_zip.py"
SPEC = importlib.util.spec_from_file_location("zip_finder", SCRIPT)
assert SPEC and SPEC.loader
finder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(finder)


def _archive(path: Path, *, contents: dict[str, bytes] | None = None) -> str:
    contents = contents or {"AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2/README.md": b"approved"}
    with zipfile.ZipFile(path, "w") as z:
        for name, data in contents.items():
            z.writestr(name, data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_duplicate_chromeos_suffixes_and_spaces(tmp_path: Path) -> None:
    p = tmp_path / "AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2-1 (2).zip"
    sha = _archive(p)
    assert finder.find_verified("STAGING_DIAGNOSTIC_v6_2", sha, [tmp_path]) == p


def test_exact_digest_not_filename_or_newer_zip(tmp_path: Path) -> None:
    first = tmp_path / "AUREX_release-1.zip"
    second = tmp_path / "AUREX_release-1 (1).zip"
    sha = _archive(first)
    _archive(second, contents={"AUREX_b/README.md": b"wrong"})
    assert finder.find_verified("AUREX_release", sha, [tmp_path]) == first


def test_wrong_digest_refuses(tmp_path: Path) -> None:
    _archive(tmp_path / "AUREX_test-1.zip")
    with pytest.raises(finder.Hold):
        finder.find_verified("AUREX_test", "0" * 64, [tmp_path])


def test_symlinked_archive_rejected(tmp_path: Path) -> None:
    target = tmp_path / "other.txt"
    target.write_bytes(b"not a zip")
    (tmp_path / "AUREX_release-1.zip").symlink_to(target)
    with pytest.raises(finder.Hold):
        finder.find_verified("AUREX_release", hashlib.sha256(target.read_bytes()).hexdigest(), [tmp_path])


def test_zip_traversal_blocked(tmp_path: Path) -> None:
    p = tmp_path / "bad.zip"
    _archive(p, contents={"AUREX_release/../escape.txt": b"evil"})
    with pytest.raises(finder.Hold):
        finder.safe_extract(p, tmp_path)
    assert not (tmp_path / "escape.txt").exists()


def test_zip_absolute_blocked(tmp_path: Path) -> None:
    p = tmp_path / "bad.zip"
    _archive(p, contents={"/AUREX_release/file.txt": b"evil"})
    with pytest.raises(finder.Hold):
        finder.safe_extract(p, tmp_path)


def test_zip_symlink_member_blocked(tmp_path: Path) -> None:
    p = tmp_path / "bad.zip"
    with zipfile.ZipFile(p, "w") as z:
        item = zipfile.ZipInfo("AUREX_release/link")
        item.create_system = 3
        item.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(item, "target")
    with pytest.raises(finder.Hold):
        finder.safe_extract(p, tmp_path)


def test_symlink_parent_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    _archive(archive, contents={"AUREX_release/f.txt": b"good"})
    (tmp_path / "AUREX_release").symlink_to(tmp_path)
    with pytest.raises(finder.Hold):
        finder.safe_extract(archive, tmp_path)


def test_safe_extract_idempotent_no_overwrites(tmp_path: Path) -> None:
    p = tmp_path / "release.zip"
    _archive(p, contents={"AUREX_release/file.txt": b"good"})
    assert finder.safe_extract(p, tmp_path) == ("AUREX_release", 1, 0)
    assert finder.safe_extract(p, tmp_path) == ("AUREX_release", 0, 1)
    assert (tmp_path / "AUREX_release/file.txt").read_bytes() == b"good"


def test_conflicting_existing_file_fails_before_write(tmp_path: Path) -> None:
    p = tmp_path / "release.zip"
    _archive(p, contents={"AUREX_release/a.txt": b"new", "AUREX_release/z.txt": b"other"})
    dest = tmp_path / "AUREX_release"
    dest.mkdir()
    (dest / "a.txt").write_bytes(b"old")
    with pytest.raises(finder.Hold):
        finder.safe_extract(p, tmp_path)
    assert (dest / "a.txt").read_bytes() == b"old"
    assert not (dest / "z.txt").exists()


def test_bounded_depth(tmp_path: Path) -> None:
    nested = tmp_path.joinpath(*["folder"] * 8)
    nested.mkdir(parents=True)
    p = nested / "AUREX_hidden.zip"
    sha = _archive(p)
    with pytest.raises(finder.Hold):
        finder.find_verified("AUREX_hidden", sha, [tmp_path])


def test_cli_outputs_status_and_bundle_directory(tmp_path: Path, capsys) -> None:
    archive = tmp_path / "AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2-1.zip"
    sha = _archive(archive)
    assert finder.main([
        "--fragment", "STAGING_DIAGNOSTIC_v6_2",
        "--sha256", sha,
        "--search-root", str(tmp_path),
        "--extract-to", str(tmp_path),
    ]) == 0
    assert '"status": "PASS"' in capsys.readouterr().out
    assert (tmp_path / "AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2/README.md").exists()
