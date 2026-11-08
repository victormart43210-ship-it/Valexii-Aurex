"""Optional genuine PEFT LoRA training on original Transformers weights."""

import argparse
import json
import os
from pathlib import Path

from training.common import (
    collator,
    encode,
    require_finite_loss,
    validate_model_config,
    verified_data,
)
from training.prepare_dataset import sha

# Reviewed target modules. An unknown architecture is not guessed.
LORA_TARGETS = {
    "qwen2": ["q_proj", "v_proj"],
    "mistral": ["q_proj", "v_proj"],
    "llama": ["q_proj", "v_proj"],
}


def lora_targets(config):
    if "target_modules" in config:
        modules = config["target_modules"]
        if (
            not isinstance(modules, list)
            or not modules
            or any(not isinstance(name, str) or not name.endswith("_proj") for name in modules)
        ):
            raise ValueError("LoRA targets must be a list of projection module names")
        return modules
    family = str(config.get("architecture", "qwen2"))
    if family not in LORA_TARGETS:
        raise ValueError(f"no reviewed LoRA targets for {family}")
    return list(LORA_TARGETS[family])


def execution_plan(config):
    """QLoRA stays NOT_RUN unless this host has CUDA, bitsandbytes, and owner approval."""
    method = config.get("method", "lora")
    if method not in {"lora", "qlora"}:
        raise ValueError("unknown training method")
    if method == "lora":
        return {"status": "READY", "method": "lora"}
    from aurex.ox.forge import hardware_preflight

    report = hardware_preflight()
    approved = os.environ.get("AUREX_QLORA_APPROVED") == "1"
    if report["qlora"] != "READY_NOT_EXECUTED" or not approved:
        return {
            "status": "NOT_RUN",
            "method": "qlora",
            "hardware": report,
            "owner_approval": "PRESENT" if approved else "ABSENT",
        }
    return {"status": "READY", "method": "qlora", "hardware": report}


def model_load_kwargs(config, plan):
    """Build a from_pretrained call. QLoRA adds 4-bit config only after the plan is READY."""
    if plan.get("method") == "qlora" and plan.get("status") != "READY":
        raise ValueError("QLoRA is not authorized")
    kwargs = {
        "revision": config["revision"],
        "trust_remote_code": False,
        "use_safetensors": True,
    }
    if plan.get("method") == "qlora":
        import torch
        from transformers import BitsAndBytesConfig

        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        kwargs["device_map"] = "auto"
    return kwargs


def validate_checkpoint(directory):
    """A resume source must be a complete LoRA safetensors adapter."""
    directory = Path(directory)
    weights = directory / "adapter_model.safetensors"
    adapter_config = directory / "adapter_config.json"
    if weights.is_symlink() or adapter_config.is_symlink():
        raise ValueError("checkpoint symlinks are rejected")
    if not weights.is_file() or not adapter_config.is_file():
        raise ValueError("checkpoint is incomplete")
    from safetensors import safe_open

    with safe_open(weights, framework="pt") as handle:
        keys = list(handle.keys())
    if not any("lora_" in key for key in keys):
        raise ValueError("checkpoint has no LoRA tensors")
    saved = json.loads(adapter_config.read_text())
    if saved.get("base_model_name_or_path", "").lower().endswith(".gguf"):
        raise ValueError("a GGUF file is not a resume checkpoint")
    return {"status": "PASS", "tensors": len(keys)}


def fit(model, tokenizer, rows, config, output):
    from peft import LoraConfig, get_peft_model
    from transformers import Trainer, TrainingArguments, set_seed

    rank = int(config["rank"])
    dropout = float(config.get("lora_dropout", 0.0))
    if not 1 <= rank <= 64 or not 0.0 <= dropout < 0.5:
        raise ValueError("rank or dropout is outside the bounded range")
    if int(config.get("gradient_accumulation_steps", 1)) < 1:
        raise ValueError("gradient accumulation must be positive")
    set_seed(config["seed"])
    model = get_peft_model(
        model,
        LoraConfig(
            task_type="CAUSAL_LM",
            r=rank,
            lora_alpha=config["alpha"],
            lora_dropout=dropout,
            target_modules=lora_targets(config),
            bias="none",
        ),
    )
    if config.get("method") == "qlora":
        from peft import prepare_model_for_kbit_training

        model = prepare_model_for_kbit_training(model)
    if config.get("gradient_checkpointing"):
        model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
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
    limit = config.get("max_artifact_bytes")
    if limit is not None:
        total = sum(path.stat().st_size for path in Path(output).rglob("*") if path.is_file())
        if total > int(limit):
            raise ValueError("training artifacts exceed the storage bound")
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
    plan = execution_plan(config)
    if not a.execute or plan["status"] == "NOT_RUN":
        print(
            json.dumps(
                {
                    "status": "NOT RUN" if plan["status"] != "NOT_RUN" else "NOT_RUN",
                    "reason": "Preflight only; --execute starts compute"
                    if plan["status"] != "NOT_RUN"
                    else "QLoRA is not authorized on this host",
                    "counts": manifest["counts"],
                    "plan": plan,
                }
            )
        )
        if plan["status"] == "NOT_RUN":
            raise SystemExit(2)
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
        **model_load_kwargs(config, plan),
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
