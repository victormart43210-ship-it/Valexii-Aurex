import { useRef, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { PromptSchema } from "@/lib/aurex-api-schema";
import { checkAurexOwner } from "@/lib/aurex-control.functions";
import {
  commandConnection,
  submitAurexCommand,
  readAurexCommand,
  cancelAurexCommand,
} from "@/lib/aurex-command.functions";

/** No operational data is rendered until owner authorization succeeds server-side. */
export function AurexCommand() {
  const check = useServerFn(checkAurexOwner);
  const owner = useQuery({
    queryKey: ["aurex-command-owner"],
    queryFn: () => check(),
    retry: false,
    staleTime: 0,
    gcTime: 0,
  });
  return (
    <section
      className="site-grid border-b border-border py-10"
      aria-labelledby="aurex-command-heading"
    >
      <h2 id="aurex-command-heading" className="font-display text-2xl text-primary">
        AUREX COMMAND INTERFACE
      </h2>
      <p className="mt-3 text-sm text-muted-foreground">
        Owner-only local inference. Responses are advisory; execution does not establish factual
        verification or security authority.
      </p>
      {owner.data?.owner && !owner.isError ? (
        <Command />
      ) : (
        <OwnerSignIn onSignedIn={() => owner.refetch()} pending={owner.isPending} />
      )}
    </section>
  );
}
function OwnerSignIn({ onSignedIn, pending }: { onSignedIn: () => unknown; pending: boolean }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="mt-5 grid max-w-lg gap-3"
      onSubmit={async (event) => {
        event.preventDefault();
        setBusy(true);
        setError("");
        const form = event.currentTarget;
        const data = new FormData(form);
        try {
          const { supabase } = await import("@/integrations/supabase/client");
          const result = await supabase.auth.signInWithPassword({
            email: String(data.get("email")),
            password: String(data.get("password")),
          });
          if (result.error) throw new Error("Sign in failed");
          form.reset();
          await onSignedIn();
        } catch {
          setError("Sign-in unavailable or credentials rejected. This interface remains locked.");
        } finally {
          setBusy(false);
        }
      }}
    >
      <p role="status" className="text-sm text-amber">
        {pending
          ? "Checking owner access…"
          : "LOCKED · Sign in with the configured owner account. Backend connection NOT VERIFIED."}
      </p>
      <label htmlFor="aurex-owner-email">Owner email</label>
      <input
        id="aurex-owner-email"
        name="email"
        type="email"
        autoComplete="username"
        required
        className="min-h-11 rounded border border-border bg-background p-3"
      />
      <label htmlFor="aurex-owner-password">Password</label>
      <input
        id="aurex-owner-password"
        name="password"
        type="password"
        autoComplete="current-password"
        required
        className="min-h-11 rounded border border-border bg-background p-3"
      />
      <Button disabled={busy || pending} type="submit">
        {busy ? "Signing in…" : "Owner sign in"}
      </Button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
function Command() {
  const [prompt, setPrompt] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const request = useRef<{ prompt: string; key: string } | null>(null);
  const connectionFn = useServerFn(commandConnection);
  const submitFn = useServerFn(submitAurexCommand);
  const readFn = useServerFn(readAurexCommand);
  const cancelFn = useServerFn(cancelAurexCommand);
  const connection = useQuery({
    queryKey: ["aurex-command-connection"],
    queryFn: () => connectionFn(),
    retry: false,
    gcTime: 0,
  });
  const job = useQuery({
    queryKey: ["aurex-command-job", jobId],
    enabled: !!jobId,
    queryFn: () => readFn({ data: { jobId: jobId! } }),
    retry: false,
    gcTime: 0,
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return status?.ok && ["queued", "running"].includes(status.value.state) ? 5000 : false;
    },
  });
  const submit = useMutation({
    mutationFn: async () => {
      if (!request.current || request.current.prompt !== prompt)
        request.current = { prompt, key: crypto.randomUUID() };
      return submitFn({
        data: { prompt: request.current.prompt, idempotencyKey: request.current.key },
      });
    },
    onSuccess: (response) => {
      if (response.ok) {
        setJobId(response.value.id);
        request.current = null;
      }
    },
  });
  const cancel = useMutation({
    mutationFn: () => cancelFn({ data: { jobId: jobId!, idempotencyKey: crypto.randomUUID() } }),
    onSuccess: () => job.refetch(),
  });
  const status = job.data?.status;
  const result = job.data?.result;
  const evidence = job.data?.evidence;
  const active = !!jobId && (!status?.ok || ["queued", "running"].includes(status.value.state));
  return (
    <div className="mt-6 max-w-3xl space-y-4">
      <p role="status">
        Connection: {connection.isError ? "UNAVAILABLE" : (connection.data?.state ?? "UNVERIFIED")}{" "}
        · Inference:{" "}
        {connection.data?.inferenceAvailable
          ? "accepting jobs (model not verified)"
          : "unavailable or not verified"}
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit.mutate();
        }}
        className="grid gap-3"
      >
        <label htmlFor="aurex-command-prompt">Ask AUREX</label>
        <textarea
          id="aurex-command-prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={5}
          maxLength={8192}
          className="w-full rounded border border-border bg-background p-3"
          aria-describedby="aurex-command-limit"
        />
        <p id="aurex-command-limit" className="text-xs text-muted-foreground">
          Maximum 8192 UTF-8 bytes. Local inference only. External inference budget: $0.00.
        </p>
        <Button
          type="submit"
          disabled={
            submit.isPending ||
            active ||
            !PromptSchema.safeParse(prompt).success ||
            !connection.data?.inferenceAvailable
          }
        >
          {" "}
          {submit.isPending ? "Submitting…" : "Submit task"}
        </Button>
      </form>
      {(submit.isError || (submit.data && !submit.data.ok)) && (
        <p role="alert">
          Submission failed:{" "}
          {submit.data && !submit.data.ok ? submit.data.error : "session or service unavailable"}.
          Retry the unchanged prompt to reuse its request key.
        </p>
      )}
      {jobId && (
        <div className="space-y-3 rounded border border-border p-4" aria-live="polite">
          <p className="break-all">Job: {jobId}</p>
          <p>Status: {status?.ok ? status.value.state.toUpperCase() : "UNVERIFIED"}</p>
          {(job.isError || (status && !status.ok)) && (
            <p role="alert">Job status unavailable. No successful completion is assumed.</p>
          )}
          {status?.ok && ["failed", "cancelled", "expired"].includes(status.value.state) && (
            <p>Task did not complete successfully. No model response is claimed.</p>
          )}
          {result?.ok && result.value.result && (
            <>
              <p>
                Model: {result.value.result.model} · Provider: {result.value.result.provider}
              </p>
              <p className="whitespace-pre-wrap break-words">{result.value.result.text}</p>
              <p>Verification: NOT VERIFIED · Authority granted: NO</p>
            </>
          )}
          {(!result?.ok || !result.value.result) && (
            <p>Response unavailable or pending. NOT VERIFIED.</p>
          )}
          <h3 className="font-display text-lg">Execution evidence</h3>
          {evidence?.ok && evidence.value.evidence.length > 0 ? (
            evidence.value.evidence.map((e) => (
              <div key={e.id} className="break-all text-sm">
                <p>
                  {e.id} · {e.collectedAt}
                </p>
                <p>SHA-256: {e.sha256}</p>
                <p>
                  Integrity: {e.integrity ?? "NOT VERIFIED"} · Factual verification: NOT VERIFIED
                </p>
              </div>
            ))
          ) : (
            <p>Evidence unavailable. NOT VERIFIED.</p>
          )}
          <div className="flex flex-wrap gap-3">
            <Button type="button" onClick={() => job.refetch()} disabled={job.isFetching}>
              Refresh status
            </Button>
            <Button
              type="button"
              onClick={() => cancel.mutate()}
              disabled={!active || cancel.isPending}
            >
              Cancel task
            </Button>
          </div>
          {(cancel.isError || (cancel.data && !cancel.data.ok)) && (
            <p role="alert">Cancellation was not confirmed. Refresh status.</p>
          )}
        </div>
      )}
      <Button type="button" onClick={() => connection.refetch()} disabled={connection.isFetching}>
        Check connection
      </Button>
    </div>
  );
}
