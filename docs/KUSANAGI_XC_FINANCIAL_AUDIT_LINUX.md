# KUSANAGI XC — AUREX Financial Audit Linux Development Kit

**Status:** SYNTHETIC-ONLY LOCAL PROTOTYPE · CODE REVIEW REQUIRED · PRODUCTION HOLD  
**Repository:** `victormart43210-ship-it/Valexii-Aurex`  
**Branch:** `feature/kusanagi-xc-financial-audit-linux-kit-20261017` (draft, not merged)

This branch carries the AUREX financial discrepancy review kit prepared on October 17, 2026, to make it **accessible by cloning the same canonical AUREX repo on Chromebook/Linux**. It is NOT a deployed auditing service, authenticated browser integration, or financial-authority engine.

## Linux — check out safely

```bash
git clone https://github.com/victormart43210-ship-it/Valexii-Aurex.git
cd Valexii-Aurex
git fetch origin feature/kusanagi-xc-financial-audit-linux-kit-20261017
git switch --track origin/feature/kusanagi-xc-financial-audit-linux-kit-20261017
```

**Install the source only into this feature checkout**, not `main`:

```bash
bash scripts/install_financial_audit_kit.sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_audit_engine.py tests/test_source_bytes.py
python -m aurex.financial_review.cli serve --port 8767
```

Open `http://127.0.0.1:8767` on the same Linux device. Server binds to **127.0.0.1**, not a public interface.

## Scope

- Strict, frozen Pydantic v2 input records, `Decimal` money, explicit unknowns and ISO timestamps.
- Compare one synthetic invoice against a synthetic PO or field ticket.
- Exact discrepancy, source-reference, duplicate-number advisory and reconciliation checks.
- Deterministic, complete, domain-separated SHA-256 evidence receipt (authenticity remains UNVERIFIED).
- Explicit **DISCREPANCY / NO_DISCREPANCY_DETECTED / INDETERMINATE** finding, with **authority = HOLD** and **human review required** under every outcome.
- Untrusted suggestion-only plain-text parser; **no PDF/OCR**, customer document ingestion or payments.
- A separate local-only FastAPI reviewer/HTML interface; **no production API route introduced**.

The separate website source/Cloudflare Wrangler work remains in the October 17 handoff and PRs #72/#76/#79, not silently merged here. The local reviewer is NOT proof that the Cloudflare Worker → Railway → owner browser handshake works.

## Source integrity and independently repeatable tests

Source is distributed in `artifacts/financial-audit/aurex-audit-install.tar.xz.b64`, a base64-encoded XZ tar containing the additive financial modules, tests, synthetic fixtures and local HTML. The installer checks **the archive SHA-256 against the pinned manifest**, validates archive paths before unpacking, and refuses to overwrite any existing target files. No GitHub credential is used by the installer. Commit a *separate* reviewed change if integration tests pass; no automatic merge/deploy.

Upstream sandbox validation before import: **47/47 Python tests passed**, local review HTTP smoke, and synthetic Wrangler checks. Those results belong to the offline package, **not** this GitHub branch's current CI until independently run at the exact branch head.

### Governance

**Evidence → Qualification → Reality → Authority → Effect**. No self-witness, no synthetic audit finding can authorize payment, no real user records or USB scans, no paid inference. Unknown/stale/infra failure = HOLD.

**CUSTOS RELEASE: HOLD.**
