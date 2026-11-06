import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  admitSyntheticDispaterCsv,
  readDispaterStoredRun,
  runDispaterDemoReconciliation,
} from "@/lib/dispater.functions";
import type { DispaterReconciliationReport } from "@/lib/dispater-contract";
import { dispaterLinkState, documentSourceLine, storedRunAgrees } from "@/lib/dispater-link";
import { Button } from "@/components/ui/button";
import {
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Download,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

export function DispaterReconciliationConsole() {
  const reconcileFn = useServerFn(runDispaterDemoReconciliation);
  const admitFn = useServerFn(admitSyntheticDispaterCsv);
  const readFn = useServerFn(readDispaterStoredRun);
  const [presentation, setPresentation] = useState<"SYNTHETIC DEMO" | "SYNTHETIC DOCUMENT">(
    "SYNTHETIC DEMO",
  );
  const [busy, setBusy] = useState(false);
  const [selectedFixture, setSelectedFixture] = useState<"oilfield_demo_v1" | "clean_control_v1">(
    "oilfield_demo_v1",
  );
  const [report, setReport] = useState<DispaterReconciliationReport | null>(null);
  const [sourceLine, setSourceLine] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [storedMatch, setStoredMatch] = useState<"MATCH" | "UNCHECKED" | null>(null);

  async function confirmStored(res: DispaterReconciliationReport) {
    if (!res.run_id) {
      setStoredMatch("UNCHECKED");
      return;
    }
    const stored = await readFn({ data: { runId: res.run_id } });
    if (!storedRunAgrees(res, stored)) throw new Error("DISPATER API returned an invalid report");
    setStoredMatch("MATCH");
  }

  async function handleRunDemo() {
    setBusy(true);
    setErrorMsg(null);
    setStoredMatch(null);
    try {
      const res = await reconcileFn({ data: { fixture: selectedFixture } });
      setPresentation("SYNTHETIC DEMO");
      setSourceLine(null);
      await confirmStored(res);
      setReport(res);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Reconciliation failed");
      setReport(null);
    } finally {
      setBusy(false);
    }
  }

  async function handleAdmitCsv() {
    setBusy(true);
    setErrorMsg(null);
    try {
      const admitted = await admitFn({ data: {} });
      setPresentation("SYNTHETIC DOCUMENT");
      setSourceLine(documentSourceLine(admitted.source));
      await confirmStored(admitted.report);
      setReport(admitted.report);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Document admission failed");
      setReport(null);
    } finally {
      setBusy(false);
    }
  }

  function handleExportJson() {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dispater-audit-report-${report.tenant_id}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div
      className="rounded-xl border border-primary/30 bg-card p-6 shadow-xl"
      aria-labelledby="console-heading"
    >
      <p className="mb-4 text-xs uppercase tracking-wider text-muted-foreground">
        Synthetic demonstration. These dollars are not customer savings or recovered revenue.
      </p>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-primary">
            DISPATER REVENUE RECONCILIATION CONSOLE · {presentation}
          </span>
          <h3 id="console-heading" className="text-2xl font-display text-foreground mt-1">
            Automated Audit Workflow
          </h3>
        </div>
        <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center">
          <select
            className="w-full bg-background border border-border text-foreground text-sm rounded-lg px-3 py-2 sm:w-auto"
            value={selectedFixture}
            onChange={(e) =>
              setSelectedFixture(e.target.value as "oilfield_demo_v1" | "clean_control_v1")
            }
            disabled={busy}
            aria-label="Select test fixture"
          >
            <option value="oilfield_demo_v1">
              Synthetic Oilfield Discrepancy (Planted differences)
            </option>
            <option value="clean_control_v1">Clean Control Dataset (No findings in this sample)</option>
          </select>
          <Button
            type="button"
            variant="hero"
            disabled={busy}
            onClick={() => void handleRunDemo()}
            className="flex w-full items-center justify-center gap-2 sm:w-auto"
          >
            {busy ? (
              <>
                <RefreshCw className="size-4 motion-reduce:animate-none animate-spin" /> Running Audit…
              </>
            ) : (
              <>
                Run Synthetic Audit <ArrowRight className="size-4" />
              </>
            )}
          </Button>
          <Button type="button" variant="glass" disabled={busy} onClick={() => void handleAdmitCsv()} className="w-full sm:w-auto">
            Admit synthetic CSV
          </Button>
        </div>
      </div>

      <p className="mt-4 text-xs uppercase tracking-wider text-muted-foreground" role="status">
        API link: {dispaterLinkState(busy, report, errorMsg)} · synthetic demonstration · not recovered revenue
      </p>

      {errorMsg && (
        <div className="mt-4 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive flex items-center gap-3">
          <ShieldAlert className="size-5 shrink-0" />
          <div>
            <p className="font-semibold text-sm">{dispaterLinkState(busy, report, errorMsg)}</p>
            <p className="text-xs">{errorMsg}</p>
          </div>
        </div>
      )}

      {!report && !errorMsg && !busy && (
        <div className="py-12 text-center text-muted-foreground">
          <AlertTriangle className="size-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">
            No audit running. Select a dataset and execute the demonstration above.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Status: DISCONNECTED / IDLE · Production Authority: HOLD
          </p>
        </div>
      )}

      {report && (
        <div className="mt-6 space-y-6">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">
            {presentation} · {report.receipt_binding ?? "RECEIPT UNBOUND"}
            {sourceLine ? ` · source ${sourceLine}` : ""} · confirmed recovery stays
            ${report.financial_summary.confirmed_recovery_usd} · withheld $
            {report.financial_summary.withheld_unresolved_usd ?? "0.00"} · XAELI cannot approve recovery
            · you decide the next action · no vendor is contacted
          </p>
          {/* Exposure and Stats Header */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Identified Exposure</span>
              <p className="text-2xl font-display text-gold mt-1">
                ${report.financial_summary.identified_exposure_usd}
              </p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Human Review Candidate
                {report.financial_summary.event_separation
                  ? ` · ${report.financial_summary.event_separation}`
                  : ""}
              </span>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Confirmed Recovery</span>
              <p className="text-2xl font-display text-emerald mt-1">
                ${report.financial_summary.confirmed_recovery_usd}
              </p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Requires human settlement
              </span>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Audit Findings</span>
              <p className="text-2xl font-display text-primary mt-1">{report.counts.findings}</p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Jobs: {report.counts.jobs} · Invoices: {report.counts.invoices}
              </span>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Evidence Receipt</span>
              <p
                className="text-xs font-mono text-muted-foreground mt-2 truncate"
                title={report.receipt_sha256}
              >
                SHA-256: {report.receipt_sha256.slice(0, 16)}…
              </p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                {report.receipt_binding === "BOUND_V2"
                  ? "Identity-bound receipt"
                  : "Legacy or unbound metadata"}
                {storedMatch === "MATCH" ? " · Stored run matches" : ""}
                {storedMatch === "UNCHECKED" ? " · Stored run was not read back" : ""}
                {report.financial_summary.withheld_unresolved_usd
                  ? ` · Withheld ${report.financial_summary.withheld_unresolved_usd}`
                  : ""}
              </span>
            </div>
          </div>

          {/* Finding Cards */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-foreground mb-3">
              Grounded Audit Findings ({report.findings.length})
            </h4>
            <p className="text-xs text-muted-foreground -mt-2 mb-3">
              XAELI can explain a finding. It cannot approve a recovery or replace the calculation.
              The proof line is the trace back to the source digest, page, or row. OCR is not claimed
              on this screen.
            </p>
            {report.findings.length === 0 ? (
              <div className="rounded-lg border border-emerald/30 bg-emerald/5 p-4 text-emerald flex items-center gap-3">
                <CheckCircle2 className="size-5 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">Control Dataset Clean</p>
                  <p className="text-xs">
                    This sample produced no findings. That is not proof of zero false positives.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {report.findings.map((f) => (
                  <div
                    key={f.finding_id}
                    className="rounded-lg border border-border bg-background/80 p-5 space-y-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            f.severity === "CRITICAL"
                              ? "bg-red/20 text-red"
                              : f.severity === "HIGH"
                                ? "bg-amber/20 text-amber"
                                : "bg-primary/20 text-primary"
                          }`}
                        >
                          {f.severity}
                        </span>
                        <span className="font-mono text-xs text-muted-foreground">{f.code}</span>
                        {f.qualification ? (
                          <span className="text-[10px] uppercase text-muted-foreground">
                            {f.qualification}
                          </span>
                        ) : null}
                        <span className="font-semibold text-sm text-foreground">
                          Subject: {f.subject}
                        </span>
                        {f.event_relation ? (
                          <span className="text-[10px] uppercase text-amber">
                            {f.event_relation}
                          </span>
                        ) : null}
                      </div>
                      <span className="text-sm font-bold text-gold">
                        Exposure: ${f.exposure_usd}
                      </span>
                    </div>

                    {/* 5-Step XAELI Section */}
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2 text-xs border-t border-border/50">
                      <div>
                        <span className="font-semibold text-primary block">NOW</span>
                        <p className="text-muted-foreground mt-0.5">{f.xaeli_explanation.now}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-amber block">CHANGED</span>
                        <p className="text-muted-foreground mt-0.5">
                          {f.xaeli_explanation.changed}
                        </p>
                      </div>
                      <div>
                        <span className="font-semibold text-emerald block">NEXT</span>
                        <p className="text-muted-foreground mt-0.5">{f.xaeli_explanation.next}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-gold block">WHY</span>
                        <p className="text-muted-foreground mt-0.5">{f.xaeli_explanation.why}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-primary block">PROOF</span>
                        <p
                          className="text-muted-foreground font-mono text-[10px] mt-0.5 truncate"
                          title={f.xaeli_explanation.proof}
                        >
                          {f.xaeli_explanation.proof}
                        </p>
                      </div>
                    </div>
                    {f.evidence.length > 0 ? (
                      <p className="font-mono text-[10px] text-muted-foreground">
                        Sources:{" "}
                        {f.evidence
                          .map((item) => `${item.kind} ${item.record_sha256.slice(0, 12)}`)
                          .join(" · ")}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center justify-between border-t border-border pt-4">
            <span className="text-xs text-muted-foreground">
              Production Release: <strong className="text-amber">HOLD</strong> · Financial
              Authority: <strong className="text-red">NONE</strong>
            </span>
            <Button
              type="button"
              variant="glass"
              size="sm"
              onClick={handleExportJson}
              className="flex items-center gap-2"
            >
              <Download className="size-4" /> Export Audit Report (JSON)
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
