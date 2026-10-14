import { useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft,
  ArrowRight,
  Fingerprint,
  Globe,
  Wallet,
  LockKeyhole,
  MessageSquareWarning,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { phoneTopics } from "@/components/phone-scenarios";
import { PhoneDetailPanel } from "@/components/phone-context";
import { PresentationOrb } from "@/components/presentation-orb";
import { JourneyArt } from "@/components/journey-art";
import { emitActivation } from "@/lib/activation-events";

export function CommandCenter({
  selected,
  onSelect,
  onXaeli,
}: {
  selected: number;
  onSelect: (index: number) => void;
  onXaeli: (index: number) => void;
}) {
  const [opened, setOpened] = useState(false);
  const overview = useRef<HTMLHeadingElement>(null);
  const [demo, setDemo] = useState<number | null>(null);
  const [review, setReview] = useState<"explain" | "proof" | "help" | null>(null);
  const topics = phoneTopics["Command Center"];
  const topic = topics[selected] ?? topics[0];
  const icons = [MessageSquareWarning, Wallet, LockKeyhole, Globe, Fingerprint];
  if (!topic) return null;
  const choose = (index: number) => {
    onSelect(index);
    setOpened(true);
    setDemo(null);
    setReview(null);
  };
  const start = () => {
    setDemo(selected);
    emitActivation(selected === 0 ? "call_demo_start" : "malware_demo_start");
  };
  const xaeli = (mode: "explain" | "proof" | "help", index: number) => {
    setReview(mode);
    onXaeli(index);
    if (mode === "explain") emitActivation("xaeli_explain");
    if (mode === "proof") {
      emitActivation("proof_view");
      if (demo !== null) {
        emitActivation(demo === 0 ? "call_demo_finish" : "malware_demo_finish");
        setDemo(null);
      }
    }
  };
  return (
    <section className="command-web" aria-label="Full-size Command Center">
      <div className="command-heading">
        <div>
          <p className="text-xs text-gold">BCXMET / COMMAND CENTER</p>
          <h2 ref={overview} tabIndex={-1} className="mt-3 font-display text-3xl">
            Choose what matters.
          </h2>
        </div>
        <span className="text-xs text-primary">WEBSITE DEMO ONLY</span>
      </div>
      <p className="mt-4 text-sm leading-7 text-muted-foreground">
        Review a call or question an app. No blocking, scanning or Android permission access runs
        here.
      </p>
      <div className="command-featured">
        {topics.slice(0, 2).map((item, index) => (
          <Button
            key={item.title}
            variant="glass"
            className="command-card"
            aria-pressed={selected === index}
            onClick={() => choose(index)}
          >
            <span className="command-card-inner">
              <JourneyArt kind={index === 0 ? "call" : "malware"} />
              <span className="text-xs text-gold">FEATURED #{index + 1} · UNDER DEVELOPMENT</span>
              <strong>{item.title}</strong>
              <span className="text-xs text-muted-foreground">
                {index === 0
                  ? "Call Shield · review suspicious cues"
                  : "Malware Shield · inspect uncertainty"}
              </span>
              <span className="mt-3 flex items-center gap-2 text-xs text-primary">
                Explore example <ArrowRight className="size-4" />
              </span>
            </span>
          </Button>
        ))}
      </div>
      <h3 className="mt-6 text-sm font-semibold">Five everyday journeys</h3>
      <div className="command-categories">
        {topics.slice(2).map((item, index) => {
          const Icon = icons[index] ?? Fingerprint;
          return (
            <Button
              key={item.title}
              variant="glass"
              aria-pressed={selected === index + 2}
              onClick={() => choose(index + 2)}
            >
              <Icon aria-hidden="true" />
              <span>{item.title}</span>
              <ArrowRight className="size-4" />
            </Button>
          );
        })}
      </div>
      <div className="command-drilldown">
        <nav aria-label="Demo breadcrumb" className="flex flex-wrap items-center gap-2 text-xs">
          <Button
            variant="link"
            className="min-h-11 px-0"
            onClick={() => {
              setOpened(false);
              setDemo(null);
              setReview(null);
              overview.current?.focus({ preventScroll: true });
              overview.current?.scrollIntoView({ block: "start", behavior: "auto" });
            }}
          >
            <ArrowLeft /> Command overview
          </Button>
          <span aria-hidden="true">/</span>
          <span>{topic.title}</span>
        </nav>
        {!opened && (
          <p className="mb-4 text-xs text-muted-foreground">
            Selected example follows the phone. Choose any featured card or journey to continue.
          </p>
        )}
        <PhoneDetailPanel view="Command Center" selected={selected} onSelect={choose} />
        <div className="evidence-rail" aria-label="Illustrative evidence trail">
          {[
            ["Evidence", "Authored fixture"],
            ["Quality", "Synthetic / incomplete"],
            ["Freshness", "Illustrative, not current"],
            ["Authority", "NONE · HOLD"],
          ].map(([label, value]) => (
            <div key={label}>
              <strong>{label}</strong>
              <span>{value}</span>
            </div>
          ))}
        </div>
        {selected < 2 && (
          <Button variant="hero" className="mt-5" onClick={start}>
            Start {selected === 0 ? "call" : "app"} scenario <ArrowRight />
          </Button>
        )}
        {demo !== null && (
          <div className="command-story" role="status">
            <div className={demo === 0 ? "routine-call-pulse" : ""}>
              <PresentationOrb compact state={demo === 0 ? "AWARE" : "DEFEND"} />
            </div>
            <p>
              {demo === 0
                ? "Fictional caller asks for a recovery code. A subtle cue invites review; source identity is unknown. No call was blocked."
                : "Counterfactual serious-threat story: imagine an independent witness and fresh evidence were supplied. They are NOT supplied here. The DEFEND comet renders demo state only; no malware verdict or containment occurs."}
              <br />
              <strong>SIMULATION · ORB MOTION AUTHORITY = NONE</strong>
            </p>
          </div>
        )}
        <h3 className="mt-6 font-display text-xl">XAELI · review this case</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="glass" onClick={() => xaeli("explain", 0)}>
            Explain it
          </Button>
          <Button variant="glass" onClick={() => xaeli("proof", 1)}>
            Show proof
          </Button>
          <Button variant="glass" onClick={() => xaeli("help", 2)}>
            Help me review it
          </Button>
        </div>
        {review && (
          <div className="command-review" role="status">
            <p className="text-xs text-gold">AUTHORED XAELI EXPLANATION · NOT LIVE AI</p>
            <p className="mt-3 text-sm leading-7">
              {review === "explain"
                ? `${topic.summary}. This is a cue for human review, not a security conclusion. Benign explanations and mistaken identity remain possible.`
                : review === "proof"
                  ? `Source: ${selected === 0 ? "call-A" : selected === 1 ? "app-B" : "authored journey fixture"}. No independent device witness is attached. Quality is synthetic; freshness is illustrative; qualification is NOT ESTABLISHED. Reviewing this fixture completes only an educational website step.`
                  : "Confirm identity through a separate trusted channel; inspect real Android settings; compare alternatives and request independent evidence. Keep unresolved questions on HOLD. Unknown ≠ Safe."}
            </p>
          </div>
        )}
        <p className="mt-5 text-xs leading-6 text-muted-foreground">
          Evidence → Qualification → Reality → Authority → Effect. The system may never be its own
          sole witness. No effect is authorized here.
        </p>
        <Button asChild variant="link" className="mt-4 px-0">
          <Link to="/contact" data-activation="beta_interest">
            Optional beta interest <ArrowRight />
          </Link>
        </Button>
      </div>
    </section>
  );
}
