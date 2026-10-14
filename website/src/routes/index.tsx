import { ReasoningSpine } from "@/components/reasoning-spine";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, ShieldCheck, MessageSquare, Factory, ChartNoAxesCombined } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageShell, Eyebrow, SectionHeading } from "@/components/site";
import { FlagshipJourneys } from "@/components/flagship-journeys";
import { CometDynamics, VerificationDiagram } from "@/components/visuals";
import { HomeHeroArt } from "@/components/home-hero-art";
import { HomeCoreAmbience } from "@/components/home-core-ambience";
import heroOriginal from "../../public/assets/bcxmet-celestial-comet-home.jpg.asset.json";
import heroMobile from "../../public/assets/bcxmet-celestial-comet-home-mobile.webp.asset.json";
import guardianEye from "../../public/assets/bcxmet-guardian-eye-logo.jpg.asset.json";
import phones from "@/assets/bcxmet-five-screens.webp";
import architecture from "@/assets/valexii-system.webp";
import lux from "@/assets/valexii-lux.webp";
export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "VALEXII.AI — Privacy-centered Android security & governed AI" },
      {
        name: "description",
        content:
          "VALEXII.AI is building BCXMET Android security and evidence-governed AI. Explore simulated reviews, human control and independent research—not live protection.",
      },
      { property: "og:title", content: "VALEXII.AI — BCXMET · BCXME THE CHANGE" },
      {
        property: "og:description",
        content:
          "Your digital life belongs to you. Explore BCXMET’s developmental Android security vision: evidence-aware review, visible limits and human control.",
      },
      { property: "og:url", content: "https://valexii.com/" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:image", content: "https://valexii.com/og-valexii.jpg" },
      { name: "twitter:image", content: "https://valexii.com/og-valexii.jpg" },
      { property: "og:image:width", content: "1200" },
      { property: "og:image:height", content: "630" },
    ],
    links: [
      { rel: "canonical", href: "https://valexii.com/" },
      {
        rel: "preload",
        as: "image",
        href: heroOriginal.url,
        imageSrcSet: `${heroMobile.url} 960w, ${heroOriginal.url} 1536w`,
        imageSizes: "100vw",
      },
    ],
  }),
  component: Home,
});
function Home() {
  return (
    <PageShell>
      <div className="home-core-page">
        <HomeCoreAmbience />
        <section className="cinematic-hero home-identity-hero">
          <HomeHeroArt />
          <div className="home-chapter-divider" aria-hidden="true">
            <svg viewBox="0 0 640 32" fill="none" focusable="false">
              <g stroke="currentColor" strokeWidth="1">
                <path d="M8 16H272 M368 16H632 M68 21H246 M394 21H572" />
                <path d="M246 16c14 0 16-10 30-10 9 0 15 4 18 10-3 6-9 10-18 10-6 0-8-3-8-5s2-4 5-3 M394 16c-14 0-16-10-30-10-9 0-15 4-18 10 3 6 9 10 18 10 6 0 8-3 8-5s-2-4-5-3" />
              </g>
              <path
                className="home-divider-comet"
                d="m308 16 12-7 12 7-12 7-12-7Zm12-7 19-6-7 13"
              />
            </svg>
          </div>
          <figure className="home-guardian-art">
            <img
              src={guardianEye.url}
              width={1536}
              height={1536}
              decoding="async"
              alt="Original BCXMET Guardian Eye artwork: ornate gold and teal guardian surrounding a cyan comet iris, with the complete BCXMET wordmark."
            />
          </figure>
          <div className="site-grid cinematic-layout">
            <div className="cinematic-copy">
              <h1>
                <span className="home-bcxmet-brand">BCXMET</span>
                <span className="home-bcxmet-hook">
                  Your digital life
                  <br />
                  <span className="text-primary">belongs to you.</span>
                </span>
              </h1>
              <p className="hero-subhead">
                VALEXII.AI is building privacy-centered Android security and AI that answers to
                evidence—and to people. Conceptual Android security preview. No live call blocking,
                scanning or verified protection.
              </p>
              <div className="hero-actions">
                <Button asChild variant="hero">
                  <Link to="/bcxmet" hash="command-center" data-activation="command_open">
                    Explore BCXMET <ArrowRight />
                  </Link>
                </Button>
                <Button asChild variant="glass">
                  <Link to="/system">
                    Our evidence philosophy <ArrowRight />
                  </Link>
                </Button>
                <Button asChild variant="glass">
                  <a href="#spam-demo" data-activation="hero_call_click">
                    Review a call <ArrowRight />
                  </a>
                </Button>
                <Button asChild variant="glass">
                  <a href="#malware-demo" data-activation="hero_malware_click">
                    Review an app <ArrowRight />
                  </a>
                </Button>
              </div>
              <p className="hero-brand">
                Powered by VALEXII.AI · BCXME THE CHANGE
                <br />
                V43 DESIGN INTENT / DEVELOPMENTAL
              </p>
            </div>
            <h2 className="sr-only">Simulated BCXMET instrument preview</h2>
            <CometDynamics />
          </div>
        </section>
        <ReasoningSpine context="home" />
        <section className="home-band border-t border-border">
          <div className="site-grid">
            <SectionHeading
              eyebrow="Your phone holds your private life · simulated reviews"
              title="A familiar voice. An unfamiliar request."
              copy="Calls and apps can ask for more trust than they deserve. Explore how evidence-aware review could help you pause, understand and choose. These simulations do not replace Android protections."
            />
            <FlagshipJourneys />
            <div className="mt-5 flex flex-wrap gap-3">
              <Button asChild variant="glass">
                <Link to="/bcxmet">
                  Open full phone demo <ArrowRight />
                </Link>
              </Button>
              <Button asChild variant="glass">
                <Link to="/build-with-us">
                  Build with us <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </section>
        <section className="founding-band" id="founding-support">
          <div className="site-grid grid gap-7 lg:grid-cols-[1.1fr_1fr]">
            <div>
              <Eyebrow>Independent work needs independent support</Eyebrow>
              <h2 className="font-display text-3xl">Become an early supporter of BCXMET.</h2>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Suggested founding contribution: $50—any amount is welcome. Contributions support
                engineering, research, testing and independent verification. They are voluntary: not
                a purchase, subscription or investment, and they guarantee no item, access or
                outcome.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Button asChild variant="hero" className="founding-button">
                  <a
                    href="https://cash.app/$illuminaughty210"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Support via Cash App <ArrowRight />
                  </a>
                </Button>
                <Button asChild variant="glass">
                  <Link to="/support">
                    Support details <ArrowRight />
                  </Link>
                </Button>
              </div>
            </div>
            <div>
              <h3 className="font-display text-xl">THE DECIPHERMENT FRONTIER</h3>
              <p className="mt-3 text-sm leading-7 text-muted-foreground">
                Three ancient mysteries. One disciplined approach to discovery. Follow patterns,
                competing hypotheses, reproducibility checks and failed tests—without a claimed
                decipherment.
              </p>
              <Button asChild variant="glass" className="mt-4">
                <Link to="/decipherment-frontier">
                  Explore the planned briefing <ArrowRight />
                </Link>
              </Button>
              <p className="mt-3 text-xs leading-6 text-muted-foreground">
                Newsletter signup is not active. No address is collected while it is disabled.
              </p>
              <p className="mt-4 text-xs leading-6 text-muted-foreground">
                Optional USB archive of public project materials, artwork and research summaries, by
                request only: availability, contents, costs and fulfillment need individual
                confirmation—no automatic entitlement or shipping-address collection. Future APK or
                QR download access is planned only after independent signed/hash verification; no
                unverified sideloading offer.
              </p>
            </div>
          </div>
        </section>
        <section className="home-band">
          <div className="site-grid">
            <SectionHeading
              eyebrow="From security app to governed intelligence"
              title="Privacy is personal. Proof matters."
              copy="People remain in control. Our mission began with Android security and grew into a harder question: how can intelligence explain its basis without granting itself power? This is a development story, not a release claim."
            />
            <ol className="origin-line">
              {[
                "Security app",
                "Android iteration",
                "Evidence rules",
                "Authority & revocation",
                "BCXMET + VALEXII Core",
              ].map((x, i) => (
                <li key={x}>
                  <span>0{i + 1}</span>
                  {x}
                </li>
              ))}
            </ol>
            <figure className="mt-7">
              <img
                src={phones}
                width={1536}
                height={1024}
                loading="lazy"
                alt="Original illustrative five-phone composition for BCXMET Home, Command Center, XAELI, Activity and More; conceptual artwork, not production screens."
                className="product-panorama"
              />
              <figcaption className="mt-3 text-xs leading-6 text-muted-foreground">
                Generated product artwork · DESIGN INTENT / DEVELOPMENTAL. Lettering and screen
                details are illustrative; the interactive coded demo above defines the canonical
                journeys.
              </figcaption>
            </figure>
          </div>
        </section>
        <section className="home-band border-y border-border" id="architecture">
          <div className="site-grid">
            <div className="flex flex-wrap items-end justify-between gap-5">
              <SectionHeading
                eyebrow="VALEXII verification framework"
                title="Evidence before effect."
                copy="What was observed? Does it hold up? Who permits the next step? Our design separates those questions. UNKNOWN ≠ SAFE; stale or missing ≠ PASS."
              />
              <Button asChild variant="glass">
                <Link to="/system">
                  Understand the framework <ArrowRight />
                </Link>
              </Button>
            </div>
            <figure className="mt-7">
              <img
                src={architecture}
                width={1536}
                height={1024}
                loading="lazy"
                alt="Conceptual evidence architecture: Evidence, Qualification, Reality, Authority and Effect linked forward by cyan lineage and independently backward by gold verification."
                className="architecture-art"
              />
              <figcaption className="mt-3 text-xs text-muted-foreground">
                Original conceptual artwork—not a proprietary implementation diagram.
              </figcaption>
            </figure>
            <VerificationDiagram />
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <h3 className="font-display text-xl">A changed permission is not proof of harm.</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  The design asks what changed, whether the source is current and whether an
                  ordinary update explains it. Only then can a person review a response. An
                  unresolved question means HOLD—not a verdict and not permission.
                </p>
              </div>
              <div>
                <h3 className="font-display text-xl">Trace the result back to its source</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  Result → Authority → Truth → Admissibility → Source. Reconstruct the justification
                  independently. Revocation stops future permission; it does not erase history.
                  Effects require current authority.
                </p>
                <Button asChild variant="link" className="mt-2 px-0">
                  <a
                    href="https://github.com/victormart43210-ship-it/Valexii-Aurex"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    AUREX public challenge <ArrowRight />
                  </a>
                </Button>
                <p className="text-xs text-amber">
                  CI verification not passed yet · independent qualification not established
                </p>
              </div>
            </div>
          </div>
        </section>
        <section className="home-band">
          <div className="site-grid">
            <SectionHeading
              eyebrow="VALEXII.AI · Products and research directions"
              title="One umbrella. Distinct responsibilities."
              copy="BCXMET is our first product focus. XAELI is its planned explanation interface. Industrial and capital intelligence are separate research directions—not connected production services."
            />
            <div className="ecosystem-shell">
              <div className="shell-heading">
                <span className="text-gold">VALEXII.AI</span>
                <span>Evidence · Verification · Human authority</span>
              </div>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {[
                  {
                    n: "BCXMET",
                    to: "/bcxmet",
                    s: "Active development",
                    c: "Android security in development; simulated call and app reviews.",
                    I: ShieldCheck,
                  },
                  {
                    n: "XAELI",
                    to: "/xaeli",
                    s: "Developmental",
                    c: "A planned assistant for evidence, limits and informed review.",
                    I: MessageSquare,
                  },
                  {
                    n: "DISPATER.AI",
                    to: "/dispater",
                    s: "Industrial / resource · Future direction",
                    c: "Explore bounded operational decision support.",
                    I: Factory,
                  },
                  {
                    n: "XAITA.AI",
                    to: "/xaita",
                    s: "Finance / markets · Future direction",
                    c: "Explore qualified market evidence, not trading promises.",
                    I: ChartNoAxesCombined,
                  },
                ].map(({ n, to, s, c, I }) => (
                  <article key={n} className="shell-node">
                    <I aria-hidden="true" className="size-7 text-primary" />
                    <h3 className="mt-4 font-display text-xl">{n}</h3>
                    <p className="mt-3 text-xs text-gold">{s}</p>
                    <p className="mt-4 text-sm leading-6 text-muted-foreground">{c}</p>
                    <Button asChild variant="link" className="mt-3 px-0">
                      <Link to={to}>
                        Explore <ArrowRight />
                      </Link>
                    </Button>
                  </article>
                ))}
              </div>
            </div>
            <Button asChild variant="glass" className="mt-5">
              <Link to="/ecosystem">
                Explore the ecosystem <ArrowRight />
              </Link>
            </Button>
          </div>
        </section>
        <section className="home-band lux-band">
          <div className="site-grid grid items-center gap-8 lg:grid-cols-2">
            <figure>
              <img
                src={lux}
                width={1024}
                height={1024}
                loading="lazy"
                alt="Original LUX observatory artwork: precision astronomical research wheel with calendar rings and a celestial lens; not a historical manuscript or translation."
                className="lux-art"
              />
              <figcaption className="mt-3 text-xs text-muted-foreground">
                Original conceptual research instrument artwork.
              </figcaption>
            </figure>
            <div>
              <Eyebrow>Last, a wider horizon</Eyebrow>
              <h2 className="font-display text-3xl sm:text-4xl">LUX OBSERVATORY</h2>
              <p className="mt-5 text-sm leading-7 text-muted-foreground">
                Curiosity reaches beyond the phone. Manuscripts, calendars and astronomy offer
                questions worth testing. Voynich, Linear A and Rongorongo are research tracks—not
                solved scripts. LUX contributes observations, never security authority.
              </p>
              <p className="mt-4 text-xs leading-7 text-amber">
                INTERNAL-PREPUBLICATION / EVIDENCE ATTACHMENT REQUIRED
                <br />
                SEMANTIC INTERPRETATION NOT ESTABLISHED · HOLD
              </p>
              <p className="mt-4 text-sm leading-7 text-muted-foreground">
                Internal synthetic evaluation asks where reasoning fails and when to abstain.
                Numerical results are withheld here pending inspectable artifacts—not official HLE,
                not a live XAELI benchmark and not independently verified.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Button asChild variant="glass">
                  <Link to="/research">
                    Explore research <ArrowRight />
                  </Link>
                </Button>
                <Button asChild variant="glass">
                  <Link to="/evaluation">
                    Evaluation limits <ArrowRight />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </PageShell>
  );
}
