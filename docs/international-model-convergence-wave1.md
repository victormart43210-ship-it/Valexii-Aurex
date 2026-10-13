# International model convergence — Wave 1 (proposal)

Status: **DESIGN ONLY / NOT VERIFIED**. This public AUREX repository is an independent witness, never BCXMET's runtime authority. No production model, training job, or crawler has been installed by this change.

## Goal
Evaluate Chinese and international open-weight models on the **same frozen, provenance-rich test set**, then admit only reproducible, independently reviewed capabilities. Preserve original-language text and translated text separately. Do not equate a model's answer, translation, retrieved webpage, or another agent's agreement with security truth.

## Candidate components (license/version review required)

| Role | Candidate | Admission condition |
|---|---|---|
| Local inference | Ollama / llama.cpp | Resource-bounded, pinned model digest, deterministic API envelope |
| Multilingual reasoning | Qwen family | Exact model-card license, Chinese/English test set, tool-use and abstention results |
| Independent challenger | DeepSeek or distinct family | Independent provider and prompt path, blinded comparison |
| Small multimodal model | MiniCPM | Model-specific Android/device feasibility and provenance |
| Training | Unsloth (initial), ms-swift (advanced) | Frozen train/eval split, artifact hashes, legal dataset provenance |
| Research | Firecrawl (hosted), Crawl4AI (local) | Allowlisted crawl scope, SSRF protection, URL/time/content hash |
| OCR | PaddleOCR | Original image retained, multilingual OCR error evaluation |
| Security validation | MobSF, Semgrep | Independent reports, no runtime authority or unverified security claims |

## Authority boundaries

1. **Evidence**: ingestion emits URL, UTC timestamp, content digest, source language, retrieval method, and license/robots metadata when available. Raw external text is untrusted.
2. **Qualification**: enforce allowlists, network safety (no private/loopback/link-local destinations), size limits, freshness, consent, and content-type checks. Reject prompt-injection instructions as commands.
3. **Reality**: independently cross-check factual and translated claims against anchored references. Model agreement is not independent evidence.
4. **Authority**: AUREX can return SUPPORTED / CONTESTED / INSUFFICIENT / STALE / HOLD. No adapter may promote its own output to a product authorization.
5. **Effect**: prohibit unapproved writes, payments, device changes, autonomous scans of third-party infrastructure, or production deployments.

## Evaluation matrix

Every row must have PASS / FAIL / NOT RUN / NOT VERIFIED, with run ID, exact code SHA, model digest, dataset SHA, command, environment, and artifact path.

| Test | Required negative case |
|---|---|
| Provider adapters and schema | Malformed JSON / provider timeout / model swap |
| Prompt-injection resistance | Webpage requests secret exfiltration or tool invocation |
| Multilingual translation | Chinese security terminology changes meaning or omits negation |
| Citation and freshness | Invented URL / stale source / mismatched content digest |
| Cross-model challenge | Two correlated models agree on false evidence |
| Security authority isolation | LLM claims PASS or changes an authorization field |
| Abstention | No credible source, conflicting source, or offline state |
| Performance | Resource exhaustion, long input, network timeout |
| Training hygiene | Test contamination, license conflict, PII in examples |
| Android safety | Missing scanner coverage incorrectly displayed as safe |

## Staged implementation

- **Wave 1A:** inspect current AUREX contracts; implement an additive, read-only provider registry and evidence-envelope adapters with mocked network calls and negative tests. No new required dependencies.
- **Wave 1B:** local Qwen via existing Ollama API, pinned versions and model digest; run frozen multilingual and adversarial evaluation.
- **Wave 1C:** optional Crawl4AI/Firecrawl ingestion through a network-isolated worker; no raw webpage text may become an instruction.
- **Wave 1D:** OCR and challenger adapters; compare baseline against candidates with independent oracles.
- **Wave 1E:** fine-tune only after datasets, evaluation holdouts, licensing, GPU budget, and reproducibility are approved. Never train on benchmark holdouts.

## Compatibility note

The separate Chromebook `~/aurex-offline-v3` environment and its `verify_gate.py` are not established as identical to this public GitHub repository. Do not overwrite or claim integration with that environment until its exact source SHA and contracts are reconciled.

## Primary upstreams

- https://github.com/QwenLM/Qwen3
- https://github.com/deepseek-ai
- https://github.com/OpenBMB/MiniCPM
- https://github.com/unslothai/unsloth
- https://github.com/modelscope/ms-swift
- https://github.com/unclecode/crawl4ai
- https://github.com/PaddlePaddle/PaddleOCR
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/semgrep/semgrep
