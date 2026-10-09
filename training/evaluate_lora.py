"""Loss-only held-out diagnostic. Not governance accuracy and not independent grading."""

import argparse
import json
from pathlib import Path

from training.common import collator, encode, require_finite_loss, verified_adapter, verified_data
from training.prepare_dataset import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError("Use a new output file")
    record = verified_adapter(a.adapter)
    c = record["config"]
    manifest, _, rows = verified_data(a.data)
    if sha(a.data / "manifest.json") != record["data_manifest_sha256"]:
        raise ValueError("Dataset version mismatch")
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

    tok = AutoTokenizer.from_pretrained(a.adapter, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        c["base_model"], revision=c["revision"], trust_remote_code=False, use_safetensors=True
    )
    model = PeftModel.from_pretrained(model, a.adapter)
    args = TrainingArguments(
        output_dir=str(a.output.parent / "eval-work"),
        report_to=[],
        use_cpu=True,
        per_device_eval_batch_size=1,
    )
    trainer = Trainer(
        model=model,
        args=args,
        eval_dataset=[encode(r, tok, c["max_length"]) for r in rows],
        data_collator=collator(tok),
    )
    metrics = trainer.evaluate()
    require_finite_loss(metrics, "eval_loss")
    result = {
        "status": "PASS",
        "kind": "held-out loss diagnostic",
        "metrics": metrics,
        "dataset_manifest": sha(a.data / "manifest.json"),
        "n": manifest["counts"]["eval"],
        "governance_accuracy": "NOT RUN",
        "independent_review": "NOT VERIFIED",
    }
    with a.output.open("x") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
