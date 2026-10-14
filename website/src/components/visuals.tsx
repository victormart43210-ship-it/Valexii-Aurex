import { useEffect, useId, useRef, useState } from "react";
import {
  ArrowRight,
  ArrowLeft,
  Layers,
  ScanSearch,
  ShieldCheck,
  Smartphone,
  Database,
  Accessibility,
  Server,
  Users,
  MessageSquare,
  History,
  Home,
  Ellipsis,
  Pause,
  Play,
  PhoneOff,
  Zap,
  CircleHelp,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { PresentationOrb } from "@/components/presentation-orb";
import { OrbEvidenceTour } from "@/components/orb-evidence-tour";
import { orbStates, orbDescriptions, type OrbState } from "@/components/orb-states";

export function CanonicalOrb({ compact = false }: { compact?: boolean }) {
  return <PresentationOrb compact={compact} />;
}

import { PhoneTopicPicker, PhoneDetailPanel } from "@/components/phone-context";
import {
  phoneViews as views,
  getDemoTelemetry,
  type DemoPhase,
  type DemoKind,
  type PhoneView as ProductView,
} from "@/components/phone-scenarios";
import { PhoneScanReadout } from "@/components/orb-instruments";
import { SpectrumRadar, FieldDomains } from "@/components/spectrum-radar";
import { TelemetryUniverse } from "@/components/telemetry-universe";
import { FlagshipJourneys } from "@/components/flagship-journeys";
import { CommandCenter } from "@/components/command-center";
import { emitActivation } from "@/lib/activation-events";
export function ProductComposition({
  initialView = "Home",
  initialOrbState = "REST",
  expandedDetails = false,
  showFlagships = true,
  fullCommand = false,
  scenarioRequest,
}: {
  initialView?: ProductView;
  initialOrbState?: OrbState;
  expandedDetails?: boolean;
  showFlagships?: boolean;
  fullCommand?: boolean;
  scenarioRequest?: { kind: "routine" | "qualified"; serial: number } | undefined;
}) {
  const [view, updateView] = useState<ProductView>(initialView);
  const [detailOpen, setDetailOpen] = useState(expandedDetails);
  const [demoControlsOpen, setDemoControlsOpen] = useState(true);
  const setView = (next: ProductView) => {
    if (next === "Command Center") emitActivation("command_open");
    updateView(next);
    setDetailOpen(true);
  };
  const id = useId();
  const screenViewport = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (screenViewport.current) screenViewport.current.scrollTop = 0;
  }, [view]);
  const [orbState, setOrbState] = useState<OrbState>(initialOrbState);
  const [motion, setMotion] = useState(true);
  const [demoEvent, setDemoEvent] = useState<{
    kind: DemoKind;
    serial: number;
  } | null>(null);
  const [demoPhase, setDemoPhase] = useState<DemoPhase>("idle");
  useEffect(() => {
    if (scenarioRequest) {
      updateView("Home");
      if (screenViewport.current) screenViewport.current.scrollTop = 0;
      setDemoEvent(scenarioRequest);
    }
  }, [scenarioRequest]);
  const requestedEvent = demoEvent;
  useEffect(() => {
    if (!requestedEvent) return;
    setDemoPhase("review");
    const returnTimer = window.setTimeout(
      () => setDemoPhase("returning"),
      requestedEvent.kind === "routine" ? 1800 : 4200,
    );
    const restTimer = window.setTimeout(
      () => setDemoPhase("complete"),
      requestedEvent.kind === "routine" ? 2700 : 6500,
    );
    return () => {
      window.clearTimeout(returnTimer);
      window.clearTimeout(restTimer);
    };
  }, [requestedEvent]);
  const telemetry = getDemoTelemetry(demoPhase, demoEvent?.kind ?? null);
  const displayOrbState = demoEvent ? telemetry.orb : orbState;
  const triggerDemo = (kind: DemoKind) => {
    setView("Home");
    if (screenViewport.current) screenViewport.current.scrollTop = 0;
    setDemoPhase("review");
    setDemoEvent({ kind, serial: Date.now() });
  };
  const [analyst, setAnalyst] = useState(false);
  const [selections, setSelections] = useState<Record<ProductView, number>>({
    Home: 0,
    "Command Center": 0,
    XAELI: 0,
    Activity: 0,
    More: 0,
  });
  const selectTopic = (index: number) => {
    chooseTopic(view, index);
  };
  const chooseTopic = (screen: ProductView, topic: number) => {
    setSelections((current) => ({ ...current, [screen]: topic }));
    setDetailOpen(true);
    if (screen === "Command Center" && topic < 2) {
      emitActivation(topic === 0 ? "spam_card_open" : "malware_card_open");
    }
    if (screen === "XAELI" && topic === 1) emitActivation("xaeli_proof_click");
  };
  const startFlagship = (topic: number) => {
    setView("Command Center");
    chooseTopic("Command Center", topic);
    emitActivation("demo_start");
  };
  return (
    <div
      className={`product-composition premium-simulator ${fullCommand ? "command-composition" : ""}`}
    >
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 text-xs">
        <span className="text-gold">DESIGN INTENT / DEVELOPMENTAL</span>
        <span className="text-muted-foreground">Interactive conceptual demo · no live scan</span>
      </div>
      <div className="phone-chassis">
        <Tabs
          value={view}
          onValueChange={(next) => {
            const target = views.find((screen) => screen === next);
            if (target) setView(target);
          }}
        >
          <div className="phone-camera" aria-hidden="true" />
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border pb-4 pt-5">
            <span className="font-sans text-lg font-semibold">BCXMET</span>
            <span className="text-xs text-amber">Scope unresolved</span>
          </div>
          <TabsList aria-label="BCXMET concept screens" className="phone-tabs">
            {views.map((name, i) => (
              <TabsTrigger
                key={name}
                value={name}
                id={`${id}-tab-${i}`}
                aria-controls={`${id}-panel-${i}`}
                className="phone-tab"
              >
                {i === 0 ? (
                  <Home className="size-4" />
                ) : i === 1 ? (
                  <ScanSearch className="size-4" />
                ) : i === 2 ? (
                  <MessageSquare className="size-4" />
                ) : i === 3 ? (
                  <History className="size-4" />
                ) : (
                  <Ellipsis className="size-4" />
                )}
                {name}
              </TabsTrigger>
            ))}
          </TabsList>
          <div className="phone-viewport" ref={screenViewport}>
            {views.map((screen, i) => (
              <TabsContent
                key={screen}
                id={`${id}-panel-${i}`}
                aria-labelledby={`${id}-tab-${i}`}
                value={screen}
                forceMount
                hidden={view !== screen}
                className="phone-screen"
              >
                {(screen === "Home" || screen === "XAELI") && (
                  <>
                    <p className="instrument-demo-label">DEMO / SIMULATED INSTRUMENTS</p>
                    <OrbEvidenceTour
                      state={displayOrbState}
                      motion={motion}
                      telemetry={telemetry}
                      deliberate={demoEvent?.kind === "qualified" && demoPhase === "review"}
                      eventKey={demoEvent?.serial ?? 0}
                    />
                    <PhoneScanReadout telemetry={telemetry} />
                    <FieldDomains telemetry={telemetry} />
                    <SpectrumRadar telemetry={telemetry} motion={motion} />
                    <TelemetryUniverse
                      telemetry={telemetry}
                      state={displayOrbState}
                      motion={motion}
                      deliberate={demoEvent?.kind === "qualified" && demoPhase === "review"}
                      eventKey={demoEvent?.serial ?? 0}
                    />
                    <p className="mb-4 text-center text-[10px] text-muted-foreground">
                      {screen === "XAELI" ? "XAELI · " : ""}
                      {displayOrbState} · simulated presentation · no authority
                    </p>
                  </>
                )}
                <PhoneTopicPicker
                  view={screen}
                  selected={selections[screen]}
                  onSelect={(topic) => chooseTopic(screen, topic)}
                />
                {screen === "More" && (
                  <div className="mt-5 space-y-3 text-sm">
                    <label className="flex min-h-11 items-center justify-between gap-3">
                      Presentation motion
                      <input
                        type="checkbox"
                        checked={motion}
                        onChange={(e) => setMotion(e.target.checked)}
                        className="size-5 accent-primary"
                      />
                    </label>
                    <label className="flex min-h-11 items-center justify-between gap-3">
                      Analyst detail
                      <input
                        type="checkbox"
                        checked={analyst}
                        onChange={(e) => setAnalyst(e.target.checked)}
                        className="size-5 accent-primary"
                      />
                    </label>
                    {analyst && (
                      <p className="text-xs leading-6">
                        Synthetic source only · freshness unverified · authority NONE · no actual
                        device data.
                      </p>
                    )}
                  </div>
                )}
              </TabsContent>
            ))}
          </div>
        </Tabs>
        <p className="phone-footer">
          BCXMET · Powered by VALEXII.AI · BCXME THE CHANGE
          <br />
          Synthetic concept content · no live device telemetry
        </p>
      </div>
      <details
        className="phone-demo-drawer"
        open={demoControlsOpen}
        onToggle={(event) => setDemoControlsOpen(event.currentTarget.open)}
      >
        <summary aria-expanded={demoControlsOpen} aria-controls={`${id}-demo-controls`}>
          <span className="phone-demo-heading">
            <span>EXPLORE THE ORB STATES</span>
            <span className="phone-demo-subtitle">Choose a state or trigger a simulated event</span>
          </span>
          <ChevronDown className="phone-demo-chevron" aria-hidden="true" />
        </summary>
        <div id={`${id}-demo-controls`} className="phone-demo-content">
          <p className="instrument-demo-label">
            DEMO / SIMULATED · NO LIVE SCAN · ORB MOTION AUTHORITY = NONE
          </p>
          <div className="orb-state-controls">
            <label htmlFor={`${id}-orb-state`} className="text-xs text-muted-foreground">
              Orb presentation
            </label>
            <select
              id={`${id}-orb-state`}
              value={displayOrbState}
              onChange={(e) => {
                const next = orbStates.find((state) => state === e.target.value);
                if (next) {
                  setDemoEvent(null);
                  setDemoPhase("idle");
                  setOrbState(next);
                }
              }}
              className="min-h-11 min-w-0 rounded-sm border border-input bg-background px-3 text-sm"
            >
              {orbStates.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </div>
          <div className="phone-orb-actions" role="group" aria-label="Simulated comet events">
            <Button variant="outline" onClick={() => triggerDemo("scan")}>
              <ScanSearch />
              Scan demo
            </Button>
            <Button variant="outline" onClick={() => triggerDemo("review")}>
              <Layers />
              Qualified review demo
            </Button>
            <Button variant="outline" onClick={() => triggerDemo("ambiguous")}>
              <CircleHelp />
              Ambiguous demo
            </Button>
            <Button
              variant="outline"
              size="icon"
              aria-label={motion ? "Pause Orb motion" : "Play Orb motion"}
              title={motion ? "Pause Orb motion" : "Play Orb motion"}
              aria-pressed={!motion}
              onClick={() => setMotion(!motion)}
            >
              {motion ? <Pause /> : <Play />}
            </Button>
            <Button
              variant="outline"
              title="Simulated spam call blocked · no actual blocking"
              onClick={() => triggerDemo("routine")}
            >
              <PhoneOff />
              Routine call demo
            </Button>
            <Button
              variant="outline"
              title="Simulated critical attack · no actual device protection"
              onClick={() => triggerDemo("qualified")}
            >
              <Zap />
              Critical attack demo
            </Button>
          </div>
          <p className="orb-state-description" role="status">
            {orbDescriptions[displayOrbState]}
          </p>
        </div>
      </details>
      {fullCommand && (
        <CommandCenter
          selected={selections["Command Center"]}
          onSelect={(topic) => {
            setView("Command Center");
            chooseTopic("Command Center", topic);
          }}
          onXaeli={(topic) => {
            chooseTopic("XAELI", topic);
          }}
        />
      )}
      {showFlagships && <FlagshipJourneys onStart={startFlagship} />}
      <details
        className="phone-explorer"
        open={detailOpen}
        onToggle={(event) => setDetailOpen(event.currentTarget.open)}
      >
        <summary>Explore {view} · contextual evidence &amp; review</summary>
        <PhoneDetailPanel view={view} selected={selections[view]} onSelect={selectTopic} />
      </details>
    </div>
  );
}

