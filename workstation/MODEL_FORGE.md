# Model Forge v1 — initial implementation

This is a small, offline starter for the planned AUREX Model Forge, **not** an LLM trainer or working model-merger.

## Chromebook commands

From a checkout of this branch:

```bash
python3 workstation/model_forge.py demo --steps 200
python3 -m unittest discover -s workstation/tests -v
```

The demo learns synthetic character-transition frequencies; it does not train a transformer or run HLE. No benchmark score is produced.

## Pretrained weights provenance

After reviewing a specific model's license, terms, redistribution, and commercial-use rights, record the exact weights file:

```bash
python3 workstation/model_forge.py manifest \
  --name "reviewed-model" --source "publisher/repository" \
  --revision "exact-commit-or-tag" --license "reviewed-license" \
  --weights /path/to/model.gguf --output /path/to/manifest.json \
  --permission-reviewed
```

The script hashes local bytes and records *user-declared* provenance; it does **not** independently authenticate the license or model identity. Never set the review flag without performing the review.

## Next gated stages

1. Add a model registry and allowlisted model download flow with exact revision and license checks.
2. Add a local llama.cpp inference adapter.
3. Add a held-out practice dataset and independent scoring.
4. Add a browser interface to display training and scoring reports.
5. Integrate reviewable vibe-coding PR workflows.
6. Optional remote GPU fine-tuning after resource and data provenance checks.

No weights are downloaded, fine-tuned, merged, or redistributed in v1. The Chromebook offline AUREX folder remains a separate installation.
