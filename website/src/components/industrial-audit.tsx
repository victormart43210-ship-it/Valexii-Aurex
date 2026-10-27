import { useRef, useState } from "react";
import type { IndustrialFixture, IndustrialResult } from "../lib/industrial-contract";

/** Shared presentation for owner workbench and isolated local preview. No secrets. */
export function IndustrialAudit({
  run,
  mode = "STAGING SYNTHETIC",
}: {
  run: (fixture: IndustrialFixture) => Promise<IndustrialResult>;
  mode?: "STAGING SYNTHETIC" | "LOCAL SANDBOX";
}) {
  const [fixture, setFixture] = useState<IndustrialFixture>("towing_v1");
  const [result, setResult] = useState<IndustrialResult | null>(null);
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  async function submit() {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setResult(null);
    try {
      setResult(await run(fixture));
    } catch {
      setResult({ state: "NOT_VERIFIED", report: null });
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  const report = result?.report;
  return (
    <section className="ox-dash-panel space-y-4" aria-labelledby="industrial-title">
      <p>{mode} · Fictional records only · Production HOLD</p>
      <h2 id="industrial-title">Industrial audit demonstration</h2>
      <label>
        Fictional company{" "}
        <select
          aria-label="Fictional company"
          value={fixture}
          disabled={busy}
          onChange={(e) => {
            setFixture(e.target.value as IndustrialFixture);
            setResult(null);
          }}
        >
          <option value="towing_v1">Permian Recovery Services (fictional)</option>
          <option value="oilfield_v1">Permian Field Operations (fictional)</option>
        </select>
      </label>
      <button type="button" disabled={busy} onClick={() => void submit()}>
        {busy ? "Running…" : "Run fictional audit"}
      </button>
      <p role="status">{busy ? "Request in progress" : (result?.state ?? "NOT RUN")}</p>
      {report && (
        <>
          <h3>NOW</h3>
          <p>
            {report.operator} · Fixed fixture date {report.as_of}
          </p>
          <ul>
            {report.now.map((row) => (
              <li key={row.category}>
                {row.category}: <strong>{row.status}</strong>
                <br />
                Synthetic references: {row.record_ids.join(", ") || "MISSING"}
              </li>
            ))}
          </ul>
          <h3>CHANGED</h3>
          <p>{report.changed}</p>
          <h3>NEXT</h3>
          <ul>
            {report.next.map((row) => (
              <li key={row.category}>
                {row.category}: {row.action}
              </li>
            ))}
          </ul>
          <h3>WHY</h3>
          <p>
            {report.why}. Presence does not prove authenticity; expired, conflicting or absent
            sources require review.
          </p>
          <h3>PROOF</h3>
          <p>
            {report.proof.status}: {report.proof.reason}
          </p>
        </>
      )}
      <p>
        Stateless demonstration. No persisted industrial receipt. Advisory only; no regulatory
        certification. Unknown ≠ Safe. Production functionality is not enabled.
      </p>
    </section>
  );
}
