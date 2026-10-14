import { Link } from "@tanstack/react-router";
import { SectionHeading } from "@/components/site";
import { Button } from "@/components/ui/button";

/** Public design direction, never a claim of implemented cross-domain transfer. */
export function DomainReasoning() {
  return (
    <section className="section-space border-y border-border bg-card/25">
      <div className="site-grid">
        <SectionHeading
          eyebrow="Shared context / Separate permission"
          title="Shared reasoning. Separate boundaries."
          copy="The shared design explores carrying useful context between applications without carrying permission to act. Evidence and review history may inform another question; authority must be checked there anew."
        />
        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <div>
            <h3 className="font-display text-xl">Carry context, not control</h3>
            <p className="mt-4 leading-7 text-muted-foreground">
              The design explores transferable cognitive state—structured context, evidence
              references, uncertainty and review history—across BCXMET cybersecurity, DISPATER
              industrial intelligence and XAITA capital intelligence. Each domain shell retains its
              own evidence, permissions and authorities. Cross-domain transfer is a developmental
              ambition, not verified functionality.
            </p>
          </div>
          <div>
            <h3 className="font-display text-xl">Continuity without silent power</h3>
            <p className="mt-4 leading-7 text-muted-foreground">
              Remembering a source or an unresolved question could make a new review more useful. It
              must not silently carry approval into another setting. This is not a claim of
              sentience or autonomous agency, and continuity is not verified functionality.
            </p>
          </div>
        </div>
        <p className="mt-8 border-l-2 border-gold pl-5 leading-7">
          Evidence → Qualification → Reality → Authority → Effect
        </p>
        <p className="mt-4 leading-7 text-muted-foreground">
          The system must never be its own sole witness. Independent evidence and challenge must
          support consequential claims; unresolved evidence remains HOLD for human review. UNKNOWN ≠
          SAFE. Missing or stale evidence is not PASS. Visualization supplies no authority, and no
          shell inherits another domain’s authorization.
        </p>
        <Button asChild variant="outline" className="mt-6">
          <Link to="/system">Explore governed intelligence</Link>
        </Button>
      </div>
    </section>
  );
}
