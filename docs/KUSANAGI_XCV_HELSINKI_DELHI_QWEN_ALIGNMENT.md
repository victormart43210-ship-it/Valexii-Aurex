# OPERATION KUSANAGI XCV — HELSINKI × NEW DELHI × LOCAL QWEN

Status: **SOURCE PROPOSED, DRAFT / HOLD.** This branch **depends on unmerged PR #84** at `70281056aa5f43070c1c4415a609b3a71850d56f`. Same canonical repository; no separate runtime repo, merge, deployment, model download, cloud inference or training.

## What was carried forward

**Finland:** University of Helsinki / Helsinki-NLP `OpusFilter 3.3.1`, a configurable parallel-corpus filtering toolkit. Source: https://github.com/Helsinki-NLP/OpusFilter and https://helsinki-nlp.github.io/OpusFilter/filters/length_filters.html . Earlier user-side shell kit `HELSINKI_OPUS_QWEN_XC_20261017.sh` prepared a pinned official wheel but **installation and any real OpusFilter execution are NOT VERIFIED here**. This PR:
- Implements a **small independent deterministic analogy** to its absolute word-length and maximum word-length ratio filters, plus deduplication, in `aurex/research_alignment.py`; it is NOT OpusFilter itself.
- Adds a true *optional* `--opusfilter-demo` path that uses an **already installed** OpusFilter **exact version 3.3.1** on invented parallel text only. It executes the upstream `opusfilter` binary in a private temp directory with a strictly generated `config.yaml`, 60-second timeout, bounded outputs and explicit exact sequence check against the local deterministic expectations.
- Does NOT install the package, fetch OPUS data, clean real customer documents, or alter Qwen weights. This filters toy text quality *only*.

**India:** IIT Delhi DAIR `LRPlan` research: https://github.com/dair-iitd/LRPlan ; local earlier evidence referred to pinned upstream commit `ca45c8037b254d934d1cfc0032a042aa3bd569ee`. The separate NEW_DELHI R2 experiment previously reported 16 synthetic tests PASS and one local Qwen response matching the structure `{"steps":["inspect","test","review"]}`. **We have NOT independently rerun that original package's 16 tests here.** This PR:
- Implements only a separate closed-schema / ordered synthetic plan constraint checker `validate_synthetic_plan`, not the LRPlan multi-agent runtime or its benchmarks.
- Requires exactly three steps `inspect → test → review` with no extra fields or executable actions; status is **STRUCTURE_MATCH_ONLY** vs **HOLD**. This does not prove reasoning depth, optimality, or actual planning correctness.
- Provides a separate new reproducible tests collection; **do not claim it is the original 16/16**.

**AUREX/Qwen:** Building on PR #84's local-only `qwen_readiness` and `aurex.local_inference`:
- `--check` runs offline synthetic deterministic filters and JSON validator, no model and no network.
- `--opusfilter-demo` explicitly invokes only an existing pinned OpusFilter 3.3.1 executable with synthetic input, no package installation.
- `--infer --approve-local --model <registered ID>` first checks the model list only on numeric loopback, then submits one bounded *synthetic* prompt to existing local Qwen using the already supported `llama.cpp` or `ollama` backends. No prompts/models/files are sent to a remote service.
- Output receipts include counts, local digests and PASS/HOLD-style markers but **never raw response text**, local filesystem paths, credentials or weights.
- Qwen-generated plan validity is not model IQ, official HLE, independent test verification or authorization. A SHA digest is an integrity fingerprint only.

## Commands — laptop/WSL/Chromebook Linux

Requires Python 3.12+ and the existing AUREX development environment from PR #84. From this branch's checked-out canonical repo:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_research_alignment.py tests/test_qwen_research_pipeline.py tests/test_qwen_readiness.py tests/test_qwen_proxy_boundary.py tests/test_local_inference.py
python -m compileall -q aurex/research_alignment.py workstation/qwen_research_pipeline.py
ruff check aurex/research_alignment.py workstation/qwen_research_pipeline.py tests/test_research_alignment.py tests/test_qwen_research_pipeline.py
mypy --strict aurex/research_alignment.py workstation/qwen_research_pipeline.py
python -m workstation.qwen_research_pipeline --check
```

*Optional only after operator personally installs and verifies official OpusFilter 3.3.1 in an isolated environment:*

```bash
python -m workstation.qwen_research_pipeline --opusfilter-demo
```

*Optional only once local llama.cpp at 127.0.0.1:8080 advertises your exact **previously installed** GGUF model identifier; one human-authorized synthetic run:*

```bash
python -m workstation.qwen_research_pipeline --infer --approve-local --backend llama.cpp --model '<local-model-id>'
```

Ollama alternative: `--backend ollama --model '<exact-installed-ollama-model-name>'`. No model pulls, remote serving, paid inference or background jobs. Do **not** paste GGUF paths or model output into public PR comments.

## Validation matrix (source audit, as of branch creation)

| Item | Result |
| --- | --- |
| New synthetic corpus/plan tests on exact branch SHA | **NOT RUN** unless independently executed |
| New OpusFilter CLI using real installed 3.3.1 | **NOT RUN** |
| OpusFilter subprocess orchestration under mocked fixture | Test supplied; **NOT RUN** until executed |
| Original Helsinki demo package | **NOT VERIFIED** |
| Original Delhi 16/16 R2 synthetic tests | **USER REPORTED**; not replayed here |
| Actual local Qwen response on physical owner machine | **NOT VERIFIED on this branch** |
| Backend 5-GET bridge and public website | **UNCHANGED** |
| Actual Lovable frontend source | **UNCHANGED**, source not synchronized |
| External spend / network model downloads | **NONE PERFORMED** |
| Release / security authority | **HOLD** |

## Promotion gates

1. Independent exact-HEAD Python compile, Ruff, Mypy and pytest. Any failures => HOLD, include actual trace without secrets.
2. Independently reproduce original New Delhi 16 cases from the original package only if the complete original tests/source are provided. Do not silently substitute the new synthetic cases.
3. On Dell: record CPU, RAM, runtime, model hash, actual Qwen latency/tokens/sec and 0-cost local inference. Use independently reviewed held-out benchmarks for meaningful model improvements; *the three-step task is not a benchmark*.
4. Explicitly approved upstream OpusFilter install in isolated venv, version/hash verified, demonstrate parity on synthetic corpus, then optionally evaluate **consented and scoped** external corpora only by new owner decision.
5. Never make the model its own judge or grant BCXMET, XAITA, deploy, purchase or security authority. FINANCIAL AUTHORITY ALWAYS HOLD.
6. Test same scoped code after combining unmerged PR #81 private gateway, PR #83 fencing and PR #84 Qwen support. Review dependencies before serial merges.
7. Website owner-only status may later describe *actual* measured test outcomes; do not display invented live telemetry or expose localhost directly to public browser.
8. Source remains **DRAFT** until independent review and explicit owner merge/deploy approval.

Governance: Evidence → Qualification → Reality → Authority → Effect. No-self-witness. UNKNOWN != SAFE. External cost $0. ORB MOTION AUTHORITY = NONE.
