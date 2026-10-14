import exact from "../../public/assets/bcxmet-celestial-comet-home.jpg.asset.json";
import mobile from "../../public/assets/bcxmet-celestial-comet-home-mobile.webp.asset.json";
import { usePresentationActivity } from "@/hooks/use-presentation-activity";

export function HomeHeroArt() {
  const { ref, active } = usePresentationActivity();
  return (
    <section
      ref={ref}
      className="hero-art-layer"
      data-motion={active ? "active" : "paused"}
      aria-label="Celestial comet artwork"
    >
      <picture data-hero-art="exact-upload">
        <source
          media="(max-width: 1023px)"
          srcSet={`${mobile.url} 960w, ${exact.url} 1536w`}
          sizes="100vw"
        />
        <img
          src={exact.url}
          srcSet={`${mobile.url} 960w, ${exact.url} 1536w`}
          sizes="100vw"
          width={1536}
          height={864}
          fetchPriority="high"
          decoding="async"
          alt="User-supplied blue-and-gold celestial comet above a golden futuristic observatory city and reflective water."
          className="hero-art"
        />
      </picture>
      <svg className="hero-atmosphere" viewBox="0 0 1536 864" aria-hidden="true" focusable="false">
        <g className="hero-ion-filaments" fill="none" stroke="var(--cyan)">
          <path d="M1130 60 Q970 150 770 295" />
          <path d="M1220 50 Q1050 190 790 312" />
          <path d="M1300 100 Q1090 220 820 326" />
        </g>
        <g className="hero-gold-filament" fill="none" stroke="var(--gold)">
          <path d="M1210 98 Q1000 170 805 311" />
        </g>
        <g className="hero-depth-particles">
          {Array.from({ length: 18 }, (_, i) => (
            <circle
              key={i}
              cx={560 + ((i * 137) % 850)}
              cy={45 + ((i * 83) % 380)}
              r={i % 4 === 0 ? 1.8 : 0.8}
            />
          ))}
        </g>
      </svg>
    </section>
  );
}
