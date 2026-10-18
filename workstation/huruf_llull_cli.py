"""Read-only AUREX HURUF/LLULL research CLI; local user-chosen UTF-8 text only."""
from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any

from aurex.huruf_llull import (
    MAX_TEXT_BYTES, abjad_calculate, caesar_candidates, combined_research,
    inspect_python, llull_wheel, profile_document,
)

TEXT_EXTENSIONS = frozenset({
    ".txt", ".md", ".py", ".csv", ".json", ".tex", ".v", ".xml", ".html",
})


def read_local_text(path: Path) -> str:
    """Never follow symlinks; never parse PDF, DOCX, images or binary data."""
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError("only permitted plain-text extensions are supported")
    # Avoid the check/open symlink race; reject pipes/devices before reading.
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("secure no-follow file opening is unavailable")
    flags = os.O_RDONLY | nofollow | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError("file unavailable or symlink refused") from exc
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("only regular files are supported")
        raw = handle.read(MAX_TEXT_BYTES + 1)
    if len(raw) > MAX_TEXT_BYTES:
        raise ValueError("file too large (64 KiB)")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8; extract/transcribe separately") from exc
    if "\x00" in text:
        raise ValueError("binary input rejected")
    return text


def analyze_file(
    *, path: Path, mode: str, suffix_width: int = 2,
    normalize_alef: bool = False,
) -> dict[str, Any]:
    text = read_local_text(path)
    if mode == "document":
        return profile_document(text, suffix_width=suffix_width)
    if mode == "python":
        if path.suffix.lower() != ".py":
            raise ValueError("Python AST mode requires a .py file")
        return inspect_python(text)
    if mode == "abjad":
        return abjad_calculate(text, normalize_alef=normalize_alef)
    if mode == "caesar":
        return caesar_candidates(text)
    if mode == "crosswalk":
        return combined_research(
            text, kind="python" if path.suffix.lower() == ".py" else "document"
        )
    raise ValueError("unsupported analysis mode")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUREX symbolic document/Python research — offline / $0"
    )
    parser.add_argument(
        "--mode", required=True,
        choices=("document", "python", "abjad", "caesar", "llull", "crosswalk"),
    )
    parser.add_argument("--file", type=Path, help="local plaintext only")
    parser.add_argument("--suffix-width", type=int, default=2)
    parser.add_argument("--normalize-alef", action="store_true")
    parser.add_argument(
        "--wheel-offsets", nargs=3, type=int,
        metavar=("OUTER", "MIDDLE", "INNER"), default=[0, 1, 2],
    )
    args = parser.parse_args(argv)
    try:
        if args.mode == "llull":
            if args.file:
                parser.error("llull wheel needs no source file")
            result = llull_wheel(offsets=(args.wheel_offsets[0], args.wheel_offsets[1], args.wheel_offsets[2]))
        else:
            if args.file is None:
                parser.error("mode requires --file")
            result = analyze_file(
                path=args.file, mode=args.mode,
                suffix_width=args.suffix_width, normalize_alef=args.normalize_alef,
            )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not str(result["status"]).startswith("HOLD") else 2


if __name__ == "__main__":
    raise SystemExit(main())
