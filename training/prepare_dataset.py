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


def token_set(text):
    return set(re.findall(r"\w+", text.casefold()))


def jaccard(left, right):
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


SECRET_TEXT = re.compile(
    r"(bearer\s+\S+|api[_-]?key\s*[:=]|password\s*[:=]|sk-[A-Za-z0-9]{8,})",
    re.IGNORECASE,
)


def validate_receipt(receipt, train_path, eval_path, author):
    """A receipt binds a reviewer to these bytes. It does not prove the license."""
    required = ("reviewer", "decision", "train_sha256", "eval_sha256")
    if any(not isinstance(receipt.get(key), str) or not receipt[key].strip() for key in required):
        raise ValueError("approval receipt is incomplete")
    reviewer = receipt["reviewer"].strip()
    if reviewer == author.strip() or reviewer.startswith("model:"):
        raise ValueError("dataset approval requires a different human reviewer")
    if receipt["decision"] != "APPROVED_FOR_TRAINING":
        raise ValueError("dataset is not approved for training")
    if receipt.get("legal_license_authentication") == "VERIFIED":
        raise ValueError("a receipt cannot declare the license independently verified")
    if receipt["train_sha256"] != sha(train_path) or receipt["eval_sha256"] != sha(eval_path):
        raise ValueError("approval receipt does not match these files")
    return reviewer


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
            if SECRET_TEXT.search(m["content"]):
                raise ValueError("Secret or credential text is not training data")
        start = 1 if roles[0] == "system" else 0
        if roles[start:] != ["user", "assistant"] * ((len(roles) - start) // 2):
            raise ValueError("Require alternating user/assistant turns, optional leading system")
        if len(roles) - start < 2:
            raise ValueError("Missing assistant target")
        rows.append(row)
    if not rows:
        raise ValueError("Empty dataset")
    return rows


def prepare(train_path, eval_path, provenance_path, output, receipt_path=None, test_path=None):
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
    if test_path is not None:
        test_path = Path(test_path)
        rows["test"] = read_rows(test_path)
    seen = []
    for split, values in rows.items():
        for index, row in enumerate(values):
            prompt = normalized(
                " ".join(m["content"] for m in row["messages"] if m["role"] != "assistant")
            )
            target = normalized(
                " ".join(m["content"] for m in row["messages"] if m["role"] == "assistant")
            )
            prompt_tokens = token_set(prompt)
            for old_split, old_index, old_prompt, old_target, old_tokens in seen:
                similar = (
                    prompt == old_prompt
                    or SequenceMatcher(None, prompt, old_prompt).ratio() >= 0.9
                    or jaccard(prompt_tokens, old_tokens) >= 0.8
                )
                if similar:
                    reason = (
                        "contradictory targets"
                        if target != old_target
                        else "duplicate or near-duplicate"
                    )
                    raise ValueError(f"{reason}: {old_split}[{old_index}] and {split}[{index}]")
            seen.append((split, index, prompt, target, prompt_tokens))
    approval = "UNREVIEWED"
    if receipt_path is not None:
        receipt_path = Path(receipt_path)
        receipt = json.loads(receipt_path.read_text())
        validate_receipt(receipt, train_path, eval_path, provenance["author"])
        approval = "APPROVED_FOR_TRAINING"
    else:
        receipt = None
    output.mkdir(parents=True)
    copies = [
        (train_path, "train.jsonl"),
        (eval_path, "eval.jsonl"),
        (provenance_path, "provenance.json"),
    ]
    if test_path is not None:
        copies.append((test_path, "test.jsonl"))
    if receipt_path is not None:
        copies.append((receipt_path, "approval-receipt.json"))
    for source, name in copies:
        shutil.copyfile(source, output / name)
    manifest = {
        "schema_version": 1,
        "counts": {k: len(v) for k, v in rows.items()},
        "files": {name: sha(output / name) for _, name in copies},
        "architecture_review": "NOT VERIFIED",
        "semantic_leakage_review": "SCREENED_NOT_PROVEN",
        "legal_license_authentication": "NOT_VERIFIED",
        "training_approval": approval,
        "reviewer": None if receipt is None else receipt["reviewer"],
        "provenance": provenance,
        "near_duplicate_threshold": 0.9,
        "token_jaccard_threshold": 0.8,
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
