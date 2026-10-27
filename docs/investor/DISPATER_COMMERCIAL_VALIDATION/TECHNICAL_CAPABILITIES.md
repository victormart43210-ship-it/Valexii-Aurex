# DISPATER.AI — Technical Capabilities Sheet

**Platform:** AUREX-OX Governed Execution Infrastructure
**Core Module:** `aurex/dispater_intelligence.py`
**API Boundary:** `aurex/api.py` (`POST /v1/dispater/reconciliation`, `GET /v1/dispater/fleet-maintenance`, `POST /v1/dispater/value-calculator`, `GET /v1/dispater/dashboard`)

---

## 10 Exception Detection Rules

1. **UNMATCHED_PO:** Identifies field tickets executed without approved Purchase Orders.
2. **UNBILLED_FIELD_TICKET:** Identifies finalized field tickets lacking generated customer invoices.
3. **RATE_DISCREPANCY:** Reconciles line-item unit rates against effective master rate sheets.
4. **DUPLICATE_INVOICE:** Identifies duplicate supplier and customer invoice submissions.
5. **MISSING_SIGNATURE:** Flags field tickets missing customer representative signatures.
6. **UNBILLED_ITEMS:** Identifies unbilled labor, equipment hours, or materials on tickets.
7. **QUANTITY_UNIT_MISMATCH:** Flags quantity or unit of measure mismatches against dispatch logs.
8. **PARTIAL_PO_FULFILLMENT:** Flags cumulative invoice totals exceeding authorized PO caps.
9. **MULTI_RECORD_DISCREPANCY:** Detects invoice totals disagreeing with aggregated field ticket subtotals.
10. **MISSING_CONFLICTING_EVIDENCE:** Identifies corrupted or missing SHA-256 evidence attachments.

---

## Security & Data Isolation

- **Tenant Isolation:** Explicit tenant parameters and canonicalized path isolation prevent cross-tenant data leakage.
- **Fail-Closed Policy:** Incomplete or corrupted records return `INSUFFICIENT_EVIDENCE` status.
- **Spend Limits:** Default external API authorized spend is pinned at `$0.00`.
