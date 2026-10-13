# AUREX-Qwen LoRA pipeline

This trains original Transformers weights, not GGUF. The Chromebook's reported 24
examples have not been read here. No Qwen2.5-0.5B fine-tune is supplied.

Tested stack: Python 3.12, CPU PyTorch 2.6.0, Transformers 4.51.3, PEFT 0.15.2,
Accelerate 1.6.0. These are pinned tested versions, not a claim of latest releases.
The CPU test initializes a tiny random Qwen2, performs two optimizer steps, saves,
reloads and merges the adapter. It is not evidence of 0.5B training quality.

The model API reported Qwen/Qwen2.5-0.5B-Instruct revision
`7ae557604adf67be50417f59c2c2f167def9a775` on 2026-10-08; config pins that revision.
Model card: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct (Apache-2.0).
PEFT API: https://huggingface.co/docs/peft/main/en/quicktour

## Prepare your actual data

From the repository root, after installing the package and optional training requirements:

```bash
python -m training.prepare_dataset --train /path/train.jsonl --eval /path/eval.jsonl --provenance /path/provenance.json --output training/data/v1
python -m training.train_lora --data training/data/v1 --config training/configs/qwen05b-lora.json --output training/runs/qwen-v1
```

The second command is preflight only. Add `--execute` only on an authorized machine
with adequate memory. CPU defaults do not make a 2.7 GB Chromebook an adequate
training host. No paid GPU is provisioned by these scripts.

Provenance JSON must include nonempty `source`, `license`, `author` and
`"benchmark_data": false`. Supply truthful licensing information; this declaration
is not independently verified. Inputs use `{"messages":[{"role":"user","content":"..."},
{"role":"assistant","content":"..."}]}`, optionally beginning with a system message.
Multiturn conversations must alternate user/assistant.

Validation rejects empty/invalid rows, roles, exact/near duplicate prompts, differing
targets for matching prompts, train/eval overlap and known HLE canaries. It preserves
original bytes and writes hashes. It does not prove semantic non-contamination or
correct architecture labels. A human independent review remains required. The
provided four-example eval split is only a preliminary diagnostic, not a robust
held-out evaluation; the public fixtures in this repository are never hidden tests.

## Train, diagnose loss, export

```bash
python -m training.train_lora --data training/data/v1 --config training/configs/qwen05b-lora.json --output training/runs/qwen-v1 --execute
python -m training.evaluate_lora --adapter training/runs/qwen-v1 --data training/data/v1 --output training/runs/qwen-v1-eval.json
python -m training.export_model --adapter training/runs/qwen-v1 --output training/runs/qwen-v1-merged
```

Training uses assistant-only loss, rejects overlength examples rather than silently
truncating, sets seeds, records source manifest hash/configuration/metrics and saves
safetensors. Held-out loss is not accuracy, hallucination rate or independent grading.
Export produces merged safetensors. Converting those to GGUF requires a separately
pinned llama.cpp converter and subsequent inference validation; it is NOT RUN here.
A CPU LoRA smoke is implemented; CUDA/QLoRA execution is NOT VERIFIED.

Use new output directories for every run. Do not upload private data or model weights
to the git repository. Use the separate A/B/C/D CLI for behavior measurement, with
reference files withheld from model execution and an external trusted verifier.
