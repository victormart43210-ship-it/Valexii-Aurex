import { useRef, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { examineSyntheticManuscript } from "@/lib/manuscript.functions";
import { selectedLayer, type ManuscriptLayer, type ManuscriptReport } from "@/lib/manuscript-contract";
import { Button } from "@/components/ui/button";

const FIXTURES = [
  ["faint-stroke-v1", "Faint bar"],
  ["blank-v1", "Blank field"],
  ["noise-v1", "Isolated noise"],
  ["overlap-v1", "Overlapping bars"],
] as const;

export function ManuscriptForensicsLab() {
  const examine = useServerFn(examineSyntheticManuscript);
  const requestSeq = useRef(0);
  const [fixture, setFixture] = useState<(typeof FIXTURES)[number][0]>("faint-stroke-v1");
  const [busy, setBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [report, setReport] = useState<ManuscriptReport | null>(null);
  const [method, setMethod] = useState("grayscale");
  const [opacity, setOpacity] = useState(70);

  async function run() {
    const requestId = ++requestSeq.current;
    setBusy(true);
    setErrorMsg(null);
    try {
      const next = await examine({ data: { fixture } });
      if (requestId !== requestSeq.current) return;
      setReport(next);
    } catch (err: unknown) {
      if (requestId !== requestSeq.current) return;
      setReport(null);
      setErrorMsg(err instanceof Error ? err.message : "The laboratory did not return a report");
    } finally {
      if (requestId === requestSeq.current) setBusy(false);
    }
  }

  const original = report ? selectedLayer(report, "original_rgb") : null;
  const active = report ? selectedLayer(report, method) : null;

  return (
    <div className="mt-8 border border-border bg-card/40 p-4 sm:p-6">
      <p className="text-xs uppercase tracking-wider text-gold">Tier 1 · Synthetic fixtures only</p>
      <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
        The laboratory measures pixels in a supplied image. It does not transcribe them, assign a
        wavelength to an ordinary color file, or see through paint. XAELI is not connected here.
      </p>
      <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="text-sm" htmlFor="forensic-fixture">
          Fixture
          <select
            id="forensic-fixture"
            className="ml-0 mt-2 block min-h-11 w-full border border-border bg-background px-3 sm:ml-3 sm:mt-0 sm:inline-block sm:w-auto"
            value={fixture}
            onChange={(event) => setFixture(event.target.value as (typeof FIXTURES)[number][0])}
          >
            {FIXTURES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <Button type="button" className="min-h-11" disabled={busy} onClick={() => void run()}>
          {busy ? "Measuring…" : "Examine synthetic fixture"}
        </Button>
      </div>
      {errorMsg && (
        <p role="alert" className="mt-4 text-sm text-destructive">
          {errorMsg}
        </p>
      )}
      {report && original && active && (
        <LaboratoryResult
          report={report}
          original={original}
          active={active}
          method={method}
          opacity={opacity}
          onMethod={setMethod}
          onOpacity={setOpacity}
        />
      )}
    </div>
  );
}

function LaboratoryResult({
  report,
  original,
  active,
  method,
  opacity,
  onMethod,
  onOpacity,
}: {
  report: ManuscriptReport;
  original: ManuscriptLayer;
  active: ManuscriptLayer;
  method: string;
  opacity: number;
  onMethod: (method: string) => void;
  onOpacity: (opacity: number) => void;
}) {
  function download() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `manuscript-forensics-${report.fixture ?? "report"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(16rem,0.8fr)]">
      <div>
        <div className="relative inline-block max-w-full border border-border bg-background p-2">
          <img
            alt="Decoded synthetic fixture. This is the original color image, not a reading."
            className="block h-auto max-w-full"
            style={{ imageRendering: "pixelated" }}
            src={`data:image/png;base64,${original.png_base64}`}
          />
          <img
            alt={`Processed layer ${active.method}. Display opacity does not change the stored pixels.`}
            className="absolute left-2 top-2 h-[calc(100%-1rem)] w-[calc(100%-1rem)]"
            style={{ opacity: opacity / 100, imageRendering: "pixelated" }}
            src={`data:image/png;base64,${active.png_base64}`}
          />
        </div>
        <label className="mt-4 block text-sm" htmlFor="forensic-opacity">
          Display opacity {opacity}%. The slider does not change the image hash.
          <input
            id="forensic-opacity"
            className="mt-2 block w-full"
            type="range"
            min={0}
            max={100}
            value={opacity}
            onChange={(event) => onOpacity(Number(event.target.value))}
          />
        </label>
      </div>
      <div className="text-sm leading-6">
        <p>
          Decision {report.decision}. Effect {report.effect}. Decipherment {report.decipherment}.
          Recovered text: none.
        </p>
        <p className="mt-2 font-mono text-xs text-muted-foreground">
          Source {report.source_sha256?.slice(0, 16) ?? "none"} · {report.observation}
        </p>
        <label className="mt-4 block" htmlFor="forensic-layer">
          Layer
          <select
            id="forensic-layer"
            className="mt-2 block min-h-11 w-full border border-border bg-background px-3"
            value={method}
            onChange={(event) => onMethod(event.target.value)}
          >
            {report.layers.map((layer) => (
              <option key={layer.id} value={layer.method}>
                {layer.method}
              </option>
            ))}
          </select>
        </label>
        <p className="mt-3 text-muted-foreground">{active.limitations.join(" ")}</p>
        <p className="mt-2 font-mono text-xs">Layer {active.sha256.slice(0, 16)}</p>
        <h3 className="mt-5 font-display text-xl">Unverified components</h3>
        {report.regions.length === 0 ? (
          <p className="mt-2 text-muted-foreground">No component passed the size minimum.</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {report.regions.map((region) => (
              <li key={region.id} className="border border-border p-2 font-mono text-xs">
                {region.id} · {region.classification} · {region.pixels} px · reading none
              </li>
            ))}
          </ul>
        )}
        <Button type="button" variant="glass" className="mt-4 min-h-11" onClick={download}>
          Download evidence report
        </Button>
      </div>
    </div>
  );
}
