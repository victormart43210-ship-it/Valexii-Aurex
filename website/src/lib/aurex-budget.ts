/**
 * Budget reservation ledger (pattern inspired by LiteLLM-style reserve → commit/release; no dependency).
 * Reference semantics for the AUREX service; the authoritative ledger must live server-side in the service.
 * Reservations are atomic within one ledger instance: check-and-reserve happens synchronously.
 */
export interface Reservation { id: string; amountUsd: number; state: "reserved" | "committed" | "released" }

export function createBudgetLedger(limitUsd: number) {
  const limit = Number.isFinite(limitUsd) && limitUsd > 0 ? limitUsd : 0;
  const res = new Map<string, Reservation>();
  let seq = 0;
  const total = (s: Reservation["state"]) => [...res.values()].filter((r) => r.state === s).reduce((a, r) => a + r.amountUsd, 0);

  return {
    limit,
    reserved: () => total("reserved"),
    spent: () => total("committed"),
    /** Synchronous check-and-reserve: no await between check and write, so concurrent callers cannot overspend. */
    reserve(amountUsd: number): { ok: true; id: string } | { ok: false; reason: string } {
      if (!(amountUsd > 0) || !Number.isFinite(amountUsd)) return { ok: false, reason: "invalid_amount" };
      if (limit === 0) return { ok: false, reason: "no_spend_default" };
      if (total("reserved") + total("committed") + amountUsd > limit + 1e-9) return { ok: false, reason: "budget_exceeded" };
      const id = `r${++seq}`;
      res.set(id, { id, amountUsd, state: "reserved" });
      return { ok: true, id };
    },
    /** Commit actual cost ≤ reserved; overage is refused (never silently spent). */
    commit(id: string, actualUsd: number): boolean {
      const r = res.get(id);
      if (!r || r.state !== "reserved" || !(actualUsd >= 0) || actualUsd > r.amountUsd) return false;
      res.set(id, { ...r, amountUsd: actualUsd, state: "committed" });
      return true;
    },
    release(id: string): boolean {
      const r = res.get(id);
      if (!r || r.state !== "reserved") return false;
      res.set(id, { ...r, state: "released" });
      return true;
    },
  };
}
