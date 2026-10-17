# VALEXII-AUREX

**An evidence-first research and engineering engine for governed AI systems.**

AUREX is the **external evidence, challenge, and evaluation** component of the VALEXII.AI ecosystem. Its purpose is to produce reproducible claims, challenge unsupported conclusions, and keep AI-assisted recommendations separate from human or system authority. It is not a general-purpose autonomous financial system, a production-certified security platform, or proof that connected apps have completed end-to-end deployment.

> **Governing rule:** The system may never be its own sole witness.
>
> **Pipeline:** Evidence → Qualification → Reality → Authority → Effect.

## What lives here

- **Typed service contracts:** Python and FastAPI interfaces for read-only service health, capabilities, evidence, budget information, and jobs.
- **Adversarial review:** Repeatable tests and challenger interfaces that attempt to falsify results.
- **Provenance and governance:** Versioned evidence, fingerprints, freshness checks, explicit unknowns, and policy boundaries.
- **Evaluation harnesses:** Reproducible local or budgeted tests; internal practice is **not** an official external benchmark.
- **Local development:** Workstation, CLI, and model adapters; paid model calls are not enabled by the repository itself.
- **Experimental financial evidence review:** A separate **design and test plan**, not a shipped financial service.

Architecture and capabilities must be judged from the **exact tested source version**, not a feature name, demo, or pull-request count.

## AUREX/OX and related projects

| Component | Role | Boundary |
| --- | --- | --- |
| **AUREX** (this repository) | External evidence, evaluation, research and review engine | Evidence/advice is **not** security or payment authority |
| **AUREX/OX** at VALEXII.COM | Website presentation and owner review of evidence/status | Site health alone does **not** prove authenticated, canonical backend execution |
| **BCXMET** | Android cybersecurity product (legacy repository name `CoreGuard-Android`) | Android security actions retain their own governing authority |
| **DISPATER.AI** | Industrial / oilfield product direction | Proposed integrations require independent verification |
| **XAITA.AI** | Financial/market product direction | Not evidence of deployed trading or automated finance |

A separate public website may discuss these products, but repository links and product demonstrations do **not** establish that the systems are deployed together.

## KUSANAGI OMEGA — Proof-gated financial review

The selected **Hypothesis C** aims to test a narrow, human-reviewed financial discrepancy workflow:

```text
Synthetic invoice + synthetic purchase order / field ticket
        ↓
Typed, exact-value comparison
        ↓
Complete, versioned evidence receipt
        ↓
DISCREPANCY / NO_DISCREPANCY_DETECTED / INDETERMINATE
        ↓
HOLD — HUMAN REVIEW REQUIRED
```

**Current status: design approved; implementation and real-data validation NOT VERIFIED.** No automatic invoice approval, bank connection, payment execution, or paid inference is authorized.

- [Proposed proof-gated review design (draft PR #77)](https://github.com/victormart43210-ship-it/Valexii-Aurex/pull/77)
- [Ongoing integration and evidence tracking (Issue #75)](https://github.com/victormart43210-ship-it/Valexii-Aurex/issues/75)

A SHA-256 digest helps detect changes **only to the data actually bound into the digest**; it cannot, by itself, establish document authenticity or independent custody.

## Engineering method: Speed · Altitude · Depth · Range

| Dimension | What we actually optimize |
| --- | --- |
| **Speed** | Measured cycle time, latency, rendering and operating cost—not untested speedup claims |
| **Altitude** | Useful, verifiable user outcomes rather than the number of features or commits |
| **Depth** | Primary evidence, negative tests, precise failure analysis and independent outside judgment |
| **Range** | Cross-disciplinary learning without crossing privacy, scope or authority boundaries |

A successful engineering report records **exact commit SHA**, test command and output, independent checker, limitations, and whether the result was **coded, locally tested, CI verified, merged, deployed or proven end to end**. These states are not interchangeable.

## Development

**Requirements:** Python 3.12+ and the dependency constraints in [pyproject.toml](pyproject.toml).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
python -m ruff check .
python -m mypy --strict aurex
```

The commands above are **instructions**, not a claim that CI passes on every branch. Review [SECURITY.md](SECURITY.md) before reporting vulnerabilities or sharing evidence.

## Honest project status

- **Source:** Ongoing open-source, pre-release engineering.
- **Website integration:** AUREX/OX frontend and read-only service contracts exist, but full authenticated published-site → canonical backend verification has **not** been established in this README.
- **Deployment:** An older read-only Railway bridge has been operated. That does **not** prove the canonical worker → durable SQLite → independent evidence → website path.
- **Financial extraction:** Prototypes and synthetic tests exist on development branches; verified production financial accuracy is **not** claimed.
- **Security:** Model outputs and static summaries **never** independently confer owner authority or approval.

This public repository intentionally excludes private user records, credentials, protected detection internals and patent-sensitive materials. Financial originals must remain private and read-only unless their owner separately authorizes a secure evaluation.

**Suggested GitHub About description:** `Evidence-first AUREX engine for governed AI evaluation, reproducible challenge, provenance, and human-reviewed decisions (pre-release).`
