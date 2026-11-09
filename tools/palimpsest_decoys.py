"""Bounded, inert PALIMPSEST decoy fixture generation.

Decoys are never imported or executed by AUREX. No network, subprocess,
filesystem traversal, dynamic execution, or security-authority claims.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

MAX_FILES = 16
MAX_BYTES = 32768


def generate_decoys(destination: Path, *, count: int = 4, seed: str = "palimpsest-v1") -> list[Path]:
    """Write a finite set of inert Python data fixtures into a new directory."""
    if not 1 <= count <= MAX_FILES:
        raise ValueError("count must be between 1 and 16")
    if not seed or len(seed) > 128:
        raise ValueError("seed must contain 1..128 characters")
    if destination.is_symlink() or destination.exists():
        raise FileExistsError("destination must not exist (symlinks refused)")
    destination.mkdir(parents=True, exist_ok=False)
    paths: list[Path] = []
    total = 0
    for index in range(count):
        token = hashlib.sha256(f"{seed}:{index}".encode()).hexdigest()[:20]
        content = (
            '"""INERT DECOY FIXTURE — NOT A SECURITY CONTROL OR EXECUTABLE WORKER."""\n'
            f"DECOY_ID = {token!r}\n"
            f"SEQUENCE = {tuple(int(c, 16) for c in token[:8])!r}\n"
            'VERIFICATION = "NOT VERIFIED"\n'
        )
        total += len(content.encode("utf-8"))
        if total > MAX_BYTES:
            raise ValueError("decoy output exceeds maximum bytes")
        path = destination / f"fixture_{index:02d}.py"
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate bounded inert decoy fixtures")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--seed", default="palimpsest-v1")
    args = parser.parse_args()
    for path in generate_decoys(args.destination, count=args.count, seed=args.seed):
        print(path)


if __name__ == "__main__":
    main()