export function VerificationDiagram() {
  return (
    <figure className="verification-visual">
      <figcaption className="mb-6 text-xs text-gold">
        DESIGN INTENT · Independent verification before consequence
      </figcaption>
      <ol className="grid gap-3 sm:grid-cols-5">
        {["Evidence", "Qualification", "Reality", "Authority", "Effect"].map((x, i) => (
          <li className="border-t-2 border-primary/50 py-4" key={x}>
            <span className="text-xs text-primary">0{i + 1}</span>
            <p className="mt-3 text-sm font-semibold">{x}</p>
          </li>
        ))}
      </ol>
      <div className="mt-6 grid gap-4 md:grid-cols-[1fr_auto_1fr]">
        <div className="verification-path">
          <ArrowRight className="size-5 text-primary" aria-hidden="true" />
          <p>Forward evidence</p>
          <span>Observation → proposed consequence</span>
        </div>
        <div className="grid place-items-center border border-gold/40 p-4 text-center text-xs text-gold">
          Converge
          <br />
          or HOLD
        </div>
        <div className="verification-path">
          <ArrowRight className="size-5 rotate-180 text-analyze" aria-hidden="true" />
          <p>Independent reverse reconstruction</p>
          <span>Proposed consequence → supporting evidence</span>
        </div>
      </div>
      <p className="mt-6 text-xs leading-6 text-muted-foreground">
        Witness ≠ Truth · Witness ≠ Authority. No effect without revalidation. The system may never
        be its own sole witness.
      </p>
    </figure>
  );
}

