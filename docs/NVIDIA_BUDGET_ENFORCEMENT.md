# NVIDIA budget boundary

External AI spending stays OFF. Canonical remote OpenAI-compatible transport denies before credential lookup/network; direct calls cannot bypass InferenceClient. Current XAELI ask endpoint and website helper independently deny. Environment flags and chatConfigured cannot authorize spending.

BudgetGuard is Decimal-based but memory-only, not durable/concurrent accounting. It was not misrepresented as a hard provider cap. Positive-budget remote execution is intentionally unavailable. No reservations are made or refunded by denied requests. Future admission needs durable atomic reservation, scoped fresh authorization, exact model/endpoint allowlists, conservative positive bound, bounded tokens/deadline, and ambiguous-billing reconciliation without automatic refund/retry. Provider account caps remain unverified.

The protected status endpoint returns zero allowance and missing configuration categories without secret values. No paid request was executed. Source changes are not deployed protection for the legacy Railway app. See PR150 recovery and low-cost decision for evidence and next actions.
