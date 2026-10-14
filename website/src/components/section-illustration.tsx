import voynichSmall from "@/assets/voynich-cinematic-480.webp";
import voynich from "@/assets/voynich-cinematic-768.webp";
import linearSmall from "@/assets/linear-a-cinematic-480.webp";
import linear from "@/assets/linear-a-cinematic-768.webp";
import rongoSmall from "@/assets/rongorongo-cinematic-480.webp";
import rongo from "@/assets/rongorongo-cinematic-768.webp";
import systemSmall from "@/assets/evidence-architecture-cinematic-640.webp";
import system from "@/assets/evidence-architecture-cinematic-1280.webp";
import phoneSmall from "@/assets/bcxmet-simulator-cinematic-640.webp";
import phone from "@/assets/bcxmet-simulator-cinematic-1280.webp";

const illustrations = {
  voynich: {
    small: voynichSmall,
    full: voynich,
    width: 768,
    height: 1296,
    alt: "Conceptual botanical manuscript with invented markings, inspired by Voynich research.",
    caption: "Voynich · artistic illustration, not an artifact reproduction or proposed reading.",
  },
  "linear-a": {
    small: linearSmall,
    full: linear,
    width: 768,
    height: 1296,
    alt: "Conceptual Minoan clay tablet with invented marks, inspired by Linear A research.",
    caption: "Linear A · artistic illustration, not an artifact reproduction or proposed reading.",
  },
  rongorongo: {
    small: rongoSmall,
    full: rongo,
    width: 768,
    height: 1296,
    alt: "Conceptual carved wooden glyph board with invented marks, inspired by Rongorongo research.",
    caption:
      "Rongorongo · artistic illustration, not an artifact reproduction or proposed reading.",
  },
  architecture: {
    small: systemSmall,
    full: system,
    width: 1280,
    height: 720,
    alt: "Conceptual cyan evidence threads crossing five glass planes with violet challenge and a gold boundary.",
    caption:
      "Research architecture · conceptual illustration, not deployed infrastructure or evidence of a breakthrough.",
  },
  phone: {
    small: phoneSmall,
    full: phone,
    width: 1280,
    height: 720,
    alt: "Conceptual Android phone with an abstract cyan Orb and a restrained cyan-gold comet ribbon.",
    caption:
      "BCXMET · conceptual product illustration, not an Android screenshot. Interactive simulation below.",
  },
};
export type IllustrationSubject = keyof typeof illustrations;
export interface SectionIllustrationProps {
  subject: IllustrationSubject;
  loading?: "lazy" | "eager";
}
export function SectionIllustration({ subject, loading = "lazy" }: SectionIllustrationProps) {
  const art = illustrations[subject];
  const smallWidth = art.width === 768 ? 480 : 640;
  return (
    <figure className="section-illustration" data-subject={subject}>
      <picture>
        <img
          src={art.full}
          srcSet={`${art.small} ${smallWidth}w, ${art.full} ${art.width}w`}
          sizes={
            art.width === 768 ? "(min-width: 768px) 30vw, 92vw" : "(min-width: 1280px) 1280px, 92vw"
          }
          width={art.width}
          height={art.height}
          alt={art.alt}
          loading={loading}
          decoding="async"
        />
      </picture>
      <figcaption>{art.caption}</figcaption>
    </figure>
  );
}
