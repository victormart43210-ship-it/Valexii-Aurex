"""Preserve and validate user-provided chat data; never invent original-data access."""

import argparse
import hashlib
import json
import re
import shutil
from difflib import SequenceMatcher
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def read_rows(path):
    rows = []
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            raise ValueError(f"Blank JSONL record at line {number}")
        row = json.loads(line)
        if not isinstance(row, dict) or set(row) != {"messages"}:
            raise ValueError("Expected messages-only JSONL records")
        messages = row["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("Missing conversation")
        roles = []
        for m in messages:
            if (
                not isinstance(m, dict)
                or set(m) != {"role", "content"}
                or not isinstance(m["content"], str)
                or not m["content"].strip()
            ):
                raise ValueError("Invalid chat message")
            roles.append(m["role"])
            if "hle:3r2s:" in m["content"].lower():
                raise ValueError("Benchmark canary detected; quarantine this source")
        start = 1 if roles[0] == "system" else 0
        if roles[start:] != ["user", "assistant"] * ((len(roles) - start) // 2):
            raise ValueError("Require alternating user/assistant turns, optional leading system")
        if len(roles) - start < 2:
            raise ValueError("Missing assistant target")
        rows.append(row)
    if not rows:
        raise ValueError("Empty dataset")
    return rows


def prepare(train_path, eval_path, provenance_path, output):
    train_path, eval_path, provenance_path, output = map(
        Path, (train_path, eval_path, provenance_path, output)
    )
    if output.exists():
        raise ValueError("Output must be a new directory; preserve previous versions")
    provenance = json.loads(provenance_path.read_text())
    if (
        any(
            not isinstance(provenance.get(k), str) or not provenance[k].strip()
            for k in ("source", "license", "author")
        )
        or provenance.get("benchmark_data") is not False
    ):
        raise ValueError("Explicit original-data provenance and license required")
    rows = {"train": read_rows(train_path), "eval": read_rows(eval_path)}
    seen = []
    for split, values in rows.items():
        for index, row in enumerate(values):
            prompt = normalized(
                " ".join(m["content"] for m in row["messages"] if m["role"] != "assistant")
            )
            target = normalized(
                " ".join(m["content"] for m in row["messages"] if m["role"] == "assistant")
            )
            for old_split, old_index, old_prompt, old_target in seen:
                if prompt == old_prompt or SequenceMatcher(None, prompt, old_prompt).ratio() >= 0.9:
                    reason = (
                        "contradictory targets"
                        if target != old_target
                        else "duplicate or near-duplicate"
                    )
                    raise ValueError(f"{reason}: {old_split}[{old_index}] and {split}[{index}]")
            seen.append((split, index, prompt, target))
    output.mkdir(parents=True)
    for source, name in [
        (train_path, "train.jsonl"),
        (eval_path, "eval.jsonl"),
        (provenance_path, "provenance.json"),
    ]:
        shutil.copyfile(source, output / name)
    manifest = {
        "schema_version": 1,
        "counts": {k: len(v) for k, v in rows.items()},
        "files": {n: sha(output / n) for n in ("train.jsonl", "eval.jsonl", "provenance.json")},
        "architecture_review": "NOT VERIFIED",
        "semantic_leakage_review": "NOT VERIFIED",
        "provenance": provenance,
        "near_duplicate_threshold": 0.9,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser()
    for name in ["train", "eval", "provenance", "output"]:
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prepare(a.train, a.eval, a.provenance, a.output), indent=2))


if __name__ == "__main__":
    main()
