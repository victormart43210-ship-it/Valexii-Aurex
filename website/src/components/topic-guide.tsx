import type { ReactNode } from "react";
import { SectionHeading } from "@/components/site";

export interface TopicFaq {
  question: string;
  answer: string;
}
export interface TopicSource {
  label: string;
  href: string;
}

/** Visible, crawlable educational FAQ with external sources. No structured-data claims. */
export function TopicGuide({
  id,
  eyebrow,
  title,
  intro,
  faqs,
  sources,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  intro?: string;
  faqs: TopicFaq[];
  sources: TopicSource[];
  children?: ReactNode;
}) {
  return (
    <section id={id} className="section-space border-t border-border" aria-labelledby={`${id}-h`}>
      <div className="site-grid">
        <div id={`${id}-h`}>
          <SectionHeading eyebrow={eyebrow} title={title} {...(intro ? { copy: intro } : {})} />
        </div>
        {children}
        <dl className="mt-10 grid gap-x-12 md:grid-cols-2">
          {faqs.map((f) => (
            <div key={f.question} className="border-t border-primary/35 py-6">
              <dt className="font-display text-lg">{f.question}</dt>
              <dd className="mt-3 text-sm leading-7 text-muted-foreground">{f.answer}</dd>
            </div>
          ))}
        </dl>
        <div className="mt-8 border-l-2 border-gold pl-5">
          <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
            Sources and further reading
          </h3>
          <ul className="mt-3 space-y-2 text-sm">
            {sources.map((s) => (
              <li key={s.href}>
                <a
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-4 hover:text-primary"
                >
                  {s.label}
                </a>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-muted-foreground">
            External sources are independent of VALEXII.AI and do not endorse this work.
          </p>
        </div>
      </div>
    </section>
  );
}
