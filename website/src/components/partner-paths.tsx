import { useId } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, GraduationCap, Milestone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui-system";

/** Public invitations, not representations of partners, funding or delivered capability. */
export function PartnerPaths({ contact = false }: { contact?: boolean }) {
  const id = useId();
  return (
    <section className="section-space border-y border-border" aria-labelledby={`${id}-title`} data-partner-paths>
      <div className="site-grid">
        <SectionHeader id={`${id}-title`} eyebrow="Research partners & investors / Open invitation" title="Two ways to move the work forward." copy="Start with a question, agree on what would count as evidence, and make the next decision reviewable. No existing partnership or funding is implied." />
        <div className="mt-9 grid gap-10 md:grid-cols-2">
          <article className="min-w-0 border-t border-primary pt-6">
            <GraduationCap aria-hidden="true" className="size-7 text-primary" />
            <h3 className="mt-4 font-display text-2xl">Universities: test what could fail.</h3>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">Independent evaluation, reproducibility and adversarial testing can turn a design claim into a research question. We welcome scoped student collaboration, ethics review and non-confidential IP discussions—not assumed access to private research.</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">A useful first brief names the question, comparison method, evidence needed and result that would falsify the hypothesis. Agree on consent, publication, data access and IP boundaries before work begins.</p>
            <Button asChild variant="glass" className="mt-6"><Link to={contact ? "/aurex" : "/contact"}>{contact ? "Review AUREX research scope" : "Discuss independent research"}<ArrowRight /></Link></Button>
          </article>
          <article className="min-w-0 border-t border-gold pt-6">
            <Milestone aria-hidden="true" className="size-7 text-gold" />
            <h3 className="mt-4 font-display text-2xl">Investors: examine the next milestone.</h3>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">Investors welcome. BCXMET is the first product focus; DISPATER and XAITA are later domain directions. A potentially defensible architecture must earn that description through validation—not visual polish or an assertion of uniqueness.</p>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">Explore product sequencing, validation gaps, market hypotheses and evidence-gated milestones. The 10,000 retained-user target is not traction. IP strategy is being pursued, not patent-pending status; the grant proposal is a target, not an award.</p>
            <Button asChild variant="outline" className="mt-6"><Link to={contact ? "/build-with-us" : "/contact"}>{contact ? "Review milestones and grant target" : "Discuss the product roadmap"}<ArrowRight /></Link></Button>
          </article>
        </div>
        <p className="mt-8 text-xs leading-6 text-amber">Exploratory conversations only · No investment offering, promised return, completed validation or funded commitment.</p>
      </div>
    </section>
  );
}