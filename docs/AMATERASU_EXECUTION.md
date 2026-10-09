# Executable evaluation, October 8

## Contracts and limitations

`ModelAdapter.answer` remains compatible. Ollama and OpenAI-compatible adapters now
send explicit generation settings and capture supplied token usage. `LlamaCppAdapter`
targets an already running `llama-server` on literal loopback HTTP; it does not repair
or start the Chromebook binary. Remote OpenAI-compatible access requires HTTPS and
an environment credential. Redirects and environment proxies are disabled. Remote
endpoint DNS rebinding/SSRF hardening remains an independent security-review item;
do not expose endpoint configuration to untrusted users.

`InferenceClient` records input/output hashes, ID, timestamp, latency, declared model
revision/quantization/runtime/settings and error codes. PASS denotes completed
inference only; answer verification stays NOT VERIFIED. Provider revision strings
are declarations, not proof of the actual served weights. Provider errors never
serialize exception text. Explicit token controls are portable only to compatible
endpoints; unsupported-parameter rejections fail closed. No automatic retries.

`Witness` signatures bind source, item/prompt context digest, answer digest, evidence digest, outcome, time,
expiry and revocation. Public keys come from an operator-controlled trust store;
never load keys from model output or retrieved documents. Compute context_sha256 with
`aurex.provenance.fingerprint({"item_id": item_id, "prompt": prompt})`. Signed
conflicting answers for that same context cause HOLD; cross-question replay is rejected. Qualification preserves
conflicts and returns no product authority. Signatures authenticate assertions,
not their real-world truth or evaluator independence. Live revocation distribution
and trusted-source onboarding are external prerequisites. Old records are retained.
Legacy UER unsigned attestations can no longer grant PASS. Ledger prefix integrity
is distinct from completeness: supply independently retained head/count checkpoints.
Durable external anchoring still needs operational deployment.

## Run original infrastructure fixtures

```bash
python -m aurex.evals.demo --output /tmp/aurex-original-smoke
```

Eight public, original development fixtures cover arithmetic, science, coding and
knowledge of evidence rules. Scripted outputs include one deliberate error. Synthetic
signed witnesses let the harness exercise qualification, not claim independent
AI efficacy. Do not train and evaluate on these fixtures and call it held-out quality.

## Run a real model and score separately

Create a config with `base` and optional `tuned` objects:

```json
{"base":{"identity":{"provider":"llama.cpp","model":"qwen","revision":"YOUR_GGUF_SHA256","quantization":"Q4_K_M","runtime":"PINNED_LLAMA_CPP_COMMIT"},"base_url":"http://127.0.0.1:8080/v1","generation":{"temperature":0,"max_tokens":256,"seed":42}}}
```

Provider may be `llama.cpp`, `ollama`, or `openai-compatible`. Each prompt row has
only `item_id` and `prompt`; extra reference fields are rejected. To measure governance,
ask for JSON with `answer`, `status`, `evidence_ids`; plain answers are recorded as
NOT VERIFIED. Witness JSON maps item IDs to signed Witness arrays. Trust JSON maps
source IDs to base64 Ed25519 public keys. `{}` stores are allowed and cause HOLD.

```bash
python -m aurex.evals.cli generate --config config.json --prompts questions.jsonl --witnesses witnesses.json --trust-store trust.json --output predictions.json --execute
python -m aurex.evals.cli score --predictions predictions.json --references references.json --output scores.json
```

Scoring references map every exact item ID to `{"answer":"expected","status":"PASS"}`.
Keep that file inaccessible to the generation process. The scorer is deterministic
exact-match, not a semantic/official HLE grader. Case, wording and formatting matter.
Run output is created exclusively and hashed, but its digest is not an external
signature. Preserve the digest in independent storage before scoring.

A/B and C/D use paired replay: one inference per item, then the same output with
AUREX qualification. This isolates qualification and does not test iterative answer
repair. No corrected answer is supplied by the verifier. Base/tuned model comparisons
use identical prompts/settings selected by the operator. Missing tuned config marks
C/D NOT RUN. Metrics retain all frozen items in the denominator and separately record
errors, false PASS, false FAIL, abstention, evidence support, latency and usage. Paired
counts and exact McNemar p-values are diagnostics. No general superiority or formal
confidence interval is established by a small development smoke. Costs stay null
until real provider pricing and usage can be reconciled; replay does not incur a
second inference bill.

## HLE admission

HLE STATUS: NOT RUN. Official sources reviewed 2026-10-08:
https://github.com/centerforaisafety/hle
https://huggingface.co/datasets/cais/hle/blob/main/README.md
https://agi.safe.ai/

Freeze dataset ID/revision/hashes/unique IDs and choose original HLE vs Rolling vs
Diamond explicitly. Do not redistribute benchmark material or use it in training.
Keep answers/rationales outside solver access. Pin the official judging prompt and
model, blind arm labels, and audit all expected outcomes. Official sample evaluator
code inspected October 7 at 22ed3074b1e7b134bcbc09028d0ba320839b0655 had a small-sample
calibration IndexError and full-dataset metric denominator; do not mistake a tiny
subset report for full HLE accuracy. This harness supports text-only original items;
multimodal HLE adapter and official judge integration remain PARTIAL/MISSING.

Before HLE: remote exact-SHA CI, independently reviewed fixes, authorized dataset,
verified model access, reference isolation, frozen protocol, external evaluator,
contamination controls and approved compute budget. Synthetic fixture PASS does not
satisfy these gates.

## Chromebook illegal instruction

No Chromebook filesystem or binary was accessed. Root cause is NOT VERIFIED.
Run `bash tools/collect_llama_diagnostics.sh /path/to/llama-cli /path/to/llama-source`
on that machine. Inspect the exact faulting instruction, CPU flags, source revision,
linked ggml library paths and CMake cache before another rebuild. `--version` may not
reach the failure; if it does not, collect the same GDB evidence from the known failing
invocation locally. Do not send private prompt/model contents. Distinguish unsupported
instruction, stale shared library and wrong binary before choosing compiler changes.
