import { useId } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, ArrowDown, ShieldQuestion } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui-system";
import {
  reverseFlow,
  spineContexts,
  spineFlow,
  spineStages,
  type SpineContext,
} from "./reasoning-spine-model";

export interface ReasoningSpineProps {
  context: SpineContext;
  detailed?: boolean;
}

/** Authored public explanation only; no link from presentation into authority. */
export function ReasoningSpine({ context, detailed = false }: ReasoningSpineProps) {
  const id = useId();
  const content = spineContexts[context];
  return (
    <section
      className="section-space border-y border-border bg-card/25"
      aria-labelledby={`${id}-title`}
      data-reasoning-spine={context}
    >
      <div className="site-grid">
        <SectionHeader
          id={`${id}-title`}
          eyebrow="Evidence-governed design / In development"
          title={content.title}
          copy={content.copy}
        />
        <p className="mt-6 max-w-3xl leading-7 text-muted-foreground">{content.application}</p>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-muted-foreground">
          The aim is simple: know the source, test alternative explanations and keep permission
          separate from persuasion. Independent checks must support consequential claims. Approval
          must be current, limited in scope and withdrawable before an action—not after it.
        </p>
        <p className="sr-only">{spineFlow}</p>
        <ol
          aria-label="Unified Reasoning Spine stages"
          className="mt-9 grid gap-4 sm:grid-cols-2 lg:grid-cols-5"
        >
          {spineStages.map((stage, i) => (
            <li key={stage.name} className="min-w-0 border-t-2 border-primary/45 pt-5">
              <div className="flex items-center justify-between gap-2 text-primary">
                <span className="text-xs tabular-nums">0{i + 1}</span>
                {i < 4 && (
                  <>
                    <ArrowRight aria-hidden="true" className="hidden size-4 lg:block" />
                    <ArrowDown aria-hidden="true" className="size-4 lg:hidden" />
                  </>
                )}
              </div>
              <h3 className="mt-4 break-words text-sm font-semibold uppercase">{stage.name}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{stage.question}</p>
            </li>
          ))}
        </ol>
        {detailed && (
          <div className="mt-10 grid gap-x-10 gap-y-8 md:grid-cols-2">
            {spineStages.map((stage, i) => (
              <article key={stage.name} className="min-w-0 border-t border-border pt-6">
                <h3 className="font-display text-xl">
                  0{i + 1} / {stage.name}
                </h3>
                <p className="mt-4 leading-7 text-muted-foreground">{stage.detail}</p>
                <p className="mt-4 border-l-2 border-gold pl-4 text-sm leading-7">
                  {stage.example}
                </p>
              </article>
            ))}
            <article className="min-w-0 border-t border-border pt-6">
              <h3 className="font-display text-xl">Reverse review / Follow the result back</h3>
              <p className="mt-4 break-words text-sm leading-7 text-gold">{reverseFlow}</p>
              <p className="mt-4 leading-7 text-muted-foreground">
                Start from the result and reconstruct its permission, supported truth, admissible
                evidence and source. Here, “Truth” means the claim supported by evidence—not
                certainty by declaration. Reverse review needs independent witnesses; replaying our
                own conclusion is not verification.
              </p>
            </article>
            <article className="min-w-0 border-t border-border pt-6">
              <h3 className="font-display text-xl">
                Three roles. Independent support still required.
              </h3>
              <p className="mt-4 leading-7 text-muted-foreground">
                Advocate presents a supported interpretation. Challenger looks for counterexamples
                and competing causes. Arbiter checks the declared requirements against evidence, not
                persuasiveness. Shared models, data or incentives can create correlated agreement;
                role labels alone do not produce independent witnesses.
              </p>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                A review should record source dependencies, conflicts, unresolved objections and the
                external checks still needed. AUREX can test this method; it cannot certify itself
                or grant product authority.
              </p>
            </article>
            <article className="min-w-0 border-t border-border pt-6">
              <h3 className="font-display text-xl">
                When a dependency fails, permission must not grow.
              </h3>
              <p className="mt-4 leading-7 text-muted-foreground">
                Connected systems depend on sources, infrastructure and permissions that can change.
                The design requirement is to retain inspectable evidence, expose missing
                dependencies and stop proposed effects when freshness, scope or authorization cannot
                be established.
              </p>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Expiry and revocation must be checked again before a bounded effect. Test outages,
                stale sources and withdrawn approval explicitly. Auditability is a requirement to
                demonstrate—not a claim that these safeguards are already deployed.
              </p>
            </article>
          </div>
        )}
        <div className="mt-9 grid gap-6 border-t border-border pt-6 md:grid-cols-2">
          <div>
            <h3 className="flex items-center gap-2 text-base font-semibold">
              <ShieldQuestion aria-hidden="true" className="size-5 shrink-0 text-gold" />
              History is not permission.
            </h3>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">
              A past observation stays in the record. A present action needs current, scoped
              authorization. Missing, stale or unverified evidence never counts as PASS. UNKNOWN ≠
              SAFE.
            </p>
          </div>
          <div>
            <h3 className="text-base font-semibold">
              A system must never be its own sole witness.
            </h3>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">
              Independent support must be demonstrated, not assumed from agreement between models.
              Unresolved checks mean HOLD → human review. ORB MOTION AUTHORITY = NONE; colors,
              wheels and zoom provide presentation only.
            </p>
          </div>
        </div>
        <p className="mt-6 text-xs leading-6 text-amber">
          DESIGN INTENT / DEVELOPMENTAL · This public explanation does not establish operational
          gates, independently verified product performance or autonomous authority.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          {context !== "system" && (
            <Button asChild variant="glass">
              <Link to="/system">
                Explore our evidence philosophy <ArrowRight />
              </Link>
            </Button>
          )}
          {(context === "home" || context === "system" || context === "ecosystem") && (
            <>
              <Button asChild variant="outline">
                <Link to="/bcxmet">
                  BCXMET <ArrowRight />
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/dispater">
                  DISPATER.AI <ArrowRight />
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/xaita">
                  XAITA.AI <ArrowRight />
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
