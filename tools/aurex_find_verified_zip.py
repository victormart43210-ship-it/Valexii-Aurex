"""AUREX XXV: find a downloaded release ZIP by its checksum, not its filename.

Read-only unless --extract-to is explicit. Never runs scripts inside archives.
Downloads renamed by ChromeOS ("-1", " (1)", etc.) are supported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import IO, BinaryIO

MAX_DEPTH = 6
MAX_ENTRIES = 300
MAX_ARCHIVE_BYTES = 150 * 1024 * 1024
MAX_EXPANDED_BYTES = 350 * 1024 * 1024
PRUNE = frozenset({".git", ".cache", ".venv", ".npm", "node_modules", "__pycache__"})


class Hold(Exception):
    """A fail-closed, user-safe archive condition."""


def _hash_stream(stream: IO[bytes], *, limit: int, copy: BinaryIO | None = None) -> str:
    digest = hashlib.sha256()
    total = 0
    while block := stream.read(1024 * 1024):
        total += len(block)
        if total > limit:
            raise Hold("file exceeds allowed size")
        digest.update(block)
        if copy is not None:
            copy.write(block)
    return digest.hexdigest()


def _open_regular(path: str | Path, *, dir_fd: int | None = None) -> BinaryIO:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dir_fd)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Hold("expected a regular file")
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise


def _digest(path: Path) -> str:
    with _open_regular(path) as stream:
        return _hash_stream(stream, limit=MAX_ARCHIVE_BYTES)


def find_verified(fragment: str, expected: str, roots: list[Path]) -> Path:
    """Return first exact-digest, regular, non-symlink ZIP under bounded search roots."""
    if not 6 <= len(fragment) <= 180 or "/" in fragment or "\\" in fragment:
        raise Hold("invalid filename fragment")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise Hold("expected SHA-256 must be 64 lowercase hexadecimal characters")
    examined: set[tuple[int, int]] = set()
    matches: list[Path] = []
    for root in roots:
        root = root.expanduser()
        if not root.is_dir() or root.is_symlink():
            continue
        for directory, subdirs, files in os.walk(root, topdown=True, followlinks=False):
            folder = Path(directory)
            depth = len(folder.relative_to(root).parts)
            subdirs[:] = sorted(
                name for name in subdirs
                if depth < MAX_DEPTH and name not in PRUNE and not (folder / name).is_symlink()
            )
            for name in sorted(files):
                if fragment.casefold() not in name.casefold() or not name.lower().endswith(".zip"):
                    continue
                p = folder / name
                try:
                    st = p.lstat()
                    if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_ARCHIVE_BYTES:
                        continue
                    identity = (st.st_dev, st.st_ino)
                    if identity in examined:
                        continue
                    examined.add(identity)
                    if _digest(p) == expected:
                        matches.append(p)
                except (Hold, OSError):
                    continue
    if not matches:
        raise Hold("no downloaded ZIP matched the provided SHA-256; do not bypass verification")
    return min(matches, key=lambda p: (len(p.parts), len(str(p)), str(p)))


def _valid_members(z: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = z.infolist()
    if not members or len(members) > MAX_ENTRIES:
        raise Hold("ZIP entry count outside safe bounds")
    total = 0
    seen: dict[tuple[str, ...], bool] = {}
    roots: set[str] = set()
    for item in members:
        name = item.filename
        path = PurePosixPath(name)
        if (
            "\\" in name or "\x00" in item.orig_filename or not name or path.is_absolute()
            or any(p in {".", "..", ""} for p in name.rstrip("/").split("/"))
            or len(path.parts) < 2 or path.parts in seen
        ):
            raise Hold("ZIP contains duplicate, absolute or unsafe member names")
        seen[path.parts] = item.is_dir()
        roots.add(path.parts[0])
        mode = item.external_attr >> 16
        if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFDIR, stat.S_IFREG)):
            raise Hold("ZIP contains a symlink or unsafe filesystem object")
        if item.flag_bits & 1:
            raise Hold("ZIP contains encrypted entries")
        if item.file_size > MAX_EXPANDED_BYTES:
            raise Hold("ZIP member exceeds allowed size")
        total += item.file_size
        if total > MAX_EXPANDED_BYTES:
            raise Hold("ZIP expanded size exceeds allowed bound")
    for parts in seen:
        if any(seen.get(parts[:depth]) is False for depth in range(1, len(parts))):
            raise Hold("ZIP file conflicts with a parent directory")
    if len(roots) != 1 or not next(iter(roots)).startswith("AUREX_"):
        raise Hold("ZIP must contain one AUREX release directory")
    if z.testzip() is not None:
        raise Hold("ZIP CRC validation failed")
    return members


@contextmanager
def _directory(
    root: int, parts: tuple[str, ...], *, create: bool = False, private: bool = False,
) -> Iterator[int]:
    current = os.dup(root)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=current)
                except FileExistsError:
                    pass
            try:
                child = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current
                )
            except FileNotFoundError:
                raise
            except OSError as exc:
                raise Hold("unsafe or inaccessible extraction directory") from exc
            os.close(current)
            current = child
            if private:
                _require_private_directory(os.fstat(current))
        yield current
    finally:
        os.close(current)


def _require_private_directory(info: os.stat_result) -> None:
    if info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise Hold("choose an extraction directory owned by you and not writable by others")


def _extract_members(z: zipfile.ZipFile, root: int) -> tuple[str, int, int]:
    members = _valid_members(z)
    pending: list[tuple[zipfile.ZipInfo, tuple[str, ...]]] = []
    matches = 0
    for item in members:
        parts = PurePosixPath(item.filename).parts
        try:
            if item.is_dir():
                with _directory(root, parts, private=True):
                    pass
                continue
            with _directory(root, parts[:-1], private=True) as parent:
                try:
                    with _open_regular(parts[-1], dir_fd=parent) as existing, z.open(item) as source:
                        if (
                            _hash_stream(existing, limit=MAX_EXPANDED_BYTES)
                            != _hash_stream(source, limit=MAX_EXPANDED_BYTES)
                        ):
                            raise Hold("existing file differs; refusing to overwrite")
                except FileNotFoundError:
                    pending.append((item, parts))
                except OSError as exc:
                    raise Hold("unsafe or inaccessible existing file") from exc
                else:
                    matches += 1
        except FileNotFoundError:
            pending.append((item, parts))

    written = 0
    for item, parts in pending:
        if item.is_dir():
            with _directory(root, parts, create=True, private=True):
                pass
            continue
        with _directory(root, parts[:-1], create=True, private=True) as parent:
            fd = os.open(
                parts[-1], os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                0o600, dir_fd=parent,
            )
            try:
                with os.fdopen(fd, "wb") as out, z.open(item) as source:
                    with _directory(root, parts[:-1], private=True) as current:
                        if not os.path.samestat(os.fstat(current), os.fstat(parent)):
                            raise Hold("extraction directory changed during write")
                    while block := source.read(1024 * 1024):
                        out.write(block)
            except BaseException:
                try:
                    os.unlink(parts[-1], dir_fd=parent)
                except OSError:
                    pass
                raise
            written += 1
    # Recheck the visible tree after writes, including any files skipped as identical.
    for item in members:
        parts = PurePosixPath(item.filename).parts
        if item.is_dir():
            with _directory(root, parts, private=True):
                continue
        with _directory(root, parts[:-1], private=True) as parent:
            with _open_regular(parts[-1], dir_fd=parent) as output, z.open(item) as source:
                if (
                    _hash_stream(output, limit=MAX_EXPANDED_BYTES)
                    != _hash_stream(source, limit=MAX_EXPANDED_BYTES)
                ):
                    raise Hold("extraction output changed during verification")
    return PurePosixPath(members[0].filename).parts[0], written, matches


def safe_extract(
    archive: Path, destination: Path, *, expected_sha256: str | None = None,
) -> tuple[str, int, int]:
    """Extract a bounded snapshot into a destination controlled by the caller.

    The final check describes the files at verification time. Keep the output
    directory private before using any extracted file.
    """
    with _open_regular(archive) as source, tempfile.TemporaryFile() as snapshot:
        actual = _hash_stream(source, limit=MAX_ARCHIVE_BYTES, copy=snapshot)
        if expected_sha256 is not None and actual != expected_sha256:
            raise Hold("ZIP changed after discovery; checksum verification failed")
        snapshot.seek(0)
        root = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        try:
            parts = Path(os.path.abspath(destination)).parts[1:]
            with _directory(root, parts) as target, zipfile.ZipFile(snapshot) as z:
                target_stat = os.fstat(target)
                _require_private_directory(target_stat)
                result = _extract_members(z, target)
                with _directory(root, parts) as visible:
                    if not os.path.samestat(os.fstat(visible), target_stat):
                        raise Hold("extraction destination changed during verification")
                return result
        finally:
            os.close(root)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fragment", required=True, help="Stable part of ZIP name, ignoring ChromeOS suffixes")
    p.add_argument("--sha256", required=True, help="Published full-archive SHA-256 checksum")
    p.add_argument("--search-root", action="append", type=Path, help="Explicit search root; repeat as needed")
    p.add_argument("--extract-to", type=Path, help="Extract verified ZIP without overwriting existing files")
    args = p.parse_args(argv)
    try:
        roots = args.search_root or [Path.home(), Path("/mnt/chromeos/MyFiles/Downloads")]
        archive = find_verified(args.fragment, args.sha256, roots)
        root, written, existing = None, 0, 0
        if args.extract_to is not None:
            root, written, existing = safe_extract(archive, args.extract_to.expanduser(), expected_sha256=args.sha256)
        print(json.dumps({
            "status": "PASS", "zipPath": str(archive), "sha256": args.sha256,
            "bundleDirectory": str(args.extract_to.expanduser() / root) if root else None,
            "newFiles": written, "identicalFilesSkipped": existing,
            "authority": "NONE", "release": "HOLD",
        }, sort_keys=True))
        return 0
    except (Hold, OSError, zipfile.BadZipFile) as exc:
        print(json.dumps({
            "status": "HOLD",
            "reason": type(exc).__name__ if not isinstance(exc, Hold) else str(exc),
            "authority": "NONE", "release": "HOLD",
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
