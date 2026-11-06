import { useState } from "react";
import { runDispaterAudit } from "@/lib/dispater.functions";
import type { DispaterReconciliationReport } from "@/lib/dispater-contract";
import { Button } from "@/components/ui/button";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

export function DispaterReconciliationConsole() {
  const [busy, setBusy] = useState(false);
  const [selectedFixture, setSelectedFixture] = useState<
    "towing_recovery_v1" | "oilfield_demo_v1" | "clean_control_v1"
  >("towing_recovery_v1");
  const [report, setReport] = useState<DispaterReconciliationReport | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleRunDemo() {
    setBusy(true);
    setErrorMsg(null);
    try {
      const res = await runDispaterAudit({ data: { fixture: selectedFixture } });
      setReport(res);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Reconciliation failed");
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
    a.download = `dispater-recovery-report-${report.tenant_id}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div
      className="rounded-xl border border-primary/30 bg-card p-6 shadow-xl"
      aria-labelledby="console-heading"
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-primary">
            DISPATER REVENUE RECOVERY & AUDIT COMMAND CENTER
          </span>
          <h3 id="console-heading" className="text-2xl font-display text-foreground mt-1">
            Deterministic Reconciliation Console
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="bg-background border border-border text-foreground text-sm rounded-lg px-3 py-2"
            value={selectedFixture}
            onChange={(e) =>
              setSelectedFixture(
                e.target.value as "towing_recovery_v1" | "oilfield_demo_v1" | "clean_control_v1"
              )
            }
            disabled={busy}
            aria-label="Select test fixture"
          >
            <option value="towing_recovery_v1">
              Synthetic Towing & Recovery (Unbilled Storage & Surcharges)
            </option>
            <option value="oilfield_demo_v1">
              Synthetic Oilfield Discrepancy (Deliberate Leakage)
            </option>
            <option value="clean_control_v1">Clean Control Dataset (Zero False Positives)</option>
          </select>
          <Button
            type="button"
            variant="hero"
            disabled={busy}
            onClick={() => void handleRunDemo()}
            className="flex items-center gap-2"
          >
            {busy ? (
              <>
                <RefreshCw className="size-4 animate-spin" /> Running Audit…
              </>
            ) : (
              <>
                Execute Reconciliation <ArrowRight className="size-4" />
              </>
            )}
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="mt-4 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive flex items-center gap-3">
          <ShieldAlert className="size-5 shrink-0" />
          <div>
            <p className="font-semibold text-sm">Audit Error</p>
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Potential Underbilling</span>
              <p className="text-2xl font-display text-gold mt-1">
                ${report.financial_summary.potential_underbilling_usd || report.financial_summary.identified_exposure_usd}
              </p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Missed Revenue Candidate
              </span>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Confirmed Recovery</span>
              <p className="text-2xl font-display text-emerald mt-1">
                ${report.financial_summary.confirmed_recovery_usd}
              </p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Settled cash collections
              </span>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <span className="text-xs text-muted-foreground uppercase">Audit Findings</span>
              <p className="text-2xl font-display text-primary mt-1">{report.findings.length}</p>
              <span className="text-[10px] text-muted-foreground block mt-1">
                Human Review Enforced
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
              <span className="text-[10px] text-emerald block mt-1">Cryptographically Sealed</span>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-foreground mb-3">
              Grounded Audit Findings ({report.findings.length})
            </h4>
            {report.findings.length === 0 ? (
              <div className="rounded-lg border border-emerald/30 bg-emerald/5 p-4 text-emerald flex items-center gap-3">
                <CheckCircle2 className="size-5 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">Control Dataset Clean</p>
                  <p className="text-xs">
                    No billing anomalies or unbilled dispatches detected. Zero false positives.
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
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
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
                        <span className="font-semibold text-sm text-foreground">
                          Subject: {f.subject}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-gold">
                        Exposure: ${f.exposure_usd}
                      </span>
                    </div>

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
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="glass"
                size="sm"
                onClick={handleExportJson}
                className="flex items-center gap-2"
              >
                <Download className="size-4" /> Export Report (JSON)
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleExportJson}
                className="flex items-center gap-2"
              >
                <FileSpreadsheet className="size-4" /> Download Audit Binder
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
