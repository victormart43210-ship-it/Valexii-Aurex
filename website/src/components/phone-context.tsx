import { useId } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { JourneyArt } from "@/components/journey-art";

import { phoneTopics, type PhoneView } from "@/components/phone-scenarios";

export function XaeliPortraitPlaceholder() {
  return (
    <figure className="xaeli-portrait-placeholder">
      <svg
        viewBox="0 0 300 390"
        role="img"
        aria-label="Missing image placeholder for the exact XAELI editorial portrait; no substitute portrait is shown"
      >
        <rect width="300" height="390" fill="var(--card)" />
        <rect
          x="24"
          y="24"
          width="252"
          height="342"
          fill="none"
          stroke="var(--gold)"
          strokeDasharray="4 8"
        />
        <g fill="none" stroke="var(--muted-foreground)" strokeWidth="2">
          <rect x="116" y="156" width="68" height="68" rx="4" />
          <circle cx="136" cy="176" r="6" />
          <path d="M116 212l20-20 14 14 14-24 20 30" />
        </g>
      </svg>
      <figcaption>
        <strong>XAELI</strong>
        <span>Exact editorial portrait unavailable · please upload the original image here.</span>
      </figcaption>
    </figure>
  );
}

export function PhoneTopicPicker({
  view,
  selected,
  onSelect,
}: {
  view: PhoneView;
  selected: number;
  onSelect: (index: number) => void;
}) {
  return (
    <div
      className={`phone-topic-picker ${view === "Command Center" ? "phone-command-picker" : ""}`}
    >
      {phoneTopics[view].map((topic, index) => (
        <Button
          key={topic.title}
          variant="ghost"
          aria-pressed={selected === index}
          onClick={() => onSelect(index)}
          className="phone-topic-choice"
        >
          <span>
            {view === "Command Center" && index < 2 && (
              <>
                <JourneyArt kind={index === 0 ? "call" : "malware"} />
                <span className="text-gold">FEATURED #{index + 1}</span>
              </>
            )}
            <strong>{topic.title}</strong>
            <span>{topic.summary}</span>
          </span>
          <ArrowRight aria-hidden="true" className="size-4 shrink-0" />
        </Button>
      ))}
    </div>
  );
}

export function PhoneDetailPanel({
  view,
  selected,
  onSelect,
}: {
  view: PhoneView;
  selected: number;
  onSelect: (index: number) => void;
}) {
  const id = useId();
  const topic = phoneTopics[view][selected] ?? phoneTopics[view][0];
  if (!topic) return null;
  return (
    <section className="phone-detail-panel" aria-labelledby={id}>
      <p className="text-xs text-gold">SIMULATED EXAMPLE · NO LIVE DEVICE DATA</p>
      <h3 id={id} className="mt-4 font-display text-2xl">
        {view} / {topic.title}
      </h3>
      <p className="mt-3 text-sm leading-7 text-muted-foreground" aria-live="polite">
        {topic.summary}
      </p>
      <dl className="phone-detail-fields">
        {topic.fields.map(([label, text]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{text}</dd>
          </div>
        ))}
      </dl>
      <div className="flex items-center justify-between gap-4 border-t border-border pt-4">
        <Button variant="glass" disabled={selected === 0} onClick={() => onSelect(selected - 1)}>
          <ArrowLeft />
          Back
        </Button>
        <span className="text-xs text-muted-foreground">
          {selected + 1} / {phoneTopics[view].length}
        </span>
        <Button
          variant="glass"
          disabled={selected === phoneTopics[view].length - 1}
          onClick={() => onSelect(selected + 1)}
        >
          Next
          <ArrowRight />
        </Button>
      </div>
    </section>
  );
}
