/** Draft: mount ONLY below the existing /admin/sovereign-studio owner gate. */
import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery } from "@tanstack/react-query";
import { askNvidiaOwner, getNvidiaOwnerStatus } from "@/lib/aurex-nvidia-owner.functions";

export function AurexNvidiaOwnerConsole() {
  const statusFn = useServerFn(getNvidiaOwnerStatus);
  const askFn = useServerFn(askNvidiaOwner);
  const [question, setQuestion] = useState("Explain why evidence from two claimed source families can still be correlated.");
  const state = useQuery({ queryKey: ["nvidia-owner-stage"], queryFn: () => statusFn(), retry: false, staleTime: 15_000 });
  const call = useMutation({ mutationFn: (q: string) => askFn({ data: { question: q } }), retry: false });
  const ready = state.data?.stage === "READY_FOR_ONE_OWNER_TEST";
  return (
    <section aria-labelledby="aurex-nvidia-owner-title" className="rounded-xl border border-border bg-card p-5">
      <h3 id="aurex-nvidia-owner-title" className="font-display text-xl">NVIDIA / XAELI — Owner-only staging</h3>
      <p className="mt-2 text-sm text-muted-foreground">
        Manual explanatory test only. No financial, security or audit authority. Never input credentials or customer records.
      </p>
      <p className="mt-3 text-sm" role="status">Connection: {state.isPending ? "CHECKING" : state.data?.stage ?? "HOLD"}</p>
      <p className="text-xs text-amber-500">Provider connection and independent accuracy: NOT VERIFIED · release HOLD</p>
      <label htmlFor="owner-nvidia-question" className="mt-4 block text-sm">Question (synthetic data only)</label>
      <textarea id="owner-nvidia-question" className="mt-2 min-h-24 w-full rounded-lg border bg-background p-3 text-foreground"
        maxLength={500} value={question} onChange={(e) => setQuestion(e.target.value)} disabled={call.isPending} />
      <button type="button" className="mt-3 rounded-lg border border-primary px-4 py-2 disabled:opacity-40"
        disabled={!ready || call.isPending || question.trim().length === 0}
        onClick={() => { call.reset(); call.mutate(question.trim()); }}>
        {call.isPending ? "Running one bounded test…" : "Run one owner-approved NVIDIA test"}
      </button>
      {call.isError && <p role="alert" className="mt-3 text-sm text-destructive">Test unavailable. No result was verified.</p>}
      {call.data && <div className="mt-4 rounded-lg border p-3" aria-live="polite">
        <p className="text-xs text-amber-500">{call.data.status} · AUTHORITY NONE · NOT VERIFIED</p>
        <p className="mt-2 whitespace-pre-wrap text-sm">{call.data.answer ?? "HOLD — no model answer admitted."}</p>
        <p className="mt-2 text-xs text-muted-foreground">Model: {call.data.model ?? "NOT VERIFIED"}</p>
      </div>}
    </section>
  );
}
