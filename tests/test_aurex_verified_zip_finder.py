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


def test_cli_rejects_archive_replaced_after_discovery(tmp_path: Path, monkeypatch, capsys) -> None:
    archive = tmp_path / "AUREX_release.zip"
    sha = _archive(archive)
    original = finder.find_verified

    def replace_after_find(*args):
        found = original(*args)
        replacement = tmp_path / "replacement.zip"
        _archive(replacement, contents={"AUREX_release/replacement.txt": b"not verified"})
        replacement.replace(found)
        return found

    monkeypatch.setattr(finder, "find_verified", replace_after_find)
    assert finder.main([
        "--fragment", "AUREX_release", "--sha256", sha,
        "--search-root", str(tmp_path), "--extract-to", str(tmp_path),
    ]) == 2
    assert '"status": "HOLD"' in capsys.readouterr().out
    assert not (tmp_path / "AUREX_release").exists()


def test_file_directory_conflict_is_rejected_before_output(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    _archive(archive, contents={
        "AUREX_release/first.txt": b"first",
        "AUREX_release/node": b"file",
        "AUREX_release/node/child": b"child",
    })
    with pytest.raises(finder.Hold, match="conflicts with a parent"):
        finder.safe_extract(archive, tmp_path)
    assert not (tmp_path / "AUREX_release").exists()


def test_replaced_parent_cannot_redirect_new_file(tmp_path: Path, monkeypatch) -> None:
    archive = tmp_path / "release.zip"
    _archive(archive, contents={"AUREX_release/file.txt": b"approved"})
    outside = tmp_path / "outside"
    outside.mkdir()
    real_open = finder.os.open

    def replace_parent(path, flags, mode=0o777, *, dir_fd=None):
        if path == "file.txt" and flags & finder.os.O_CREAT:
            parent = tmp_path / "AUREX_release"
            parent.rename(tmp_path / "original")
            parent.symlink_to(outside)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(finder.os, "open", replace_parent)
    with pytest.raises(finder.Hold):
        finder.safe_extract(archive, tmp_path)
    assert not (outside / "file.txt").exists()
    assert not (tmp_path / "original/file.txt").exists()


def test_skipped_file_replaced_during_extraction_holds(tmp_path: Path, monkeypatch) -> None:
    archive = tmp_path / "release.zip"
    _archive(archive, contents={"AUREX_release/old": b"approved", "AUREX_release/new": b"new"})
    directory = tmp_path / "AUREX_release"
    directory.mkdir()
    old = directory / "old"
    old.write_bytes(b"approved")
    real_open = finder.os.open

    def replace_existing(path, flags, mode=0o777, *, dir_fd=None):
        if path == "new" and flags & finder.os.O_CREAT:
            old.write_bytes(b"changed")
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(finder.os, "open", replace_existing)
    with pytest.raises(finder.Hold, match="output changed"):
        finder.safe_extract(archive, tmp_path)
