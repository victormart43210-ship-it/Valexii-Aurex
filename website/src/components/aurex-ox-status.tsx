/**
 * AUREX OX connection status. Static, browser-safe facts only: no network calls,
 * no local paths, no hostnames, no secrets. "Local build" items describe work the
 * owner reports on a separate machine; this website cannot reach or verify them.
 */
export const AUREX_OX_STATUS = [
  { id: "advisory-api", name: "Advisory service (Phase 5)", state: "NOT CONNECTED", note: "Reported as a local build only. A local machine is not reachable from valexii.com, so nothing here is live." },
  { id: "web-ox", name: "AUREX OX public interface (Phase 6)", state: "NOT DEPLOYED", note: "The public AUREX page on this site is the canonical interface; local static builds are not served here." },
  { id: "shells", name: "Public/private shells (Phase 7)", state: "NOT INCLUDED", note: "Private shell files are never bundled into this public site." },
  { id: "hosted-backend", name: "Hosted HTTPS backend", state: "NOT CONFIGURED", note: "Requires an owner-hosted HTTPS service and server-side settings before any status can change." },
  { id: "evidence", name: "Independent evidence", state: "NOT VERIFIED", note: "Capabilities become REAL only with fresh evidence from a healthy hosted service." },
] as const;

export function AurexOxStatus({ context }: { context: "public" | "owner" }) {
  return (
    <section aria-labelledby={`aurex-ox-${context}`} className="section-space border-b border-border" data-testid="aurex-ox-status">
      <div className="site-grid">
        <p className="text-xs text-primary">AUREX OX · connection status</p>
        <h2 id={`aurex-ox-${context}`} className="mt-3 font-display text-3xl">Built locally. Not connected here.</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
          {context === "public"
            ? "This page shows no live AUREX data. Every row below stays NOT CONNECTED until a hosted service is configured on the server and its evidence is independently checked."
            : "Owner view. These labels are static; the live service check above is the only server-side signal and fails closed."}
        </p>
        <ul className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {AUREX_OX_STATUS.map((s) => (
            <li key={s.id} className="min-w-0 border-t border-border pt-4">
              <p className="text-xs text-amber">{s.state}</p>
              <h3 className="mt-1 font-display text-lg">{s.name}</h3>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">{s.note}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
