"""Shared artifact validation and assistant-only label construction."""

import json
from pathlib import Path

from training.prepare_dataset import read_rows, sha


def verified_data(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    for name in manifest["files"]:
        if Path(name).name != name or sha(directory / name) != manifest["files"][name]:
            raise ValueError("Prepared dataset hash mismatch")
    if manifest.get("training_approval") not in {None, "UNREVIEWED", "APPROVED_FOR_TRAINING"}:
        raise ValueError("Unknown dataset approval state")
    return manifest, read_rows(directory / "train.jsonl"), read_rows(directory / "eval.jsonl")


def encode(row, tokenizer, max_length):
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError("malformed conversation")
    for message in messages:
        if (
            not isinstance(message, dict)
            or set(message) != {"role", "content"}
            or message["role"] not in {"system", "user", "assistant"}
            or not isinstance(message["content"], str)
            or not message["content"].strip()
        ):
            raise ValueError("malformed message")
    tokens = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
    if len(tokens) > max_length:
        raise ValueError("Example exceeds max_length; curate it rather than silently truncating")
    labels = [-100] * len(tokens)
    for i, message in enumerate(messages):
        if message["role"] != "assistant":
            continue
        prefix = tokenizer.apply_chat_template(
            messages[:i], tokenize=True, add_generation_prompt=True
        )
        end = tokenizer.apply_chat_template(
            messages[: i + 1], tokenize=True, add_generation_prompt=False
        )
        if tokens[: len(prefix)] != prefix or tokens[: len(end)] != end:
            raise ValueError("Chat template is not prefix-stable; assistant masking unsupported")
        labels[len(prefix) : len(end)] = tokens[len(prefix) : len(end)]
    if all(x == -100 for x in labels):
        raise ValueError("No supervised assistant tokens")
    return {"input_ids": tokens, "attention_mask": [1] * len(tokens), "labels": labels}


def collator(tokenizer):
    import torch

    def batch(rows):
        width = max(len(r["input_ids"]) for r in rows)
        pads = {"input_ids": tokenizer.pad_token_id, "attention_mask": 0, "labels": -100}
        return {
            k: torch.tensor([r[k] + [pad] * (width - len(r[k])) for r in rows])
            for k, pad in pads.items()
        }

    return batch


def validate_model_config(config):
    import re

    if config["base_model"].lower().endswith(".gguf"):
        raise ValueError("GGUF is an inference artifact, not a trainable checkpoint")
    if not re.fullmatch(r"[0-9a-f]{40}", config.get("revision", "")):
        raise ValueError("Pin an exact 40-character Hugging Face model commit")
    if not 0 < config["max_steps"] <= 10000 or not 1 <= config["max_length"] <= 8192:
        raise ValueError("Invalid training bounds")


def verified_adapter(directory):
    """Check local integrity against the training record, not external authenticity."""
    directory = Path(directory)
    record = json.loads((directory / "training-record.json").read_text())
    hashes = record.get("artifact_sha256", {})
    if not {"adapter_model.safetensors", "adapter_config.json"}.issubset(hashes):
        raise ValueError("Missing adapter integrity manifest")
    for name, expected in hashes.items():
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError("Invalid adapter artifact path")
        artifact = directory / name
        if artifact.is_symlink() or not artifact.is_file() or sha(artifact) != expected:
            raise ValueError("Adapter artifact hash mismatch")
    validate_model_config(record["config"])
    return record


def verify_lineage(
    directory, expected_base, expected_revision, expected_targets, expected_tokenizer_sha256=None
):
    """Integrity against the training record. A hash is not publisher or license trust."""
    directory = Path(directory)
    record = verified_adapter(directory)
    config = record["config"]
    if config["base_model"] != expected_base or config["revision"] != expected_revision:
        raise ValueError("training record names a different base revision")
    adapter_config = json.loads((directory / "adapter_config.json").read_text())
    base_name = str(adapter_config.get("base_model_name_or_path") or "")
    if base_name.lower().endswith(".gguf"):
        raise ValueError("GGUF is not the adapter base")
    if base_name and base_name != expected_base:
        raise ValueError("adapter metadata names a different base")
    targets = adapter_config.get("target_modules")
    if targets is not None and list(targets) != list(expected_targets):
        raise ValueError("adapter target modules do not match the reviewed set")
    if expected_tokenizer_sha256 is not None:
        tokenizer = directory / "tokenizer_config.json"
        if (
            tokenizer.is_symlink()
            or not tokenizer.is_file()
            or sha(tokenizer) != expected_tokenizer_sha256
        ):
            raise ValueError("tokenizer does not match the expected digest")
    return {
        "status": "INTEGRITY_MATCH",
        "publisher_trust": "NOT_VERIFIED",
        "license_trust": "NOT_VERIFIED",
    }


def require_finite_loss(metrics, key):
    import math

    if key not in metrics or not math.isfinite(float(metrics[key])):
        raise ValueError("Training or evaluation produced a missing/non-finite loss")
