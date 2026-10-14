import { Link } from "@tanstack/react-router";
import { capabilities, resolveStatus, type CapabilityStatus } from "@/lib/aurex-capabilities";

const label: Record<CapabilityStatus, string> = {
  REAL_CONNECTED: "REAL / CONNECTED",
  NOT_CONFIGURED: "NOT CONFIGURED",
  PLANNED: "PLANNED",
};
const tone: Record<CapabilityStatus, string> = {
  REAL_CONNECTED: "text-primary",
  NOT_CONFIGURED: "text-amber",
  PLANNED: "text-muted-foreground",
};

/** Public, non-sensitive registry. Statuses use no backend checks, so service capabilities show NOT CONFIGURED. */
export function AurexCapabilitiesPanel({
  live,
}: {
  live?: Record<string, CapabilityStatus> | undefined;
}) {
  return (
    <section aria-labelledby="aurex-cap-title" className="section-space border-b border-border">
      <div className="site-grid">
        <p className="text-xs text-primary">PUBLIC · AUREX capability registry · Wave 1</p>
        <h2 id="aurex-cap-title" className="mt-3 font-display text-3xl">
          What exists, what is waiting, what is planned
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
          REAL / CONNECTED means working code on this website. NOT CONFIGURED means it depends on a
          separately hosted, authenticated AUREX service that is not connected. PLANNED means no
          implementation exists yet. No results are shown here.
        </p>
        <ul
          className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3"
          data-testid="aurex-capabilities"
        >
          {capabilities.map((c) => {
            const st = live?.[c.id] ?? resolveStatus(c);
            return (
              <li key={c.id} className="min-w-0 border-t border-border pt-4">
                <p className={`text-xs ${tone[st]}`}>
                  {label[st]}
                  {c.restricted ? " · owner only" : ""}
                </p>
                <h3 className="mt-1 font-display text-lg">{c.name}</h3>
                <p className="mt-1 text-sm leading-6 text-muted-foreground">{c.summary}</p>
              </li>
            );
          })}
        </ul>
        {!live && (
          <p className="mt-6 text-sm">
            Owner controls are private.{" "}
            <Link className="underline underline-offset-4" to="/admin/aurex-control">
              Owner sign-in required
            </Link>
            .
          </p>
        )}
      </div>
    </section>
  );
}
