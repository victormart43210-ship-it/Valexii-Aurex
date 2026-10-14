import { useEffect, useId, useState } from "react";
import { ArrowLeft, ArrowRight, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { phoneTopics } from "@/components/phone-scenarios";
import { emitActivation } from "@/lib/activation-events";

export function GuidedEvidenceTour({ topicIndex }: { topicIndex: number }) {
  const topic = phoneTopics["Command Center"][topicIndex];
  const [step, setStep] = useState(0);
  const [mobile, setMobile] = useState(false);
  const id = useId();
  useEffect(() => {
    const query = window.matchMedia("(max-width: 640px)");
    const update = () => {
      setMobile(query.matches);
      setStep(0);
    };
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  if (!topic) return null;
  const groups = mobile ? [[0, 1], [4], [2], [3, 6], [5, 7]] : [[0, 1], [4], [2], [3], [6], [5, 7]];
  const titles = mobile
    ? [
        "The scenario",
        "Inspect evidence",
        "Review permissions",
        "Status and uncertainty",
        "Your next review",
      ]
    : [
        "The scenario",
        "Inspect evidence",
        "Review permissions",
        "Capability status",
        "Qualification",
        "Your next review",
      ];
  const fields = groups[step] ?? groups[0];
  return (
    <section className="mt-5 border-t border-border pt-5" aria-labelledby={id}>
      <p className="text-xs text-gold">GUIDED EXAMPLE · SIMULATED · NO DEVICE ACCESS</p>
      <div className="mt-3" aria-live="polite" aria-atomic="true">
        <p className="text-xs text-muted-foreground">
          {step + 1} / {groups.length}
        </p>
        <h4 id={id} className="mt-2 font-display text-lg">
          {titles[step]}
        </h4>
        <dl className="phone-detail-fields">
          {fields?.map((index) => {
            const field = topic.fields[index];
            return field ? (
              <div key={field[0]}>
                <dt>{field[0]}</dt>
                <dd>{field[1]}</dd>
              </div>
            ) : null;
          })}
        </dl>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Button variant="glass" disabled={step === 0} onClick={() => setStep(step - 1)}>
          <ArrowLeft />
          Back
        </Button>
        {step < groups.length - 1 ? (
          <Button
            variant="hero"
            onClick={() => {
              setStep(step + 1);
              if (step === 0) emitActivation("proof_view");
            }}
          >
            Next
            <ArrowRight />
          </Button>
        ) : (
          <Button variant="glass" onClick={() => setStep(0)}>
            <RotateCcw />
            Restart
          </Button>
        )}
      </div>
      {step === groups.length - 1 && (
        <p className="mt-4 text-xs leading-6 text-muted-foreground">
          Review complete—not a security verdict. Unknown ≠ Safe. ORB MOTION AUTHORITY = NONE.
        </p>
      )}
    </section>
  );
}
