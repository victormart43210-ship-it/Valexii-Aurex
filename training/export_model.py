"""Merge an actual PEFT artifact into safetensors; GGUF conversion is separate."""

import argparse
import json
from pathlib import Path

from training.common import verified_adapter


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
