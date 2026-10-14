import { useState } from "react";
import { PhoneOff, ShieldQuestion, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PresentationOrb } from "@/components/presentation-orb";
import { emitActivation } from "@/lib/activation-events";
import { phoneTopics } from "@/components/phone-scenarios";
import { JourneyArt } from "@/components/journey-art";
import { GuidedEvidenceTour } from "@/components/guided-evidence-tour";
export function FlagshipJourneys({ onStart }: { onStart?: (topic: number) => void }) {
  const [event, setEvent] = useState<"spam" | "serious" | null>(null);
  const [pulse, setPulse] = useState(0);
  const start = (index: number) => {
    setEvent(index === 0 ? "spam" : "serious");
    setPulse((p) => p + 1);
    emitActivation(index === 0 ? "call_demo_start" : "malware_demo_start");
    if (onStart) onStart(index);
    else {
      emitActivation("demo_start");
      emitActivation(index === 0 ? "spam_card_open" : "malware_card_open");
    }
  };
  return (
    <section className="flagship-journeys" aria-label="Flagship security previews">
      <p className="text-xs text-gold">PREVIEW · ASPIRATIONAL · NO LIVE BLOCKING OR SCANNING</p>
      <div className="flagship-grid">
        {phoneTopics["Command Center"].slice(0, 2).map((topic, index) => {
          const Icon = index === 0 ? PhoneOff : ShieldQuestion;
          return (
            <article
              key={topic.title}
              className="flagship-journey"
              id={onStart ? undefined : index === 0 ? "spam-demo" : "malware-demo"}
            >
              <div className="flagship-icon">
                <Icon className="size-7" aria-hidden="true" />
                <span className="text-xs text-gold">0{index + 1}</span>
              </div>
              <h3 className="mt-4 font-display text-lg">{topic.title}</h3>
              <JourneyArt kind={index === 0 ? "call" : "malware"} />
              <p className="mt-3 text-xs leading-6 text-muted-foreground">
                {index === 0
                  ? "An unexpected ‘bank’ call asks for a recovery code. Review the claim—not just caller ID."
                  : "An example app requests unexpected access. Inspect evidence without turning suspicion into a verdict."}
              </p>
              <Button variant="hero" className="mt-4 min-h-11" onClick={() => start(index)}>
                {index === 0 ? "Try call preview" : "Try app preview"}
                <ArrowRight />
              </Button>
              {event === (index === 0 ? "spam" : "serious") && (
                <GuidedEvidenceTour key={pulse} topicIndex={index} />
              )}
              <details
                className="mt-4"
                onToggle={(e) => {
                  if (e.currentTarget.open) emitActivation("proof_view");
                }}
              >
                <summary className="min-h-11 cursor-pointer text-xs text-primary">
                  Evidence, permissions &amp; limitations
                </summary>
                <dl className="phone-detail-fields">
                  {topic.fields.map(([label, text]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{text}</dd>
                    </div>
                  ))}
                </dl>
              </details>
            </article>
          );
        })}
      </div>
      {event && (
        <div className="flagship-event" role="status">
          <div key={pulse} className={event === "spam" ? "routine-call-pulse" : ""}>
            <PresentationOrb compact state={event === "spam" ? "AWARE" : "DEFEND"} />
          </div>
          <p className="text-xs leading-6 text-muted-foreground">
            {event === "spam"
              ? "Simulated call cue · subtle cyan presentation only. No call was blocked; source identity is unknown."
              : "Hypothetical serious-event comet · independent evidence and current authority are assumed only for illustration, not supplied. No malware was detected or contained."}
            <br />
            ORB MOTION AUTHORITY = NONE · Unknown ≠ Safe
          </p>
        </div>
      )}
    </section>
  );
}
