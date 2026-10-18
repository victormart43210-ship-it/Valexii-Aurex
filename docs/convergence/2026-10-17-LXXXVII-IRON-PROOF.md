# KUSANAGI LXXXVII — Read-Only Iron Connection Proof

**Execution status:** Source proposed in a draft PR; `main`, Cloudflare, Railway and Lovable production unchanged.

The operator probe `scripts/aurex_readonly_probe.py` performs **exactly five HTTPS GETs** against the pinned existing Railway bridge host:
`/v1/health`, `/v1/capabilities`, `/v1/evidence`, `/v1/budgets`, `/v1/jobs`.
It reads the Railway Bearer credential from a **hidden local prompt** (or already configured environment variable). It never prints the credential, uploads financial records, follows redirects, POSTs jobs or changes production services. Response bodies are capped at 256 KiB and validated against an independent strict contract; private body contents are never printed. Valid results are hashed, **not authenticated provenance**. The old read-only bridge must report a zero budget and no enabled capabilities, jobs or evidence; otherwise the probe reports HOLD.

### Synthetic preflight (no network)

From the AUREX repository root, with local dev dependencies available:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_aurex_readonly_probe.py
```

This invokes FastAPI TestClient against the checked-out legacy bridge source and synthetic 32-character credentials. Tests also include schema corruption, 401 refusal, oversized data and no conversion of connectivity into production authority. CI must independently pass on the exact PR SHA.

### Owner-operated direct Railway check (optional; five GETs, no deployment)

```bash
python3 scripts/aurex_readonly_probe.py --live --report ./aurex-railway-proof.json
```

When prompted, enter the **existing Railway `AUREX_SERVICE_TOKEN`** locally; input is hidden. **Never paste a token into GitHub, chat, shell command arguments, or public logs.** If already exported in your local terminal, the probe will read the environment variable rather than prompting. The resulting report is sanitized and written as a new mode-0600 file; avoid committing it. An invalid or absent secret returns HOLD and makes no request.

### What this can and cannot demonstrate

A five-GET success proves that the **local operator's machine** reached the **pinned Railway bridge host** with an accepted Bearer token and obtained five valid responses. It **does not prove Cloudflare Worker execution or identity**, installed Worker secret bindings, site-rendered data, current canonical `main`, mutable jobs/SQLite, independent evidence, financial integrity, a human-review decision, release authority or a production deployment.

To prove **Cloudflare → Railway → AUREX/OX** subsequently, an authorized operator must independently establish the exact Worker route/deployed build, server-only configured binding names, five sanitized authenticated server-side GET results, published owner-only view, absence of browser tokens, end-to-end trace/correlation, and separate independent reviewer. Do not deploy or change live domains until the owner separately approves the release.

**Security constraints:** Never transmit the Railway credential to an arbitrary URL. HTTPS target is hardcoded to `aurex-api-production-c535.up.railway.app`; redirects and environment-configured proxies are disabled. Default invocation without `--live` refuses network work. **No spending; no arbitrary execution; RELEASE HOLD.**

### Speed / Altitude / Depth / Range

- **Speed:** Minimal CLI, no installed packages required for live check, five bounded GETs.
- **Altitude:** Actual validated backend responses, not inflated “percentage completed.”
- **Depth:** Exact schemas, synthetic adversarial cases, explicit unknowns and a SHA-identified source.
- **Range:** Connects API authentication, network safety, test engineering and website trust boundaries without granting frontend or model authority.

**Expected live source boundary as last independently observed:** Railway bridge commit `57a079f93b947594f1a6f854aa46a6f606f86f76` with **read-only** endpoints. Repository `main` at capture was `df0654390049118a142ec3b3356f0f40b4789fe4`. Exact release SHA must be reverified at execution time.
