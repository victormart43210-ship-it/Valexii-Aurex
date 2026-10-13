# Independent open-source witness bridge — 2026-10-07

**Branch status: implementation proposed for review; NOT MERGED / CI NOT VERIFIED.**
These integrations belong to **AUREX** (external challenger), never the BCXMET
runtime security authority. No production APK, credentials or manuscript originals
are uploaded or fetched by the bridge. All network/model actions require an
explicitly managed external runner. AUREX never promotes itself to sole witness.

## MobSF — Android security report ingestion

Upstream: https://github.com/MobSF/Mobile-Security-Framework-MobSF

Export a MobSF JSON report *after running MobSF in an isolated CI runner*.
Compute the candidate APK's SHA-256 separately using `sha256sum candidate.apk`.
Pass the exported report mapping and expected digest to:

```python
from aurex.adapters.oss_witnesses import mobsf_json_witness

report = {"sha256": "a" * 64, "security_score": 100}
witness = mobsf_json_witness(report, "a" * 64)
assert witness.status == "INSUFFICIENT"  # not a release PASS
```

When MobSF emits only `hash` (possibly MD5), this adapter refuses to bind it to
an APK. An independent SHA-256 link must exist. Never point MobSF directly at
production assets or export private APKs to a public scanner. MobSF JSON structure
varies by version: map/export an explicitly verified SHA-256 field before ingestion.

**Activation gate:** secure ephemeral runner; pinned MobSF image digest; private
artifact transfer; published finding classification; Android runtime tests;
independent review; exact APK digest; release authority elsewhere.


### Local executable evidence bridge

```bash
python -m aurex.adapters.oss_cli --apk ./candidate.apk --mobsf-report ./mobsf-report.json
python -m aurex.adapters.oss_cli --moon-utc 2026-10-07T00:00:00Z
```

The CLI reads local files only, independently streams the APK SHA-256, checks
that exported MobSF data explicitly contains a matching SHA-256, and emits a
bounded JSON witness. Reports bigger than 16 MiB are rejected. An exit code of
**0 means the ingestion command completed with INSUFFICIENT evidence**, **not**
that the application passed a security check. Exit code 3 signifies HOLD or
CONTESTED evidence; exit code 2 indicates input failure. Raw APK bytes are
never uploaded by this bridge.

## Astronomy Engine — LUX calendar witness

Upstream: https://github.com/cosinekitty/astronomy ; MIT.
Optional install: `pip install astronomy-engine`; dependency is NOT installed
automatically by AUREX. `astronomy_moon_witness("2026-10-07T00:00:00Z")` returns
a bounded computed moon phase context or HOLD if unavailable. Time is required
with a timezone; output is INSUFFICIENT for translation hypotheses. Correlating
planetary positions to a manuscript cannot by itself anchor translation.

## OpenTelemetry — opt-in instrumentation

Upstream: https://github.com/open-telemetry/opentelemetry-python ; Apache 2.0.
Optional install: `pip install opentelemetry-api`.
Use `with optional_trace("mobsf_ingest", enabled=True): ...` to obtain a
tracing span. No exporter or collector is configured by this bridge; the
operator must separately configure a trusted exporter, sampling, redaction,
storage, retention and opt-in. Never trace private manuscript text, APK
contents, user identifiers, passwords or service tokens.

## MADLAD-400 — translation baseline, not decipherment

Model card: https://huggingface.co/google/madlad400-3b-mt ; Apache 2.0 model card.
No model weights, API keys or inference endpoint are bundled or provisioned.
`madlad_text_candidate(text, "en", tokenizer, model)` accepts explicitly
provided local tokenizer/model objects; truncates requests to 512 tokens and
caps generated tokens at 128. Output remains HOLD pending source anchoring,
independent blind controls and reproducibility. The model does **not** claim to
translate undeciphered Voynich, Linear A or Rongorongo scripts.

For any GPU inference deployment, independently verify hardware and licensing,
pin model revision, check data-transfer/privacy policy, and benchmark known
language controls *before* attempting manuscript hypothesis comparisons.

## Governance and execution order

1. **Evidence:** exact artifact SHA-256, original source/license/revision, test
   protocol, input and timestamp.
2. **Qualification:** schema checks, privacy checks, freshness checks, alternative
   explanations, blinded controls, adversarial reviewer.
3. **Reality:** recorded runs in independent environments; no inferred PASS.
4. **Authority:** an authorized human/release controller evaluates evidence;
   AUREX never issues runtime security permissions or release approvals.
5. **Effect:** explicit release decision, conditioned on latest authority.

**Statuses:** SUPPORTED/CONTESTED/INSUFFICIENT/STALE/HOLD are evidence judgments;
none imply BCXMET safe, certified, or Play Store ready.

**CI verification:** use `python -m unittest tests.test_oss_witnesses -v`,
`ruff check aurex/adapters/oss_witnesses.py tests/test_oss_witnesses.py`,
`mypy aurex`, and `pytest -q`. Missing CI runners are NOT VERIFIED, not PASS.

**Integration topology:** BCXMET APK -> isolated MobSF execution -> exported
report -> SHA-qualified AUREX witness -> independent review. LUX calendar and
MADLAD are isolated research witnesses. OpenTelemetry observes execution
without granting authority.
