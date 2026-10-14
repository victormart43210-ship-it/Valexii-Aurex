import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DEFAULT_INTENSITY,
  INTENSITIES,
  LAB_AREAS,
  WORKER_CONTRACT,
  labApprovalGate,
  scopeErrors,
  type Intensity,
} from "@/lib/aurex-security-lab";

type LabData = { targets: unknown[]; history: unknown[]; workerConfigured: boolean };

/** Owner-only. Rendered only after server-side owner verification. Executes nothing. */
export function AurexSecurityLab({ data }: { data?: LabData | undefined }) {
  const [host, setHost] = useState("");
  const [intensity, setIntensity] = useState<Intensity>(DEFAULT_INTENSITY);
  const [expiryDays, setExpiry] = useState(1);
  const [ownershipConfirmed, setOwn] = useState(false);
  const [consent, setConsent] = useState(false);
  const [stagingPreferred, setStaging] = useState(true);
  const errors = scopeErrors({
    host,
    intensity,
    expiryDays,
    ownershipConfirmed,
    consent,
    stagingPreferred,
  });
  const gate = labApprovalGate({
    scopeValid: errors.length === 0,
    ownershipVerified: false,
    workerConfigured: data?.workerConfigured ?? false,
  });
  return (
    <section className="site-grid section-space" aria-labelledby="lab-h" data-testid="security-lab">
      <h2 id="lab-h" className="font-display text-2xl">
        Security Lab <span className="text-sm text-amber">PRIVATE · NOT CONFIGURED</span>
      </h2>
      <p className="mt-2 text-sm text-muted-foreground">
        No test service exists. Nothing on this page scans, probes or contacts any host.
      </p>
      <nav aria-label="Security Lab areas" className="mt-4 flex gap-2 overflow-x-auto pb-2">
        {LAB_AREAS.map((a) => (
          <a
            key={a.id}
            href={`#lab-${a.id}`}
            className="shrink-0 rounded-full border border-border px-3 py-2 text-xs min-h-11 inline-flex items-center"
          >
            {a.name}
          </a>
        ))}
      </nav>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {LAB_AREAS.map((a) => (
          <article
            key={a.id}
            id={`lab-${a.id}`}
            className="rounded-lg border border-border bg-card p-4"
          >
            <h3 className="font-display text-lg">{a.name}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{a.summary}</p>
            <p className="mt-3 text-xs font-semibold text-amber">
              NOT CONFIGURED — awaiting a real, authorized test service
            </p>
          </article>
        ))}
      </div>

      <h3 className="mt-10 font-display text-xl">Authorized targets (read-only)</h3>
      {data?.targets.length ? null : (
        <p
          className="mt-2 rounded-lg border border-dashed border-border p-4 text-sm text-muted-foreground"
          data-testid="lab-targets-empty"
        >
          No authorized targets. A target can be added only after server-verified ownership (DNS TXT
          or file token).
        </p>
      )}

      <h3 className="mt-10 font-display text-xl">Propose scope (draft only — not submitted)</h3>
      <form className="mt-3 grid gap-3 sm:max-w-xl" onSubmit={(e) => e.preventDefault()}>
        <label className="grid gap-1 text-sm">
          Target hostname
          <input
            className="min-h-11 rounded-md border border-border bg-background px-3"
            value={host}
            maxLength={253}
            onChange={(e) => setHost(e.target.value)}
            placeholder="staging.example.com"
            autoComplete="off"
          />
        </label>
        <label className="grid gap-1 text-sm">
          Proposed intensity
          <select
            className="min-h-11 rounded-md border border-border bg-background px-3"
            value={intensity}
            onChange={(e) => setIntensity(e.target.value as Intensity)}
          >
            {INTENSITIES.map((i) => (
              <option key={i} value={i}>
                {i}
                {i === "passive" ? " (default)" : ""}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm">
          Authorization expiry (days, max 7)
          <input
            type="number"
            min={1}
            max={7}
            className="min-h-11 rounded-md border border-border bg-background px-3"
            value={expiryDays}
            onChange={(e) => setExpiry(Number(e.target.value))}
          />
        </label>
        <label className="flex items-center gap-2 text-sm min-h-11">
          <input
            type="checkbox"
            checked={stagingPreferred}
            onChange={(e) => setStaging(e.target.checked)}
          />{" "}
          Prefer staging environment
        </label>
        <label className="flex items-center gap-2 text-sm min-h-11">
          <input
            type="checkbox"
            checked={ownershipConfirmed}
            onChange={(e) => setOwn(e.target.checked)}
          />{" "}
          I own this target and will complete ownership verification
        </label>
        <label className="flex items-center gap-2 text-sm min-h-11">
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />{" "}
          I hold written authorization for this scope
        </label>
        {errors.length > 0 && (
          <ul className="text-xs text-amber list-disc pl-5" aria-live="polite">
            {errors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        )}
        <Button type="button" className="min-h-11" disabled aria-describedby="lab-gate">
          Approve & run — disabled
        </Button>
        <p id="lab-gate" className="text-xs text-amber">
          Approval gate: {gate.reason}
        </p>
      </form>

      <h3 className="mt-10 font-display text-xl">Status, history & reports</h3>
      <p
        className="mt-2 rounded-lg border border-dashed border-border p-4 text-sm text-muted-foreground"
        data-testid="lab-history-empty"
      >
        No tests have run. No findings or reports exist. Reports will appear only after independent
        evidence verification.
      </p>

      <details className="mt-10 rounded-lg border border-border p-4">
        <summary className="cursor-pointer font-display text-lg min-h-11">
          Future worker capability contract
        </summary>
        <dl className="mt-3 grid gap-2 text-sm">
          {Object.entries(WORKER_CONTRACT).map(([k, v]) => (
            <div key={k}>
              <dt className="text-muted-foreground">{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      </details>
    </section>
  );
}
