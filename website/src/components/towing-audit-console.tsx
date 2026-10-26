import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ShieldCheck, AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";

export interface SyntheticRecord {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  sha256: string;
}

const DEFAULT_SYNTHETIC_RECORDS: SyntheticRecord[] = [
  {
    id: "demo-driver-01",
    type: "driver_qualification",
    description: "CDL Driver Qualification & Medical Certificate (Driver #842)",
    timestamp: "2026-10-23T08:00:00Z",
    sha256: "a".repeat(64),
  },
  {
    id: "demo-vehicle-01",
    type: "vehicle_inspection",
    description: "Class 8 Heavy Wrecker Annual Brake & Rigging Inspection (Unit #104)",
    timestamp: "2025-10-23T08:00:00Z",
    sha256: "b".repeat(64),
  },
  {
    id: "demo-maint-01",
    type: "maintenance",
    description: "Hydraulic Winch Pressure & Line Pull Test Log (Winch A)",
    timestamp: "2026-10-24T10:30:00Z",
    sha256: "c".repeat(64),
  },
  {
    id: "demo-maint-02",
    type: "maintenance",
    description: "Hydraulic Winch Maintenance Log Copy B (Conflicting Digest)",
    timestamp: "2026-10-24T11:00:00Z",
    sha256: "d".repeat(64),
  },
  {
    id: "demo-ticket-01",
    type: "service_ticket",
    description: "Heavy Recovery Field Ticket #9042 (Unverified Source Hash)",
    timestamp: "2026-10-24T14:15:00Z",
    sha256: "unknown",
  },
];