export function ResearchGraphic() {
  return (
    <figure className="research-graphic">
      <figcaption className="mb-6 text-xs text-gold">
        RESEARCH GRAPHIC · Original schematic, not manuscript imagery or a translation
      </figcaption>
      <div className="grid gap-8 md:grid-cols-2">
        <svg
          viewBox="0 0 400 300"
          role="img"
          aria-label="Schematic corpus records grouped by boundaries and linked to structural hypotheses; no historical glyphs or measured data."
        >
          <rect
            x="20"
            y="15"
            width="220"
            height="265"
            rx="4"
            fill="var(--background)"
            stroke="var(--border)"
          />
          {Array.from({ length: 9 }, (_, i) => (
            <g key={i} stroke={i % 3 === 0 ? "var(--gold)" : "var(--primary)"} strokeOpacity=".65">
              {Array.from({ length: 6 }, (_, j) => (
                <path
                  key={j}
                  d={`M ${40 + j * 30} ${45 + i * 24} h ${10 + (j % 3) * 5}`}
                  strokeWidth="2"
                />
              ))}
              <path d={`M260 ${45 + i * 24} L330 ${65 + (i % 3) * 80}`} strokeOpacity=".25" />
            </g>
          ))}
          {[65, 145, 225].map((y, i) => (
            <g key={y}>
              <circle cx="335" cy={y} r="18" fill="var(--card)" stroke="var(--primary)" />
              <text x="335" y={y + 4} fill="var(--foreground)" textAnchor="middle" fontSize="12">
                {i + 1}
              </text>
            </g>
          ))}
        </svg>
        <div className="grid content-center gap-5">
          {[
            ["Corpus control", "Preserve transcription and source identity"],
            ["Structure", "Test segmentation, local order and matched nulls"],
            ["Reconstruction", "Held-out prediction, reverse encoding, replication"],
          ].map(([t, c], i) => (
            <div className="border-l border-primary/50 pl-4" key={t}>
              <p className="text-xs text-primary">
                0{i + 1} / {t}
              </p>
              <p className="mt-2 text-sm leading-6">{c}</p>
            </div>
          ))}
        </div>
      </div>
      <p className="mt-5 text-xs text-amber">
        Semantic status: HOLD / NOT ESTABLISHED · Evidence attachment required
      </p>
    </figure>
  );
}

