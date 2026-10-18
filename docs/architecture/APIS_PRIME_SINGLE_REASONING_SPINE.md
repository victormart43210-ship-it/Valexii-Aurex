# APIS PRIME — ONE REASONING SPINE, ONE VIEW

**Status: SOURCE-ONLY EXPERIMENTAL, DRAFT / HOLD.** Owner instruction: all fourteen *named research roles* should contribute through **one reasoning spine**, with **no fourteen extra dashboard tabs**. This implements the orchestration contract and a bounded offline Python entry point, **not fourteen production-ready skills** or a live Lovable/Railway feature.

## Architecture

```text
              ONE USER RESEARCH REQUEST
                         |
              [input admission and bounds]
                         |
              APIS PRIME REASONING SPINE
                         |
   +---------------------+----------------------+
   | acquisition         | analysis             | constraints
   | APIS-LEX            | LYSIPHER             | KUKULKAN
   | COATLICUE*          | SPECTRA              | ITZAMNAAJ
   | IACCHCODEX          | SIFTRA               | ELNOESIS**
   |                     | PROSOPHEX            | ANTHOFORGE*
   |                     | TEZCATLIPOCA         |
   +---------------------+----------------------+
                         |
               CHALLENGE + REALITY GATES
                XOLOTL* / CRUCIBLE*
                         |
            ONE CONVERGED EVIDENCE REPORT
          NOW | CHANGED | NEXT | WHY | PROOF
                         |
               CUSTOS / HUMAN REVIEW
```

Asterisks: **`*`** role is a placeholder/limited internal advisory, **NOT** a validated external challenger, working visual-image engine, or prototype executor. **`**`** local Qwen is **off by default** and requires explicit owner opt-in and an already configured loopback model. No Qwen model weights are installed, downloaded or billed. All methods are **one logical bounded DAG in one call**. They are not fourteen persistent agents or separate microservices, nor necessarily fourteen physical concurrent threads.

## New code in existing backend repository

- `aurex/apis_prime_spine.py`: `unified_research(...)` produces a single report and fourteen **receipts** keyed to the owner-locked AP01–AP14 names. Each diagnostic has honest statuses. It reuses existing `aurex.huruf_llull`, `aurex.research_alignment` and optionally `aurex.local_inference`, without copying/forking them.
- `workstation/apis_prime_cli.py`: prints **only the one-view report by default**; an optional `--details` expands the technical receipts. No HTTP endpoint, no background task and no dashboard tab created.
- `tests/test_apis_prime_spine.py`: isolated negative controls for non-execution, identity, model opt-in, output shape, input bounds and fail-closed subcomponents.
- `docs/architecture/apis_prime_registry.json`: immutable internal name/role IDs. Stable APIs should identify contributors by AP01–AP14, not mutable display strings.

### Offline operator demonstration

```bash
# Requires checkout of PR #86 stacked on #85 and #84, Python >=3.12
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  tests/test_apis_prime_spine.py tests/test_apis_prime_registry.py \
  tests/test_huruf_llull.py tests/test_huruf_llull_cli.py
python -m compileall -q aurex/apis_prime_spine.py workstation/apis_prime_cli.py
ruff check aurex/apis_prime_spine.py workstation/apis_prime_cli.py tests/test_apis_prime_spine.py
mypy --strict aurex/apis_prime_spine.py workstation/apis_prime_cli.py

python -m workstation.apis_prime_cli --file /path/to/lawfully_held_sample.txt
python -m workstation.apis_prime_cli --file /path/to/sample.py --details
# Optional: one explicit local-only model call, metrics-only prompt, no cloud:
python -m workstation.apis_prime_cli --file /path/to/sample.py --details \
  --approve-local-model --backend ollama --port 11434 --model '<already-installed-model-id>'
```

Use a consented, small plain UTF-8 text file only. Symlinks, PDF, DOCX and binary are not supported by the existing workstation reader. 64KiB maximum. No dynamic Python execution, filesystem writes to user data, package installs, or external HTTP network access in default mode. The source reader now uses atomic no-follow file opening and rejects nonregular files on supported Linux hosts.

**Model integration:** The Python function can invoke `aurex.local_inference.run_local_inference` **only with `local_model_approved=True`** and a known local model/backend/port. The prompt contains **derived aggregate statistics, not source text, filenames or source paths**. Model drafts remain `LOCAL_MODEL_DRAFT_UNVERIFIED`; the model can never issue a deployment or security decision. Real workstation Qwen inference has **NOT** been independently run on this exact PR.

## One-screen frontend view model

The `one_view` field exposes only **NOW → CHANGED → NEXT → WHY → PROOF** under a single **APIS PRIME · REASONING SPINE** heading. The normal CLI presents this as **one report**; `contributions` is an optional drill-down audit transcript, **not fourteen tabs**.

Future owner-only Lovable view: embed **one existing AUREX research panel** with a source selector, a run button, one synthesis and an expandable proof drawer. No invented charts/animation-authority or live telemetry. No geographic status tags, country flags or model readiness claims without independently witnessed exact-SHA evidence. Do not add a public research-route or expose local Qwen to the public browser. Existing website remains unchanged by this PR.

## Truth table for fourteen roles

| Role | What actually runs from source code | Honest scope |
| --- | --- | --- |
| APIS-LEX | Abjad only when Arabic script is present | Numerology, not translation |
| KUKULKAN | Existing modern nine-position Llull-inspired wheel | Exploratory combinations, not medieval cipher proof |
| LYSIPHER | Existing Caesar candidate-hash generator | 26 candidates, no selected plaintext |
| SPECTRA | Shannon entropy and ASCII letter-frequency distribution | Descriptive metrics only |
| SIFTRA | Input-size/digest checks; optional existing synthetic parallel-pair filter | Not official OpusFilter runtime |
| ITZAMNAAJ | Optional existing closed synthetic-plan validator | Not full LRPlan or plan correctness |
| ELNOESIS | Default not called; explicit opt-in local model on aggregate stats only | Model output unverified; no prompt containing user raw text |
| COATLICUE | Not run without independently sourced and handled visual corpus | No visual research falsely claimed |
| IACCHCODEX | Existing document Unicode-token and suffix profile | Structure, not semantics |
| PROSOPHEX | Existing Python AST inspection when input is Python | No `exec`, import, importlib, subprocess, or vulnerability verdict |
| TEZCATLIPOCA | Reuses one shuffled-character suffix null comparison | Not a significance test or independent anomaly benchmark |
| XOLOTL | Outputs an explicit requirement for an external independent witness | Genuine independence is NOT yet implemented |
| ANTHOFORGE | Produces proposed research-test sequence | No prototype built or executed |
| CRUCIBLE | Checks internal trace integrity / non-authority invariant | Not external penetration test or SHRIKE replacement |

## Governance, validation and release

**Evidence → Qualification → Reality → Authority → Effect.** No-self-witness. `HOLD` until independent exact-HEAD replay, existing suite regression, Ruff/Mypy, hostile fixtures, actual workstation proof, human reviewer, then separate explicit owner decision. A result can be generated successfully while **its verification remains HOLD**.

No changes to the canonical website, Lovable's actual source, Railway's running service, CUSTOS, SHRIKE, XAELI or BCXMET authority. **Production stays HOLD; external spend $0.** Module/tool statuses remain advisory and never grant authority.

**Known gaps:** no official full OpusFilter/LRPlan behavior; no decipherment benchmark; no reliable image ingestion; no independent external challenger runtime; no measured end-to-end local Qwen result; no observable live UI. These are **not** hidden by the unified spine.
