# AUREX-OX Model Forge

Observed on 2026-11-07 at 6:35 PM America/Chicago, from `fc2bed4dd98054503254ad1a4c11fbecd7b0deca`. Production remains HOLD. Financial authority remains NONE. Paid inference remains OFF. This branch does not include PR #208.

The static catalog in `aurex.ox.registry` stays a candidate list. `validate_registry()` still rejects self-approval, installed runtimes, and a training state other than `NOT_STARTED`. Promotions live in the separate ledger in `aurex.ox.forge`. A model cannot move its own entry. Training completion is not deployment approval.

## What runs

```bash
python -m aurex.ox.forge preflight
python -m aurex.ox.forge acquire --manifest manifest.json --source /controlled/src --dest /controlled/store --ledger /controlled/ledger.json
python -m training.prepare_dataset --train train.jsonl --eval eval.jsonl --provenance provenance.json --output /controlled/data
python -m training.train_lora --data /controlled/data --config training/configs/qwen05b-lora.json --output /controlled/run
```

`--execute` is required before LoRA compute. `"method": "qlora"` with `--execute` exits 2 and prints `NOT_RUN` unless CUDA, bitsandbytes, and `AUREX_QLORA_APPROVED=1` are all present. No command provisions a GPU or spends money.

Acquisition accepts only the allowlisted repository `Qwen/Qwen2.5-0.5B-Instruct` at revision `7ae557604adf67be50417f59c2c2f167def9a775`. The manifest must set `trust_remote_code` to false, name a human reviewer, and approve commercial use and redistribution explicitly. Files are copied from a local directory, hashed, and refused when incomplete, corrupt, symlinked, short of disk, or different from an already verified copy. The Apache-2.0 note in `training/README.md` is not a fresh model-card fetch.

The ledger stages are `DISCOVERED → REVIEWED → ACQUIRED → TRAINED → EVALUATED → APPROVED → STAGING`. Staging requires a different reviewer and a 40-character rollback revision. Serving an approved identity goes through `LlamaCppAdapter` when the caller passes the ledger entry. The default adapter path is unchanged.

## What was measured

- Local fixture acquisition, hash resume, and remote-code rejection: PASS in `tests/test_ox_model_forge.py`.
- Tiny random Qwen2 LoRA: PASS. Two optimizer steps, finite `train_loss` 2.2353527545928955, four LoRA tensors, safetensors reload. This is not 0.5B quality.
- QLoRA on this host: NOT_RUN, exit 2. CUDA absent. bitsandbytes absent. Owner approval absent.
- Full `Qwen/Qwen2.5-0.5B-Instruct` download and fine-tune: NOT_RUN.
- GGUF conversion: NOT_RUN. GGUF files are rejected as training weights.
- Synthetic domain pack: PASS. Four domains, four train rows, four eval rows, no shared prompts. The rows are synthetic. They are not customer records.
- External-score comparison: PASS for the harness. A security regression is rejected. No foundation model was scored.
- Jules review: NOT_RUN.

## Hold

Do not deploy an adapter from this ledger. Do not treat agreement between models as proof. Do not enable paid inference. Do not grant model output financial, security, or production authority.