export function HarnessGraphic() {
  return (
    <figure className="harness-graphic">
      <figcaption className="mb-6 text-xs text-gold">
        INTERNAL MOCK / SYNTHETIC HARNESS EVALUATION / EVIDENCE ATTACHMENT REQUIRED
      </figcaption>
      <div className="grid gap-7 md:grid-cols-[1.2fr_1fr]">
        <div>
          <div
            className="harness-grid"
            role="img"
            aria-label="Twenty schematic domain tiles: nineteen reported full computational-domain scores, and one epistemic-calibration domain containing all 35 reported correlated misses. Not individual question records."
          >
            {Array.from({ length: 20 }, (_, i) => (
              <span key={i} className={i === 19 ? "harness-tile harness-misses" : "harness-tile"}>
                {String(i + 1).padStart(2, "0")}
              </span>
            ))}
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            Domain schematic · not item-level evidence
          </p>
        </div>
        <div>
          <p className="font-display text-4xl text-primary">4,965 / 5,000</p>
          <p className="mt-3 text-sm">Reported internal result · 99.30%</p>
          <div className="mt-6 border-l-2 border-amber pl-4">
            <p className="font-display text-3xl text-amber">35 correlated misses</p>
            <p className="mt-3 text-xs leading-6">
              One IR-capability wording case; item-level records remain unattached. Correlation may
              reveal a systematic gap.
            </p>
          </div>
        </div>
      </div>
      <p className="mt-6 text-xs leading-6 text-muted-foreground">
        NOT official Humanity’s Last Exam · NOT a live XAELI benchmark · NOT independently validated
      </p>
    </figure>
  );
}

