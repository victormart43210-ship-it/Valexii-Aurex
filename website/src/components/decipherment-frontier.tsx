import { ArrowRight, Check, CircleAlert, Clock3 } from "lucide-react";
import triptych from "@/assets/decipherment-triptych.jpg";

const stages = ["Evidence", "Qualification", "Reality", "Authority", "Effect"];

export function ResearchTriptych() {
  return (
    <figure className="frontier-triptych">
      <img
        src={triptych}
        width={1536}
        height={864}
        loading="lazy"
        alt="Artistic triptych of an imagined botanical manuscript, an imagined clay tablet, and an imagined carved wooden glyph board."
      />
      <div className="frontier-triptych-labels" aria-hidden="true">
        <span>Voynich Manuscript</span>
        <span>Linear A</span>
        <span>Rongorongo</span>
      </div>
      <figcaption>
        Artistic illustrations for editorial context—not photographs, facsimiles, or actual artifact
        reproductions. No glyph or inscription shown here is research evidence.
      </figcaption>
    </figure>
  );
}

export function EvidenceFlow() {
  return (
    <figure className="frontier-flow" aria-labelledby="frontier-flow-title">
      <div className="frontier-flow-heading">
        <div>
          <p className="frontier-kicker">VALEXII / Evidence review design</p>
          <h2 id="frontier-flow-title">A proposed reading must survive the chain.</h2>
        </div>
        <span className="frontier-status frontier-status-hold">HOLD</span>
      </div>
      <ol className="frontier-flow-stages">
        {stages.map((stage, index) => (
          <li key={stage}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{stage}</strong>
            {index < stages.length - 1 && <ArrowRight aria-hidden="true" />}
          </li>
        ))}
      </ol>
      <div className="frontier-cues">
        <div>
          <CircleAlert aria-hidden="true" />
          <span>
            <strong>Hypothesis</strong> Competing explanations and uncertainty stay visible.
          </span>
        </div>
        <div>
          <Check aria-hidden="true" />
          <span>
            <strong>Verified</strong> Requires reconstruction, counterchecks, and independent
            evidence.
          </span>
        </div>
      </div>
      <figcaption>
        A suggested reading needs more than a convincing explanation. Separate checks must challenge
        it; unknown is not safe, and the system is never its own sole witness.
      </figcaption>
    </figure>
  );
}

export { NewsletterSignup } from "@/components/newsletter-signup";

export function BreakthroughWatch() {
  const states = [
    {
      title: "Voynich Manuscript",
      status: "HOLD / NOT ESTABLISHED",
      body: "Structural observations and working models remain separate from semantic interpretation. No claimed decipherment.",
      tone: "hold",
    },
    {
      title: "Linear A",
      status: "HYPOTHESIS / EVIDENCE REQUIRED",
      body: "Corpus control and testable structural questions are the research direction. No verified translation is presented here.",
      tone: "hypothesis",
    },
    {
      title: "Rongorongo",
      status: "HYPOTHESIS / EVIDENCE REQUIRED",
      body: "Material record, sign sequence, and contextual constraints must be qualified before interpretation. No verified translation is presented here.",
      tone: "hypothesis",
    },
  ];
  return (
    <div className="frontier-watch">
      {states.map((item) => (
        <article key={item.title}>
          <span className={`frontier-status frontier-status-${item.tone}`}>{item.status}</span>
          <h3>{item.title}</h3>
          <p>{item.body}</p>
        </article>
      ))}
      <article className="frontier-archive">
        <Clock3 aria-hidden="true" />
        <h3>Public archive</h3>
        <p>No issues published yet. This space will list dated briefings only after they exist.</p>
      </article>
    </div>
  );
}
