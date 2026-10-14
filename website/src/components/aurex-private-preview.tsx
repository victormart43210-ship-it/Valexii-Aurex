import { Link } from "@tanstack/react-router";
import { Lock } from "lucide-react";
import { PRIVATE_PLACEHOLDERS } from "@/lib/aurex-public";

/**
 * Frosted cards built ONLY from synthetic placeholder text. No private data is
 * fetched or rendered here; the blur is decoration, not security.
 */
export function AurexPrivatePreview() {
  return (
    <section aria-labelledby="aurex-private-title" className="section-space border-b border-border">
      <div className="site-grid">
        <p className="text-xs text-gold">PRIVATE · Owner only</p>
        <h2 id="aurex-private-title" className="mt-3 font-display text-3xl">Private workspace</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
          Private research details, service status, budgets and audit records are never sent to this page.
          The cards below are illustrative placeholders, not blurred real data.
        </p>
        <ul className="mt-6 grid gap-4 md:grid-cols-3" data-testid="aurex-private-preview">
          {PRIVATE_PLACEHOLDERS.map((c) => (
            <li key={c.title} className="aurex-frost relative min-w-0 overflow-hidden rounded-md border border-border p-5">
              <div aria-hidden="true" className="aurex-frost-content">
                {c.lines.map((l) => <p key={l} className="text-sm leading-7">{l}</p>)}
              </div>
              <div className="absolute inset-0 flex flex-col items-start justify-end gap-1 p-5">
                <span className="inline-flex items-center gap-2 text-xs text-gold"><Lock className="size-3.5" aria-hidden="true" /> PRIVATE</span>
                <h3 className="font-display text-lg">{c.title}</h3>
                <p className="text-xs text-muted-foreground">Placeholder — no data shown</p>
              </div>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-sm">
          <Link className="underline underline-offset-4" to="/admin/aurex-control">Owner sign-in required</Link> — access is checked on the server.
        </p>
      </div>
    </section>
  );
}
