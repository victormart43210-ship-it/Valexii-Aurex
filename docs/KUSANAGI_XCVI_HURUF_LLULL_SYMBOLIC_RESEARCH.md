# KUSANAGI XCVI — HURUF × LLULL SYMBOLIC RESEARCH

**DRAFT / HOLD.** Source-only, read-only, offline Python tools in the existing AUREX backend repository. This stacked branch depends on unmerged PR #85 and #84. **No merge, deployment, Qwen invocation, model download, paid inference, public API route, or code execution.**

## Historically grounded components

**HURUF / Abjad:** Classical eastern Arabic abjad mapping (28 Arabic letters) and explicit optional orthographic Alef normalization. Unmapped signs, including additional Persian letters, **block** the numeric total. Calculation never implies metaphysical truth or actual decipherment. For historical Hurufism see Encyclopaedia Iranica: https://www.iranicaonline.org/articles/horufism/ ; Abjad: https://www.iranicaonline.org/articles/abjad/

**LLULL / Combinatorial figure:** Nine letters B C D E F G H I K, with explicit separate **dignity**, **relation**, **question** meanings, plus a 9-position three-ring modern analogue. This is deliberately **not** a reconstruction of Llull's historical Fourth Figure or evidence of a Hurufi-Llull cipher. See Stanford Encyclopedia of Philosophy, Section 5: https://plato.stanford.edu/entries/llull/

**Document:** Unicode token frequency and suffix-first exploration without reversing the original reading order, with one deterministic scrambled-character null control (NOT a p-value). **Code:** Python `ast.parse`-only definitions, imports, nodes and potentially sensitive-call *hints*; no actual execution or vulnerability verdict. **Cipher:** controlled Caesar/ROT experiments; without a known key, output 26 SHA-256 candidate fingerprints, not a chosen plaintext. **Crosswalk:** run document/code structure, abjad when Arabic appears, and Llull hypotheses together, but label historical linkage and decipherment **NOT ESTABLISHED**.

This does not automatically translate Voynich, Linear A or Rongorongo, decode arbitrary secret files, read PDF/OCR, or make Qwen more intelligent. The document corpus must be independently transcribed, with archival citations, appropriate script-aware segmentation and held-out positive/negative tests.

## Start locally from this branch (Python 3.12+)

```bash
# Direct historical wheel demonstration, no input:
python -m workstation.huruf_llull_cli --mode llull --wheel-offsets 0 1 2
# Your own small, lawfully held UTF-8 samples:
python -m workstation.huruf_llull_cli --mode document --file /path/to/sample.txt
python -m workstation.huruf_llull_cli --mode crosswalk --file /path/to/sample.txt
python -m workstation.huruf_llull_cli --mode abjad --file /path/to/arabic.txt
python -m workstation.huruf_llull_cli --mode python --file /path/to/script.py
python -m workstation.huruf_llull_cli --mode crosswalk --file /path/to/script.py
python -m workstation.huruf_llull_cli --mode caesar --file /path/to/encoded.txt
```

Plain UTF-8 files: .txt, .md, .py, .csv, .json, .tex, .v, .xml, .html. Binary .pdf/.docx/images/scans are rejected; extract their text with approved document tools, preserving page/source evidence, **before** using this CLI. Max 64KiB file, 10,000 tokens and 6,000 Python AST nodes. Symlinks and invalid UTF-8 fail closed. No untrusted Python import/exec; no script execution or external calls.

SHA-256 receipts are **integrity fingerprints, not signatures or independent witnesses**. Outputs never claim manuscript translation, executable code behavior, scientific validity or authority. Do not feed historical/numerological correspondences into BCXMET security decisions, financial approvals, hiring, user risk, or production deployment.

## Owner-approved APIS PRIME naming lock (2026-10-18)

The full **14-system internal display-name mapping**, stable AP01–AP14 IDs, technical attribution and governance checks are versioned in [`architecture/APIS_PRIME_NAMING_CANON.md`](architecture/APIS_PRIME_NAMING_CANON.md) and [`architecture/apis_prime_registry.json`](architecture/apis_prime_registry.json). The names are **owner-approved internal terminology**, not 14 deployed agents, installed packages, verified capabilities, authorization grants, or trademark-cleared public names. In future UI work display these exact research-system names without country status labels. The underlying technical source names remain in code and scientific citations.

## Verification and release gates

Authoring-container source-equivalent prototype: **34 synthetic tests passed** under Python 3.13.5 / pytest 9.0.2 with autoload disabled, compileall PASS. The GitHub version was manually transcribed from the tested prototype. **Exact remote commit tests, complete existing AUREX suite, Ruff, Mypy, actual laptop workstation, document corpus, manuscript decipherment and production integration: NOT RUN / NOT VERIFIED** until independent reproduction.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_huruf_llull.py tests/test_huruf_llull_cli.py
python -m compileall -q aurex/huruf_llull.py workstation/huruf_llull_cli.py
ruff check aurex/huruf_llull.py workstation/huruf_llull_cli.py tests/test_huruf_llull.py tests/test_huruf_llull_cli.py
mypy --strict aurex/huruf_llull.py workstation/huruf_llull_cli.py
```

Next: independent exact-HEAD replay, historic source-specific positive controls and randomized negative controls, freeze transformation rules, then held-out predictions and expert review. If owner-only research UI is later added to existing Lovable, panels should say **HURUF, LLULL, OPUSFILTER, LRPLAN, QWEN**, with no country-name status labels. Actual Lovable is NOT modified by this branch.

Governance: **Evidence → Qualification → Reality → Authority → Effect.** The system may never be its own sole witness. ORB MOTION AUTHORITY = NONE. External spend $0. Release **HOLD**.
