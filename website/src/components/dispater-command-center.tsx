import * as React from "react";
import {
  DollarSign,
  FileCheck2,
  AlertTriangle,
  Scale,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Clock,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";

export type CommandModule =
  | "overview"
  | "revenue"
  | "audit"
  | "contracts"
  | "operations"
  | "evidence"
  | "actions"
  | "outcomes";

interface FindingItem {
  id: string;
  code: string;
  subject: string;
  exposure: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  now: string;
  changed: string;
  next: string;
  why: string;
  proof: string;
}

const SYNTHETIC_FINDINGS: FindingItem[] = [
  {
    id: "FND-UNBILLED_JOB-JOB-101",
    code: "UNBILLED_JOB",
    subject: "JOB-101 (State Police Dispatch)",
    exposure: "$125.00",
    severity: "HIGH",
    now: "Completed highway recovery tow has no matching invoice in general ledger.",
    changed: "Field ticket marked completed at 02:40 AM without automated billing trigger.",
    next: "Draft invoice for $125.00 against Municipal Agreement schedule.",
    why: "Unbilled tow dispatches cause unrecoverable cash leakage over 30 days.",
    proof: "Ticket SHA-256: 7f8a32b0... / GPS Geofence: I-95 Mile 44",
  },
  {
    id: "FND-UNBILLED_STORAGE_DAYS-INV-103",
    code: "UNBILLED_STORAGE_DAYS",
    subject: "INV-103 (Impound Yard Storage)",
    exposure: "$135.00",
    severity: "HIGH",
    now: "Impound lot storage for 3 days was omitted from customer billing receipt.",
    changed: "Gate release timestamp indicates 72 hours lot retention billed at $0.00.",
    next: "Issue supplemental invoice for 3 days storage at $45.00/day.",
    why: "Storage lot holding costs must be recovered from insurer or registered owner.",
    proof: "Gate Entry: 2026-05-10 08:00 / Exit: 2026-05-13 08:30",
  },
  {
    id: "FND-MOTOR_CLUB_SHORT_PAY-INV-105",
    code: "MOTOR_CLUB_SHORT_PAY",
    subject: "INV-105 (Motor Club Remittance)",
    exposure: "$45.00",
    severity: "HIGH",
    now: "Motor club short-paid contracted roadside dispatch by $45.00.",
    changed: "Portal remittance applied automated administrative mileage clawback.",
    next: "Submit CAD time-stamped en-route GPS logs to dispute portal deduction.",
    why: "Disputed roadside deductions are recoverable when supported by geo-telemetry.",
    proof: "Portal Deduction Code: 402-MIL / CAD Dispatch Log: DSP-8841",
  },
  {
    id: "FND-RATE_MISMATCH-INV-102",
    code: "RATE_MISMATCH",
    subject: "INV-102 (Commercial Fleet Tow)",
    exposure: "$25.00",
    severity: "MEDIUM",
    now: "Invoice billed at obsolete $100.00 rate vs active amendment rate of $125.00.",
    changed: "Contract amendment effective 2026-05-01 increased standard tow to $125.00.",
    next: "Reissue corrected invoice reflecting current active contract schedule.",
    why: "Billing at outdated rates directly leaks negotiated pricing gains.",
    proof: "Amendment SHA-256: 3c91a0f... / Rate Schedule Rev: 2.1",
  },
];

export function DispaterCommandCenter() {
  const [activeModule, setActiveModule] = React.useState<CommandModule>("overview");
  const [selectedFinding, setSelectedFinding] = React.useState<FindingItem>(SYNTHETIC_FINDINGS[0]);

  return (
    <div className="rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="flex flex-col gap-4 border-b border-border/80 pb-5 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex size-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-mono uppercase tracking-widest text-primary">
              DISPATER.AI · EXECUTIVE COMMAND CENTER
            </span>
          </div>
          <h2 className="mt-1 font-display text-2xl text-foreground">
            Commercial Operations & Revenue Assurance
          </h2>
          <p className="text-xs text-muted-foreground">
            U.S. Towing & Roadside Pilot Architecture · Synthetic Demonstration Model
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-md border border-border bg-background/50 px-2.5 py-1 text-xs font-mono text-muted-foreground">
            Production: <strong className="text-amber">HOLD</strong>
          </span>
          <span className="rounded-md border border-border bg-background/50 px-2.5 py-1 text-xs font-mono text-muted-foreground">
            Financial Authority: <strong className="text-muted-foreground">NONE</strong>
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mt-5 flex flex-wrap gap-2 border-b border-border/60 pb-3">
        {[
          { id: "overview", label: "Executive Overview" },
          { id: "revenue", label: "Revenue Recovery" },
          { id: "audit", label: "Audit Readiness" },
          { id: "contracts", label: "Contract Intelligence" },
          { id: "operations", label: "Operations" },
          { id: "evidence", label: "Evidence Explorer" },
          { id: "actions", label: "Corrective Actions" },
          { id: "outcomes", label: "Financial Outcomes" },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveModule(tab.id as CommandModule)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              activeModule === tab.id
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-background/40 text-muted-foreground hover:bg-background hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Module Content */}
      <div className="mt-6">
        {activeModule === "overview" && (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-primary/30 bg-primary/5 p-4">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="text-xs font-medium">Potential Underbilling</span>
                  <TrendingUp className="size-4 text-primary" />
                </div>
                <div className="mt-2 text-2xl font-bold font-mono text-primary">$330.00</div>
                <p className="mt-1 text-[11px] text-muted-foreground">4 actionable discrepancy cases</p>
              </div>

              <div className="rounded-xl border border-border bg-background/40 p-4">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="text-xs font-medium">Audit Readiness</span>
                  <ShieldCheck className="size-4 text-emerald" />
                </div>
                <div className="mt-2 text-2xl font-bold font-mono text-emerald">92.5 / 100</div>
                <p className="mt-1 text-[11px] text-muted-foreground">FMCSA 49 CFR Part 390-396</p>
              </div>

              <div className="rounded-xl border border-border bg-background/40 p-4">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="text-xs font-medium">Unresolved Exceptions</span>
                  <AlertTriangle className="size-4 text-amber" />
                </div>
                <div className="mt-2 text-2xl font-bold font-mono text-amber">2 Documents</div>
                <p className="mt-1 text-[11px] text-muted-foreground">1 renewal pending · 1 missing</p>
              </div>

              <div className="rounded-xl border border-border bg-background/40 p-4">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="text-xs font-medium">Confirmed Recovery</span>
                  <CheckCircle2 className="size-4 text-muted-foreground" />
                </div>
                <div className="mt-2 text-2xl font-bold font-mono text-muted-foreground">$0.00</div>
                <p className="mt-1 text-[11px] text-muted-foreground">Human verification required</p>
              </div>
            </div>

            {/* Evidence & XAELI Explanation Section */}
            <div className="grid gap-6 lg:grid-cols-12">
              <div className="space-y-3 lg:col-span-5">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Identified Leakage Findings
                </h3>
                <div className="space-y-2">
                  {SYNTHETIC_FINDINGS.map((f) => (
                    <button
                      key={f.id}
                      type="button"
                      onClick={() => setSelectedFinding(f)}
                      className={`w-full text-left rounded-xl border p-3 transition-all ${
                        selectedFinding.id === f.id
                          ? "border-primary bg-primary/10 shadow-sm"
                          : "border-border/80 bg-background/40 hover:bg-background/80"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-semibold text-primary">{f.code}</span>
                        <span className="font-mono text-xs font-bold text-foreground">{f.exposure}</span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground line-clamp-1">{f.subject}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-border bg-background/60 p-5 lg:col-span-7">
                <div className="flex items-center justify-between border-b border-border/60 pb-3">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-primary">XAELI 5-STEP AUDIT RATIONALE</span>
                    <h4 className="font-display text-lg text-foreground">{selectedFinding.subject}</h4>
                  </div>
                  <span className="rounded bg-primary/20 px-2 py-0.5 font-mono text-xs font-bold text-primary">
                    {selectedFinding.exposure}
                  </span>
                </div>

                <div className="mt-4 space-y-3 text-xs leading-relaxed">
                  <div>
                    <span className="font-bold text-foreground">NOW: </span>
                    <span className="text-muted-foreground">{selectedFinding.now}</span>
                  </div>
                  <div>
                    <span className="font-bold text-foreground">CHANGED: </span>
                    <span className="text-muted-foreground">{selectedFinding.changed}</span>
                  </div>
                  <div>
                    <span className="font-bold text-primary">NEXT (Action): </span>
                    <span className="text-foreground">{selectedFinding.next}</span>
                  </div>
                  <div>
                    <span className="font-bold text-gold">WHY: </span>
                    <span className="text-muted-foreground">{selectedFinding.why}</span>
                  </div>
                  <div className="rounded border border-border/80 bg-black/30 p-2 font-mono text-[11px] text-muted-foreground">
                    <span className="font-bold text-foreground">PROOF: </span>
                    {selectedFinding.proof}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeModule === "revenue" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Towing Revenue Leakage & Discrepancy Stream</h3>
            <p className="text-xs text-muted-foreground">
              Automated reconciliation matches dispatch call tickets against executed invoices, master pricing
              schedules, lot storage logs, and motor club remittances.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th className="py-2">Finding ID</th>
                    <th className="py-2">Scenario</th>
                    <th className="py-2">Target Subject</th>
                    <th className="py-2">Discrepancy USD</th>
                    <th className="py-2">Classification</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 font-mono">
                  {SYNTHETIC_FINDINGS.map((f) => (
                    <tr key={f.id}>
                      <td className="py-2 text-primary">{f.id.slice(0, 16)}...</td>
                      <td className="py-2 font-sans">{f.code}</td>
                      <td className="py-2 font-sans text-muted-foreground">{f.subject}</td>
                      <td className="py-2 font-bold text-foreground">{f.exposure}</td>
                      <td className="py-2 text-primary">POTENTIAL_UNDERBILLING</td>
                      <td className="py-2 text-amber">REVIEW_REQUIRED</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeModule === "audit" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">DOT/FMCSA Safety & Regulatory Inventory</h3>
            <p className="text-xs text-muted-foreground">
              Continuous monitoring of Driver Qualification Files (DQF), annual mechanical safety inspections,
              and mandatory commercial liability coverage under 49 CFR Parts 390-396.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-border p-3 bg-card/40">
                <div className="font-semibold text-xs text-foreground">49 CFR § 391.51 · Driver Qualification</div>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  Medical certificates and annual motor vehicle driving records. 1 driver renewal currently pending.
                </p>
              </div>
              <div className="rounded-lg border border-border p-3 bg-card/40">
                <div className="font-semibold text-xs text-foreground">49 CFR § 396.17 · Annual Vehicle Inspection</div>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  Commercial tow truck mechanical periodic inspections. 1 vehicle inspection renewal required.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeModule === "contracts" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Active Contract Pricing Schedules</h3>
            <p className="text-xs text-muted-foreground">
              Master Service Agreement (MSA) and municipal towing tariff versioning with effective date window enforcement.
            </p>
            <div className="rounded-lg border border-border p-4 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span>POLICE_MUNICIPAL_TOW_V2</span>
                <span className="text-primary">$125.00 / callout</span>
              </div>
              <div className="flex justify-between">
                <span>IMPOUND_LOT_STORAGE_DAILY</span>
                <span className="text-primary">$45.00 / 24 hrs</span>
              </div>
              <div className="flex justify-between">
                <span>AFTER_HOURS_SURCHARGE_NIGHT</span>
                <span className="text-primary">$75.00 / dispatch</span>
              </div>
            </div>
          </div>
        )}

        {activeModule === "operations" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Field Dispatch & Telemetry Matching</h3>
            <p className="text-xs text-muted-foreground">
              Real-time cross-referencing between CAD dispatch logs, automated GPS geo-fences, and driver work receipts.
            </p>
            <div className="p-4 rounded-lg bg-black/40 border border-border/80 font-mono text-xs text-muted-foreground">
              [CAD:DISPATCH-SYNC] 4 calls verified · 1 tow without matching invoice · Geofence accuracy 99.8%
            </div>
          </div>
        )}

        {activeModule === "evidence" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Cryptographic Evidence Explorer</h3>
            <p className="text-xs text-muted-foreground">
              Every invoice, rate card, and dispatch ticket is signed with deterministic SHA-256 digests.
            </p>
            <div className="space-y-2 font-mono text-xs">
              <div className="p-2 rounded border border-border/60 bg-card/30">
                <span className="text-primary">EVID-7f8a32b0...</span> · JOB-101 Dispatch Field Completion
              </div>
              <div className="p-2 rounded border border-border/60 bg-card/30">
                <span className="text-primary">EVID-3c91a0f5...</span> · Municipal Towing Contract Schedule Rev 2.1
              </div>
            </div>
          </div>
        )}

        {activeModule === "actions" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Assigned Corrective Actions</h3>
            <p className="text-xs text-muted-foreground">
              Human remediation assignments required to close billing gaps and compliance exceptions.
            </p>
            <ul className="space-y-2 text-xs">
              <li className="flex items-start gap-2">
                <Clock className="size-4 text-amber shrink-0 mt-0.5" />
                <span>Re-bill 3 days impound yard storage fee ($135.00) on INV-103 to insurer.</span>
              </li>
              <li className="flex items-start gap-2">
                <Clock className="size-4 text-amber shrink-0 mt-0.5" />
                <span>File motor club appeal with GPS geo-fence logs for $45.00 unauthorized deduction on INV-105.</span>
              </li>
            </ul>
          </div>
        )}

        {activeModule === "outcomes" && (
          <div className="rounded-xl border border-border bg-background/40 p-6 space-y-4">
            <h3 className="font-display text-lg">Financial Recovery Outcomes</h3>
            <p className="text-xs text-muted-foreground">
              Strict accounting separation: AI models may discover leakage, but cash recovery is recorded only
              upon human validation and bank deposit confirmation.
            </p>
            <div className="grid gap-3 sm:grid-cols-3 font-mono text-xs">
              <div className="p-3 rounded border border-border bg-card/30">
                <span className="text-muted-foreground">Identified Discrepancies</span>
                <div className="text-lg font-bold text-foreground mt-1">$330.00</div>
              </div>
              <div className="p-3 rounded border border-border bg-card/30">
                <span className="text-muted-foreground">Human Verified</span>
                <div className="text-lg font-bold text-primary mt-1">$0.00</div>
              </div>
              <div className="p-3 rounded border border-border bg-card/30">
                <span className="text-muted-foreground">Actually Recovered Cash</span>
                <div className="text-lg font-bold text-muted-foreground mt-1">$0.00</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
