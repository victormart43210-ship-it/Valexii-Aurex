"""Merge an actual PEFT artifact into safetensors; GGUF conversion is separate."""

import argparse
import json
from pathlib import Path

from training.common import verified_adapter


def greedy_token_ids(model, input_ids, max_new_tokens):
    import torch

    model.eval()
    generated = input_ids
    with torch.no_grad():
        for _ in range(max_new_tokens):
            logits = model(generated).logits
            next_id = logits[0, -1].argmax().view(1, 1)
            generated = torch.cat([generated, next_id], dim=1)
    return [int(token) for token in generated[0].tolist()]


def assert_merge_agreement(adapter_model, merged_model, input_ids, max_new_tokens=2):
    """Greedy tokens must match. A match is not production approval."""
    left = greedy_token_ids(adapter_model, input_ids, max_new_tokens)
    right = greedy_token_ids(merged_model, input_ids, max_new_tokens)
    if left != right:
        raise ValueError("merged weights do not match the adapter outputs")
    return {
        "status": "MATCH",
        "tokens": len(left),
        "production_ready": False,
        "gguf_conversion": "NOT_RUN",
        "deployment_approval": "NOT_APPROVED",
    }


def gguf_gate(requested):
    """Conversion is a separate operation and was not executed here."""
    if requested:
        return {
            "gguf_conversion": "NOT_RUN",
            "reason": "no pinned converter was executed",
            "production_ready": False,
        }
    return {"gguf_conversion": "NOT_RUN", "production_ready": False}


def assert_export_identity(record, expected_base, expected_revision):
    """The export names its base. GGUF conversion is not a training result."""
    if record.get("base_model") != expected_base or record.get("revision") != expected_revision:
        raise ValueError("export identity mismatch")
    if str(expected_base).lower().endswith(".gguf"):
        raise ValueError("GGUF is not a Transformers training weight")
    conversion = record.get("gguf_conversion", "NOT RUN")
    if conversion != "NOT RUN" and record.get("gguf_verified") is not True:
        raise ValueError("unverified GGUF conversion")
    return {"status": "PASS", "gguf_conversion": conversion, "financial_authority": "NONE"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError("Use a new output directory")
    c = verified_adapter(a.adapter)["config"]
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(
        c["base_model"], revision=c["revision"], trust_remote_code=False, use_safetensors=True
    )
    PeftModel.from_pretrained(model, a.adapter).merge_and_unload().save_pretrained(
        a.output, safe_serialization=True
    )
    AutoTokenizer.from_pretrained(a.adapter, trust_remote_code=False).save_pretrained(a.output)
    (a.output / "export-record.json").write_text(
        json.dumps(
            {
                "format": "safetensors",
                "base_model": c["base_model"],
                "revision": c["revision"],
                "gguf_conversion": "NOT RUN",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
