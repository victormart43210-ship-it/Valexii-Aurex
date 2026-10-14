import { useEffect, useId, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { LockKeyhole, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getNewsletterStatus, subscribeNewsletter } from "@/lib/newsletter.functions";

type Phase = "checking" | "inactive" | "ready" | "sending" | "pending" | "error";

const errors = {
  rate: "Too many attempts. Please try again later.",
  invalid: "Please check the form and try again.",
  upstream: "The signup service did not accept the request. Nothing was confirmed.",
  inactive: "Signup is not yet active.",
};

/** Opt-in weekly research newsletter. Disabled unless the server reports a configured provider. */
export function NewsletterSignup({ compact = false }: { compact?: boolean }) {
  const id = useId();
  const [phase, setPhase] = useState<Phase>("checking");
  const [message, setMessage] = useState("");
  const started = useRef(Date.now());

  useEffect(() => {
    let live = true;
    getNewsletterStatus()
      .then((s) => live && setPhase(s.active ? "ready" : "inactive"))
      .catch(() => live && setPhase("inactive"));
    return () => {
      live = false;
    };
  }, []);

  const disabled = phase !== "ready" && phase !== "error";

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (disabled) return;
    const f = new FormData(e.currentTarget);
    setPhase("sending");
    try {
      const r = await subscribeNewsletter({
        data: {
          email: String(f.get("email") ?? ""),
          consent: f.get("consent") === "on",
          website: String(f.get("website") ?? ""),
          startedAt: started.current,
        },
      });
      if (r.ok) {
        setPhase("pending");
        setMessage("Check your inbox to confirm. You are not subscribed until you confirm.");
      } else {
        setPhase(r.reason === "inactive" ? "inactive" : "error");
        setMessage(errors[r.reason ?? "upstream"]);
      }
    } catch {
      setPhase("error");
      setMessage(errors.invalid);
    }
  }

  return (
    <section
      aria-labelledby={`${id}-title`}
      className={compact ? "frontier-signup frontier-signup-compact" : "frontier-signup"}
    >
      <div>
        <p className="frontier-kicker">Weekly Research Dispatch · opt-in</p>
        <h2 id={`${id}-title`}>{compact ? "Follow the research." : "Weekly research briefing"}</h2>
        <p>
          Planned weekly notes on the Voynich Manuscript, Linear A, Rongorongo and evidence-governed
          methods. Findings, hypotheses and open questions stay distinct; no claimed decipherment.
          If signup opens, confirmation and an unsubscribe option are required.
        </p>
      </div>
      <form className="frontier-signup-action" onSubmit={onSubmit} noValidate={false}>
        <label htmlFor={`${id}-email`} className="text-sm font-medium">
          Email address
        </label>
        <input
          id={`${id}-email`}
          name="email"
          type="email"
          required
          autoComplete="email"
          disabled={disabled}
          className="min-h-11 w-full rounded-md border border-input bg-background px-3 text-sm disabled:opacity-60"
        />
        <input
          type="text"
          name="website"
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          className="hidden"
        />
        <label className="flex items-start gap-2 text-sm">
          <input
            name="consent"
            type="checkbox"
            required
            disabled={disabled}
            className="mt-1 size-4"
          />
          <span>
            I agree to receive the weekly email and understand I must confirm by email. See the{" "}
            <Link to="/privacy" className="underline">
              privacy notice
            </Link>
            .
          </span>
        </label>
        <Button type="submit" variant="hero" className="min-h-11" disabled={disabled}>
          {disabled && phase !== "sending" ? (
            <LockKeyhole aria-hidden="true" />
          ) : (
            <Mail aria-hidden="true" />
          )}
          {phase === "checking"
            ? "Checking…"
            : phase === "sending"
              ? "Sending…"
              : phase === "inactive"
                ? "Signup not yet active"
                : "Request subscription"}
        </Button>
        <p role="status" aria-live="polite" className="text-sm">
          {phase === "inactive"
            ? "Signup not yet active. No address is collected, saved or added to a list."
            : message}
        </p>
      </form>
    </section>
  );
}