export function TowingAuditConsole() {
  const [selectedRecords, setSelectedRecords] = useState<string[]>(DEFAULT_SYNTHETIC_RECORDS.map((r) => r.id));
  const [auditState, setAuditState] = useState<"idle" | "submitting" | "auditing" | "completed" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [auditResult, setAuditResult] = useState<any | null>(null);
  const [reviewDecisions, setReviewDecisions] = useState<Record<string, "accepted" | "rejected" | "evidence_requested">>({});
  const [receiptInput, setReceiptInput] = useState<string>("");
  const [verifiedReceipt, setVerifiedReceipt] = useState<any | null>(null);
  const [receiptError, setReceiptError] = useState<string | null>(null);

  const toggleRecord = (id: string) => {
    setSelectedRecords((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
  };

  const handleRunAudit = async () => {
    if (selectedRecords.length === 0) {
      setErrorMessage("Missing evidence: Please select at least one synthetic record to audit.");
      setAuditState("error");
      return;
    }

    setAuditState("submitting");
    setErrorMessage(null);
    setAuditResult(null);

    try {
      await new Promise((r) => setTimeout(r, 600));
      setAuditState("auditing");
      await new Promise((r) => setTimeout(r, 600));

      const res = await fetch("/v1/industrial/audit/demo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer aurex_staging_synthetic_token_32chars_minimum",
        },
        body: JSON.stringify({ fixture: "towing_v1" }),
      });

      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          throw new Error("Authentication failure: Invalid service token or unauthorized tenant.");
        }
        throw new Error(`Audit execution failed with status ${res.status}`);
      }

      const data = await res.json();
      setAuditResult(data);
      setAuditState("completed");
    } catch (err: any) {
      setErrorMessage(err.message || "Network interruption or staging backend unavailable.");
      setAuditState("error");
    }
  };

  const handleHumanReview = (category: string, decision: "accepted" | "rejected" | "evidence_requested") => {
    setReviewDecisions((prev) => ({ ...prev, [category]: decision }));
  };

  const handleVerifyReceipt = () => {
    setReceiptError(null);
    setVerifiedReceipt(null);

    if (!receiptInput.trim()) {
      setReceiptError("Please enter a valid receipt or job ID.");
      return;
    }

    if (receiptInput.includes("invalid")) {
      setReceiptError("Audit receipt verification failed: Tampered evidence digest or unverified verifier.");
      return;
    }

    setVerifiedReceipt({
      receipt_id: receiptInput.trim(),
      job_id: `job-${receiptInput.trim().slice(0, 8)}`,
      tenant_id: "permian-towing-synthetic",
      timestamp: new Date().toISOString(),
      evidence_digest: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      verifier: "AUREX-OX-CUSTOS-V1",
      status: "VERIFIED",
    });
  };

  return (
    <div className="w-full space-y-8 rounded-xl border border-cyan/30 bg-slate-950 p-6 text-slate-100 shadow-2xl">
      <div className="flex flex-col space-y-2 border-b border-cyan/20 pb-4 md:flex-row md:items-center md:justify-between md:space-y-0">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="border-cyan text-cyan">
              STEP 1-2: SYNTHETIC TOWING AUDIT
            </Badge>
            <span className="text-xs text-slate-400">Tenant: Permian Recovery Services (Fictional)</span>
          </div>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-white">Commercial Towing Field Record Audit</h2>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            onClick={handleRunAudit}
            disabled={auditState === "submitting" || auditState === "auditing"}
            className="bg-cyan text-slate-950 hover:bg-cyan/80 font-semibold"
          >
            {auditState === "submitting" || auditState === "auditing" ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Auditing Backend...
              </>
            ) : (
              <>
                <ShieldCheck className="mr-2 h-4 w-4" />
                Initiate Authenticated Audit
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan">
          Step 3: Synthetic Towing Field Records
        </h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {DEFAULT_SYNTHETIC_RECORDS.map((record) => {
            const isSelected = selectedRecords.includes(record.id);
            return (
              <div
                key={record.id}
                onClick={() => toggleRecord(record.id)}
                className={`cursor-pointer rounded-lg border p-4 transition-all ${
                  isSelected
                    ? "border-cyan bg-cyan/10 shadow-md shadow-cyan/5"
                    : "border-slate-800 bg-slate-900/50 opacity-60 hover:opacity-100"
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="font-mono text-xs text-cyan">{record.id}</span>
                  <Badge className={isSelected ? "bg-cyan text-slate-950" : "bg-slate-800 text-slate-400"}>
                    {record.type}
                  </Badge>
                </div>
                <p className="mt-2 text-sm font-medium text-slate-200">{record.description}</p>
                <p className="mt-2 font-mono text-[10px] text-slate-500 truncate">SHA256: {record.sha256}</p>
              </div>
            );
          })}
        </div>
      </div>

      {auditState !== "idle" && (
        <div className="space-y-4 rounded-lg border border-slate-800 bg-slate-900/80 p-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-cyan uppercase tracking-wider">
              Step 4-5: Backend Execution Status
            </span>
            <Badge
              className={
                auditState === "completed"
                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                  : auditState === "error"
                  ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
                  : "bg-amber/20 text-amber border-amber/40"
              }
            >
              STATE: {auditState.toUpperCase()}
            </Badge>
          </div>

          {errorMessage && (
            <Alert variant="destructive" className="border-rose-500/50 bg-rose-950/30 text-rose-200">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Audit Execution Halt</AlertTitle>
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {auditResult && (
            <div className="space-y-6">
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-gold">Step 6-7: XAELI Evidence Findings (5-Step Analysis)</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-2">
                    <span className="font-bold text-cyan text-xs uppercase">1. NOW (Present Inventory)</span>
                    <Table>
                      <TableHeader>
                        <TableRow className="border-slate-800">
                          <TableHead className="text-slate-400 text-xs">Category</TableHead>
                          <TableHead className="text-slate-400 text-xs">Status</TableHead>
                          <TableHead className="text-slate-400 text-xs">Records</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {auditResult.now.map((f: any) => (
                          <TableRow key={f.category} className="border-slate-800/50">
                            <TableCell className="font-mono text-xs text-slate-300">{f.category}</TableCell>
                            <TableCell>
                              <Badge
                                variant="outline"
                                className={
                                  f.status === "PRESENT_NOT_VERIFIED"
                                    ? "border-emerald-500 text-emerald-400"
                                    : f.status === "EXPIRED"
                                    ? "border-rose-500 text-rose-400"
                                    : f.status === "CONFLICTING"
                                    ? "border-amber text-amber"
                                    : "border-slate-600 text-slate-400"
                                }
                              >
                                {f.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-[10px] text-slate-400">
                              {f.record_ids.join(", ") || "none"}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>

                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
                    <span className="font-bold text-cyan text-xs uppercase">2. CHANGED & 3. NEXT</span>
                    <p className="text-xs text-slate-400 font-mono">CHANGED: {auditResult.changed}</p>
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-slate-300">Required Next Actions:</span>
                      {auditResult.next.map((n: any) => (
                        <div key={n.category} className="flex justify-between items-center text-xs bg-slate-950 p-2 rounded border border-slate-800">
                          <span className="font-mono text-slate-300">{n.category}</span>
                          <Badge variant="outline" className="border-amber/50 text-amber">
                            {n.action}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-1">
                    <span className="font-bold text-cyan text-xs uppercase">4. WHY (Reasoning Scope)</span>
                    <p className="text-sm text-slate-300">{auditResult.why}</p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-1">
                    <span className="font-bold text-cyan text-xs uppercase">5. PROOF (Evidence Integrity)</span>
                    <p className="text-xs text-amber font-mono">Status: {auditResult.proof.status}</p>
                    <p className="text-xs text-slate-400">{auditResult.proof.reason}</p>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-gold/30 bg-gold/5 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-gold uppercase">Step 8: Human Review & Overrides</h4>
                  <span className="text-xs text-slate-400">Authority: Human Reviewer Required</span>
                </div>
                <div className="space-y-2">
                  {auditResult.now.map((f: any) => {
                    const decision = reviewDecisions[f.category];
                    return (
                      <div
                        key={f.category}
                        className="flex flex-col sm:flex-row sm:items-center justify-between bg-slate-900 p-3 rounded border border-slate-800 gap-2"
                      >
                        <div className="space-y-0.5">
                          <span className="font-mono text-xs font-semibold text-white">{f.category}</span>
                          <p className="text-[11px] text-slate-400">Status: {f.status}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant={decision === "accepted" ? "default" : "outline"}
                            onClick={() => handleHumanReview(f.category, "accepted")}
                            className={decision === "accepted" ? "bg-emerald-600 text-white" : "border-slate-700 text-slate-300"}
                          >
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant={decision === "rejected" ? "default" : "outline"}
                            onClick={() => handleHumanReview(f.category, "rejected")}
                            className={decision === "rejected" ? "bg-rose-600 text-white" : "border-slate-700 text-slate-300"}
                          >
                            Reject
                          </Button>
                          <Button
                            size="sm"
                            variant={decision === "evidence_requested" ? "default" : "outline"}
                            onClick={() => handleHumanReview(f.category, "evidence_requested")}
                            className={decision === "evidence_requested" ? "bg-amber text-slate-950" : "border-slate-700 text-slate-300"}
                          >
                            Request Evidence
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-2">
                <h4 className="text-sm font-bold text-cyan uppercase">Step 9: Generated Audit Summary</h4>
                <div className="font-mono text-xs text-slate-300 bg-slate-950 p-3 rounded space-y-1">
                  <p>AUDIT_ID: rcpt-towing-{Date.now().toString(36)}</p>
                  <p>OPERATOR: {auditResult.operator}</p>
                  <p>AUTHORITY: {auditResult.authority}</p>
                  <p>HUMAN_REVIEWS_LOGGED: {Object.keys(reviewDecisions).length} / {auditResult.now.length}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 space-y-4">
        <div>
          <span className="text-xs font-semibold text-cyan uppercase tracking-wider">
            Step 10: Cryptographic Audit Receipt Verification
          </span>
          <h3 className="text-lg font-bold text-white mt-1">Verify Evidence Ledger Receipt</h3>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Enter receipt ID (e.g. rcpt-towing-20261025)"
            value={receiptInput}
            onChange={(e) => setReceiptInput(e.target.value)}
            className="flex-1 rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-mono text-white placeholder:text-slate-600 focus:border-cyan focus:outline-none"
          />
          <Button onClick={handleVerifyReceipt} className="bg-cyan/20 border border-cyan/40 text-cyan hover:bg-cyan/30">
            Verify Receipt
          </Button>
        </div>

        {receiptError && (
          <p className="text-xs text-rose-400 font-mono bg-rose-950/40 p-2 rounded border border-rose-800/40">
            {receiptError}
          </p>
        )}

        {verifiedReceipt && (
          <div className="rounded border border-emerald-500/40 bg-emerald-950/20 p-3 font-mono text-xs text-emerald-300 space-y-1">
            <div className="flex items-center justify-between text-emerald-400 font-bold border-b border-emerald-500/30 pb-1">
              <span>RECEIPT STATUS: {verifiedReceipt.status}</span>
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <p>Receipt ID: {verifiedReceipt.receipt_id}</p>
            <p>Tenant ID: {verifiedReceipt.tenant_id}</p>
            <p>Verifier: {verifiedReceipt.verifier}</p>
            <p className="truncate">Evidence SHA256: {verifiedReceipt.evidence_digest}</p>
          </div>
        )}
      </div>
    </div>
  );
}
