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

Source is included IN THIS SAME BRANCH as five ordered ASCII Base64 chunks at `artifacts/financial-audit/chunk_01.b64` through `chunk_05.b64` (18,208 characters total). Together they decode to a 13,656-byte XZ tar with **SHA-256 `69fd708ab0e9857036af3696d80c7cf914de6ca43d8738a605e93acf9722c7f2`**. The GitHub readback checksum was verified against the original local archive. The installer rechecks the same digest, accepts only additive module/test/synthetic fixture/local HTML paths, and refuses overwrite or dirty/protected-branch execution. The source is on GitHub now; Linux does not require downloading a ZIP from ChatGPT. The script extracts files into the local working tree; it does NOT automatically commit them to `main` or deploy.

Upstream sandbox validation before import: **47/47 Python tests passed**, local review HTTP smoke, and synthetic Wrangler checks. Those results belong to the offline package, **not** this GitHub branch's current CI until independently run at the exact branch head.

### Governance

**Evidence → Qualification → Reality → Authority → Effect**. No self-witness, no synthetic audit finding can authorize payment, no real user records or USB scans, no paid inference. Unknown/stale/infra failure = HOLD.

**CUSTOS RELEASE: HOLD.**