export function ValidationPanels() {
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {[
        [
          Smartphone,
          "Physical-device testing",
          "PLANNED · Device qualification, not a passed hardware gate",
        ],
        [
          ShieldCheck,
          "Independent validation",
          "PLANNED · Security review and adversarial challenge",
        ],
        [
          Accessibility,
          "Accessibility matrix",
          "PLANNED · Screen readers, keyboard, touch and device diversity",
        ],
        [Server, "Compute / infrastructure", "PLANNED · Reproducible evaluation environments"],
        [Database, "Datasets / research", "PLANNED · Corpus provenance and inspectable artifacts"],
        [Users, "Research collaboration", "Open invitation · no partner commitments implied"],
      ].map(([Icon, title, copy]) => {
        const Symbol = Icon as typeof Smartphone;
        return (
          <article key={String(title)} className="validation-panel">
            <div className="validation-symbol" aria-hidden="true">
              <Symbol className="size-10" />
              <span className="validation-filament" />
            </div>
            <h2 className="mt-5 font-display text-xl">{String(title)}</h2>
            <p className="mt-3 text-xs leading-6 text-muted-foreground">{String(copy)}</p>
          </article>
        );
      })}
    </div>
  );
}

export function CometDynamics() {
  const [event, setEvent] = useState<"routine" | "qualified">("routine");
  const [scenarioRequest, setScenarioRequest] = useState<{
    kind: "routine" | "qualified";
    serial: number;
  }>();
  return (
    <div className={`comet-dynamics comet-${event}`}>
      <svg className="comet-environment" viewBox="0 0 700 800" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="hero-comet-line">
            <stop stopColor="var(--primary)" stopOpacity="0" />
            <stop offset=".65" stopColor="var(--cyan)" stopOpacity=".65" />
            <stop offset="1" stopColor="var(--gold)" stopOpacity=".85" />
          </linearGradient>
        </defs>
        <g fill="none" stroke="url(#hero-comet-line)">
          <path
            className="comet-stream"
            d="M20 720 Q90 470 350 335 Q520 245 680 55"
            strokeWidth="2"
          />
          <path
            d="M0 670 Q110 480 350 335 Q530 230 650 20 M50 800 Q150 460 350 335 Q590 230 700 90"
            strokeWidth=".6"
          />
        </g>
        <g className="comet-particles" fill="var(--cyan)">
          {Array.from({ length: 24 }, (_, i) => (
            <circle
              key={i}
              cx={365 + i * 12}
              cy={315 - i * 11 + (i % 3) * 8}
              r={i % 4 === 0 ? 2 : 1}
              opacity={0.25 + (i % 4) * 0.15}
            />
          ))}
        </g>
        <path d="M540 130 h40 m-20 -20 v40 M100 570 h35" stroke="var(--gold)" strokeOpacity=".5" />
      </svg>
      <ProductComposition showFlagships={false} scenarioRequest={scenarioRequest} />
      <div
        className="relative z-10 mt-6 flex flex-wrap justify-center gap-2"
        role="group"
        aria-label="Synthetic presentation scenarios"
      >
        <Button
          variant={event === "routine" ? "secondary" : "ghost"}
          aria-pressed={event === "routine"}
          onClick={() => {
            setEvent("routine");
            setScenarioRequest({ kind: "routine", serial: Date.now() });
          }}
        >
          Routine demo
        </Button>
        <Button
          variant={event === "qualified" ? "secondary" : "ghost"}
          aria-pressed={event === "qualified"}
          onClick={() => {
            setEvent("qualified");
            setScenarioRequest({ kind: "qualified", serial: Date.now() });
          }}
        >
          Qualified event demo
        </Button>
      </div>
      <p
        className="relative mt-3 text-center text-xs leading-6 text-muted-foreground"
        role="status"
      >
        {event === "routine"
          ? "Synthetic routine call review · no blocking · restrained presentation"
          : "Synthetic serious event · qualification assumed for illustration, not measured"}
        <br />
        ORB MOTION AUTHORITY = NONE · no security state is decided here
      </p>
    </div>
  );
}
