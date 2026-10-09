"""Optional genuine PEFT LoRA training on original Transformers weights."""

import argparse
import json
from pathlib import Path

from training.common import (
    collator,
    encode,
    require_finite_loss,
    validate_model_config,
    verified_data,
)
from training.prepare_dataset import sha


def fit(model, tokenizer, rows, config, output):
    from peft import LoraConfig, get_peft_model
    from transformers import Trainer, TrainingArguments, set_seed

    set_seed(config["seed"])
    model = get_peft_model(
        model,
        LoraConfig(
            task_type="CAUSAL_LM",
            r=config["rank"],
            lora_alpha=config["alpha"],
            lora_dropout=0.0,
            target_modules=["q_proj", "v_proj"],
            bias="none",
        ),
    )
    encoded = [encode(row, tokenizer, config["max_length"]) for row in rows]
    args = TrainingArguments(
        output_dir=str(output),
        max_steps=config["max_steps"],
        per_device_train_batch_size=1,
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 1),
        learning_rate=config["learning_rate"],
        seed=config["seed"],
        data_seed=config["seed"],
        report_to=[],
        save_strategy="no",
        logging_steps=1,
        use_cpu=config.get("use_cpu", True),
        dataloader_num_workers=0,
        remove_unused_columns=False,
    )
    trainer = Trainer(
        model=model, args=args, train_dataset=encoded, data_collator=collator(tokenizer)
    )
    result = trainer.train()
    require_finite_loss(result.metrics, "train_loss")
    model.save_pretrained(output, safe_serialization=True)
    tokenizer.save_pretrained(output)
    return result.metrics


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()
    config = json.loads(a.config.read_text())
    validate_model_config(config)
    manifest, rows, _ = verified_data(a.data)
    if a.output.exists():
        raise ValueError("Use a new output directory")
    if not a.execute:
        print(
            json.dumps(
                {
                    "status": "NOT RUN",
                    "reason": "Preflight only; --execute starts compute",
                    "counts": manifest["counts"],
                }
            )
        )
        return
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    set_seed(config["seed"])
    tokenizer = AutoTokenizer.from_pretrained(
        config["base_model"], revision=config["revision"], trust_remote_code=False
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"],
        revision=config["revision"],
        trust_remote_code=False,
        use_safetensors=True,
    )
    metrics = fit(model, tokenizer, rows, config, a.output)
    record = {
        "status": "PASS",
        "scope": "training execution only",
        "config": config,
        "data_manifest_sha256": sha(a.data / "manifest.json"),
        "metrics": metrics,
        "artifact_sha256": {f.name: sha(f) for f in a.output.iterdir() if f.is_file()},
        "architecture_review": manifest["architecture_review"],
        "independent_evaluation": "NOT RUN",
    }
    (a.output / "training-record.json").write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
