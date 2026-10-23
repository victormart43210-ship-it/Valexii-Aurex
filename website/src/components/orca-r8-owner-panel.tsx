/** Private ORCA R8 transport-status panel; observation NEVER implies verification. */
import { useServerFn } from "@tanstack/react-start";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { getOrcaR8OwnerStatus } from "@/lib/orca-r8-owner.functions";

export function OrcaR8OwnerPanel() {
  const read = useServerFn(getOrcaR8OwnerStatus);
  const state = useQuery({
    queryKey: ["orca-r8-owner-observed-status"],
    queryFn: () => read(),
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 10_000,
  });
  const s = state.data;
  const snap = s && "snapshot" in s ? s.snapshot : null;
  const percent = snap ? Math.round((snap.completedBatches / snap.totalBatches) * 1000) / 10 : 0;
  const receivedAt = s && "receivedAt" in s ? s.receivedAt : null;
  const live = s?.state === "OBSERVED" && !!snap;
  return (
    <section
      className="mt-6 rounded-xl border border-border bg-card/60 p-5"
      aria-labelledby="orca-r8-private-title"
      data-testid="orca-r8-owner-private"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs text-gold">ORCA · R8 · PRIVATE METADATA</p>
          <h2 id="orca-r8-private-title" className="mt-1 font-display text-xl">
            Operation Sovereign Audit
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Outbound-only workstation counters. No documents, contents or local ports exposed.
          </p>
        </div>
        <Button onClick={() => state.refetch()} disabled={state.isFetching}>
          {state.isFetching ? "Checking…" : "Refresh status"}
        </Button>
      </div>
      <p role="status" className="mt-4 text-sm text-amber">
        {state.isError ? "NOT VERIFIED · owner read unavailable"
          : state.isPending ? "NOT VERIFIED · checking status"
          : s?.state === "OBSERVED" ? "OBSERVED · NOT INDEPENDENTLY VERIFIED"
          : s?.state === "STALE" ? "STALE · last report expired"
          : s?.state === "NO_DATA" ? "NO DATA · no workstation report"
          : "NOT CONNECTED · verification HOLD"}
      </p>
      {snap && (
        <>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div><p className="text-xs text-muted-foreground">Completed batches</p><p className="text-2xl font-semibold">{snap.completedBatches} / {snap.totalBatches}</p></div>
            <div><p className="text-xs text-muted-foreground">Selected rows remaining</p><p className="text-2xl font-semibold">{snap.rowsRemaining ?? "—"}</p></div>
            <div><p className="text-xs text-muted-foreground">Estimated time remaining</p><p className="text-2xl font-semibold">{snap.etaSeconds == null ? "—" : Math.ceil(snap.etaSeconds / 60) + " min"}</p></div>
          </div>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-muted" aria-label={`Reported batch progress ${percent}%`}>
            <div className="h-full bg-primary" style={{ width: `${percent}%` }} />
          </div>
          <p className="mt-2 text-xs text-muted-foreground">Reported batches: {percent}% · Run state: {snap.status}</p>
          <p className="mt-1 text-xs text-muted-foreground">Server receipt: {receivedAt ?? "none"} · {live ? "Recent report" : "Do not treat as live"}</p>
        </>
      )}
      <p className="mt-4 text-xs text-muted-foreground">
        Evidence → Qualification → Reality → Authority → Effect. This display has NO authority to
        declare batches valid, sources trustworthy, worker healthy, or a production release ready.
      </p>
    </section>
  );
}
