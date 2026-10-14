import { createFileRoute } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/site";
import { checkAurexOwner, getAurexCapabilityStatus, getAurexDiagnostics, getSecurityLabState, observeSite } from "@/lib/aurex-control.functions";
import { applyGate, proposeGate } from "@/lib/aurex-control";
import { AurexCapabilitiesPanel } from "@/components/aurex-capabilities-panel";
import { AurexSecurityLab } from "@/components/aurex-security-lab";
import { AurexOxStatus } from "@/components/aurex-ox-status";

export const Route = createFileRoute("/admin/aurex-control")({
  ssr: false,
  head: () => ({
    meta: [
      { title: "AUREX Command Center — Owner only | VALEXII.AI" },
      { name: "description", content: "Restricted owner console." },
      { name: "robots", content: "noindex, nofollow" },
      { property: "og:title", content: "Restricted" },
      { property: "og:description", content: "Restricted owner console." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: AurexControl,
});

function AurexControl() {
  const check = useServerFn(checkAurexOwner);
  const owner = useQuery({ queryKey: ["aurex-owner"], queryFn: () => check(), retry: false });
  if (owner.isPending) return <PageShell><p className="site-grid section-space">Checking access…</p></PageShell>;
  if (owner.isError || !owner.data?.owner)
    return (
      <PageShell>
        <section className="site-grid section-space" data-testid="aurex-locked">
          <h1 className="font-display text-3xl">Access denied</h1>
          <p className="mt-4 text-sm text-muted-foreground">
            This console is restricted to the verified site owner. No operations are available.
          </p>
          <p className="mt-4 text-sm text-amber" data-testid="aurex-setup-blocker">
            Setup blocker: {owner.isError ? "owner sign-in is required and not active in this session." : owner.data?.ownerConfigured ? "this account is not the configured owner." : "the owner identity (AUREX_OWNER_USER_ID) is not configured."} The Security Lab stays locked.
          </p>
        </section>
      </PageShell>
    );
  return <Console />;
}

function Console() {
  const observeFn = useServerFn(observeSite);
  const statusFn = useServerFn(getAurexCapabilityStatus);
  const status = useQuery({ queryKey: ["aurex-cap-status"], queryFn: () => statusFn(), retry: false });
  const observe = useMutation({ mutationFn: () => observeFn() });
  const diagFn = useServerFn(getAurexDiagnostics);
  const diag = useMutation({ mutationFn: () => diagFn() });
  const labFn = useServerFn(getSecurityLabState);
  const lab = useQuery({ queryKey: ["aurex-lab"], queryFn: () => labFn(), retry: false });
  const propose = proposeGate({ githubRepo: undefined, githubAppConfigured: false });
  const apply = applyGate({});
  return (
    <PageShell>
      <section className="site-grid section-space">
        <h1 className="font-display text-3xl">AUREX Command Center — Phase 1</h1>
        <p className="mt-3 text-sm text-muted-foreground">Owner verified on the server. Research engine: NOT_CONNECTED.</p>
        <h2 className="mt-8 font-display text-2xl">OBSERVE</h2>
        <p className="mt-2 text-sm text-muted-foreground">Server-side checks of fixed valexii.com pages only. Redirects are reported, not followed. Firecrawl is not connected.</p>
        <Button className="mt-4 min-h-11" onClick={() => observe.mutate()} disabled={observe.isPending}>
          {observe.isPending ? "Checking…" : "Run health audit"}
        </Button>
        {observe.isError && <p className="mt-3 text-sm text-destructive">Audit failed.</p>}
        {observe.data && (
          <div className="mt-4 overflow-x-auto">
            <p className="text-xs text-muted-foreground">Checked {observe.data.checkedAt}</p>
            <table className="mt-2 w-full text-left text-sm">
              <thead><tr><th>URL</th><th>Status</th><th>ms</th><th>Note</th></tr></thead>
              <tbody>{observe.data.results.map((r) => (
                <tr key={r.url} className="border-t border-border"><td>{r.url}</td><td>{r.status ?? "—"}</td><td>{r.ms ?? "—"}</td><td>{r.note}</td></tr>
              ))}</tbody>
            </table>
          </div>
        )}
        <h2 className="mt-10 font-display text-2xl">PROPOSE — disabled</h2>
        <p className="mt-2 text-sm text-amber">{"reason" in propose ? propose.reason : ""} A GitHub-linked site repository and GitHub App credentials are required.</p>
        <h2 className="mt-10 font-display text-2xl">APPLY — disabled</h2>
        <p className="mt-2 text-sm text-amber">{apply.reason} Explicit owner approval is always required.</p>
        <h2 className="mt-10 font-display text-2xl">AUREX service & cost governor</h2>
        {status.isPending ? <p className="mt-2 text-sm">Checking…</p> : status.isError || !status.data ? (
          <p className="mt-2 text-sm text-amber">Status unavailable — treated as NOT CONFIGURED.</p>
        ) : (
          <p className="mt-2 text-sm" data-testid="aurex-service-state">
            Service: {status.data.service} · Budget: ${status.data.budgetUsd.toFixed(2)}
            {status.data.budgetUsd === 0 ? " (no-spend default; all paid actions are refused on the server)" : " (enforced on the server)"} · Checked {status.data.checkedAt}
          </p>
        )}
        <h2 className="mt-10 font-display text-2xl">Connection diagnostics</h2>
        <p className="mt-2 text-sm text-muted-foreground">Runs read-only checks against the external AUREX service. Results show codes only; addresses and keys are never returned.</p>
        <Button className="mt-4 min-h-11" variant="glass" onClick={() => diag.mutate()} disabled={diag.isPending}>
          {diag.isPending ? "Checking…" : "Run diagnostics"}
        </Button>
        {diag.isError && <p className="mt-3 text-sm text-amber">Diagnostics unavailable — treated as NOT CONFIGURED.</p>}
        {diag.data && (
          <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2" data-testid="aurex-diagnostics">
            <div><dt className="text-muted-foreground">Service address set</dt><dd>{diag.data.urlSet ? "yes" : "no"}</dd></div>
            <div><dt className="text-muted-foreground">Service key set</dt><dd>{diag.data.tokenSet ? "yes" : "no"}</dd></div>
            {Object.entries(diag.data.steps).map(([k, v]) => (
              <div key={k}><dt className="text-muted-foreground">{k}</dt><dd className={v === "ok" ? "text-primary" : "text-amber"}>{v}</dd></div>
            ))}
            <div><dt className="text-muted-foreground">Remote budget limit</dt><dd>{diag.data.remoteBudgetLimitUsd === null ? "unavailable" : `$${diag.data.remoteBudgetLimitUsd.toFixed(2)}`}</dd></div>
            <div><dt className="text-muted-foreground">Evidence-backed capabilities</dt><dd>{diag.data.evidenceBackedCapabilities.length ? diag.data.evidenceBackedCapabilities.join(", ") : "none"}</dd></div>
            <div><dt className="text-muted-foreground">Checked</dt><dd>{diag.data.checkedAt}</dd></div>
          </dl>
        )}
      </section>
      <AurexOxStatus context="owner" />
      {lab.isError ? <p className="site-grid text-sm text-amber">Security Lab unavailable — locked.</p> : <AurexSecurityLab data={lab.data} />}
      <AurexCapabilitiesPanel live={status.data ? Object.fromEntries(status.data.statuses.map((s) => [s.id, s.status])) : undefined} />
    </PageShell>
  );
}
