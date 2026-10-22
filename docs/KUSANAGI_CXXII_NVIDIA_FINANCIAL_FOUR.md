# KUSANAGI CXXII — NVIDIA Financial Services Four-Blueprint Convergence

**Research date:** 2026-10-22 (UTC). **Repository:** `victormart43210-ship-it/Valexii-Aurex`.
**Branch:** `work/kusanagi-cxxii-nvidia-finance-four`, stacked on draft PR #104
(`work/kusanagi-cxvii-contract-sqlite-proof`, original head
`3b3d1de63f764a777758f709130a91324bcd06ca`).
**Integration phase:** OFFLINE SYNTHETIC RESEARCH · **Authority NONE · Release HOLD**.

## Source audit — actual Firecrawl results, official NVIDIA pages

All four examples are on the official NVIDIA financial-services catalog.
Full source links, technologies and tested constraints:

| NVIDIA example | Official source | NVIDIA full workflow | AUREX code in this branch |
|---|---|---|---|
| Quantitative Signal Discovery Agent | https://build.nvidia.com/nvidia/quantitative-signal-discovery-agent | NeMo Agent Toolkit, Nemotron and three research agents for hypothesize → code → evaluate. Local 48GB+ GPU or hosted NIM. | Bounded, deterministic Decimal momentum candidate; no generated code, no backtest, no trading. |
| Build Your Own Transaction Foundation Model | https://build.nvidia.com/nvidia/build-your-own-transaction-foundation-model | RAPIDS cuDF/cuML, NeMo AutoModel transformer-based transaction embeddings. One A100 80GB/H100 minimum specified by NVIDIA. | CPU-only exact-cent and repeated-merchant **baseline features**, explicitly **not embeddings or foundation-model inference**. |
| AI Model Distillation for Financial Data | https://build.nvidia.com/nvidia/ai-model-distillation-for-financial-data | NeMo Customizer/Evaluator/Data Flywheel, LoRA teacher/student training, multi-GPU and storage infrastructure. Blueprint cites 2x A100/H100/H200/B200 and ~200GB disk. | Deterministic synthetic teacher/student F1 comparison, **not distillation or training**. |
| Financial Fraud Detection | https://build.nvidia.com/nvidia/financial-fraud-detection | RAPIDS preparation → GNN embeddings + XGBoost → Dynamo-Triton fraud score and explainability. GPU ≥32GB + 16GB system RAM specified. | Synthetic-only, typed external score intake; missing/unattributed/invalid scores HOLD, no fraud verdict or payment block. |

Further original NVIDIA explanations:
- https://developer.nvidia.com/industries/financial-services
- https://developer.nvidia.com/blog/automating-and-optimizing-financial-signal-discovery-with-multi-agent-systems/
- https://developer.nvidia.com/blog/build-your-own-transaction-foundation-model-for-financial-intelligence/
- https://developer.nvidia.com/blog/build-efficient-financial-data-workflows-with-ai-model-distillation

**No NVIDIA source code is vendored or implied to be licensed for redistribution.**
Before connecting containers, models, datasets, or APIs, review NVIDIA and third-party
license terms, commercial eligibility, privacy constraints and service costs.

## What was actually added

- `aurex/nvidia_finance/offline.py` — four discoverable manifest entries
  with explicit disabled/NVIDIA-not-installed status, typed offline candidate
  functions and mandatory synthetic-data guardrails.
- `workstation/nvidia_fsi_lab.py` — reusable `--catalog` and `--demo`
  command with exact-cent, Decimal and zero-network samples.
- `tests/test_nvidia_finance_offline.py` — synthetic adversarial checks for
  malformed inputs, source trust, missing scores, unsupported models and
  model/financial authority isolation.

Local invocation after checking out the branch (Python >=3.12):

```bash
python -m workstation.nvidia_fsi_lab --catalog
python -m workstation.nvidia_fsi_lab --demo
python -m pytest -q tests/test_nvidia_finance_offline.py
```

These demos never access customer financial data, bank accounts, private PDFs,
payment rails, equity brokerage accounts, internet endpoints or GPUs. Zero
external inference cost by construction. Outputs are **candidates, not
verification receipts**. Synthetic scores are NOT precision/recall evidence
for real customers.

## Required gates for actually running NVIDIA implementations (NOT SHIPPED)

1. Select owner-approved datasets with permission and de-identification;
   synthetic first. Split train/validation/test chronologically, prevent
   leakage and report base fraud prevalence.
2. Isolate the actual NVIDIA source or container in a **separate staging
   environment**, verify the license, pinned digest, GPU/VRAM/RAM budgets,
   SBOM, egress and secrets. The current 2GB Hetzner CPU VM is not sufficient
   for the published GPU training requirements.
3. Introduce versioned feature/embedding and score contracts, positive
   source provenance, operator catalog and reproducible evaluation records.
   No AI-generated Python executed directly. Static allowlisted DSL and
   sandboxed bounded evaluation only.
4. Obtain independent Challenger evidence for holdout F1, average precision,
   calibration, false positives, temporal shift and fairness. No synthetic
   score is evidence for live efficacy.
5. Integrate into canonical PR #104 authenticated job worker and DB
   **only after review**. PR #106 document analysis may be a source adapter
   for future text features, not an authority or paid default.
6. No production deployment, transfers, trading, fraud rejection, credit
   decision, invoice/payment effects, or account access without independent
   verification and explicit human authorization.

**Architecture:** Evidence → Qualification → Reality → Authority → Effect.
**The system may never be its own sole witness.** Unknown != healthy.
Reconciliation from PR #104 and new research features must not modify
historical receipts or bypass existing signed witnesses. This branch adds
only reference-safe **local research adapters**, not operational NVIDIA engines.

**Status ledger:** Firecrawl research PASS (official sources); code staged;
CI/tests to be read from exact PR head; live NVIDIA GPU training NOT RUN;
Railway deployment NOT RUN; Lovable editing NOT RUN; production HOLD.
