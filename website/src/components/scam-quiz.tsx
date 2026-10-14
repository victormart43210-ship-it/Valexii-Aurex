import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { JourneyArt } from "@/components/journey-art";
import { emitActivation } from "@/lib/activation-events";

const questions = [
  {
    cue: "‘I'm from your bank. Read me your recovery code now to stop a payment.’",
    choices: ["Share the code to act quickly", "End the call and contact the bank independently"],
    correct: 1,
    why: "Urgency and a request for recovery codes are warning cues. Do not share codes. Independently open your bank's verified contact channel; this cue does not verify the caller's identity.",
  },
  {
    cue: "A familiar-looking caller name appears on your screen. Is that sufficient proof of identity?",
    choices: ["No—verify through a separate trusted channel", "Yes—the displayed name confirms it"],
    correct: 0,
    why: "Caller names and numbers can be spoofed. Familiarity alone is not proof. The example supplies no independent witness, so identity remains unknown.",
  },
];
export function ScamQuiz() {
  const [step, setStep] = useState<number | null>(null);
  const [answer, setAnswer] = useState<number | null>(null);
  const [finished, setFinished] = useState(false);
  const question = questions[step ?? 0];
  const start = () => {
    setStep(0);
    setAnswer(null);
    setFinished(false);
    emitActivation("quiz_start");
  };
  if (!question) return null;
  return (
    <section
      className="section-space border-y border-border"
      id="scam-quiz"
      aria-labelledby="scam-quiz-title"
    >
      <div className="site-grid quiz-layout">
        <div>
          <p className="text-xs text-gold">ORIGINAL EDUCATIONAL EXERCISE · NO DEVICE SCAN</p>
          <h2 id="scam-quiz-title" className="mt-4 font-display text-3xl">
            Try spotting the scam.
          </h2>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            Two everyday decisions. No phone number, personal answer or device data is collected by
            this exercise.
          </p>
          <JourneyArt kind="call" />
        </div>
        <div className="quiz-stage">
          {step === null ? (
            <Button variant="hero" onClick={start}>
              Start quick quiz
            </Button>
          ) : finished ? (
            <>
              <h3 className="font-display text-2xl">Good questions beat false certainty.</h3>
              <p className="mt-4 text-sm leading-7">
                Exercise complete—not a security qualification. Next, see how XAELI separates a cue
                from proof and leaves uncertainty visible.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Button asChild variant="hero">
                  <Link to="/xaeli" data-activation="xaeli_explain">
                    Review with XAELI
                  </Link>
                </Button>
                <Button variant="glass" onClick={start}>
                  Try again
                </Button>
              </div>
            </>
          ) : (
            <>
              <p className="text-xs text-primary">
                Question {(step ?? 0) + 1} / 2 · fictional scenario
              </p>
              <h3 className="mt-4 text-xl leading-8">{question.cue}</h3>
              <div className="mt-5 grid gap-3" role="group" aria-label="Choose your response">
                {question.choices.map((choice, i) => (
                  <Button
                    key={choice}
                    variant="glass"
                    className="quiz-answer"
                    aria-pressed={answer === i}
                    disabled={answer !== null}
                    onClick={() => setAnswer(i)}
                  >
                    {choice}
                  </Button>
                ))}
              </div>
              {answer !== null && (
                <div className="mt-5" role="status">
                  <p className="text-sm text-gold">
                    {answer === question.correct
                      ? "That's the safer review step."
                      : "Pause—there's a safer review step."}
                  </p>
                  <p className="mt-3 text-sm leading-7 text-muted-foreground">{question.why}</p>
                  <Button
                    variant="hero"
                    className="mt-4"
                    onClick={() => {
                      if (step === questions.length - 1) {
                        setFinished(true);
                        emitActivation("quiz_finish");
                      } else setStep((step ?? 0) + 1);
                      setAnswer(null);
                    }}
                  >
                    {step === questions.length - 1 ? "Complete exercise" : "Next question"}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
}
