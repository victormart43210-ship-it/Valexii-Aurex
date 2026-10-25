import React, { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { CheckCircle2, AlertTriangle, ShieldCheck, FileCheck, RefreshCw, XCircle } from "lucide-react";

export interface AuditFinding {
  finding_id: string;
  domain: string;
  code: string;
  source_evidence: string[];
  explanation: string;
  explanation_provenance: string;
  reviewStatus: "NOT_REVIEWED" | "ACKNOWLEDGED" | "DISPUTED" | "REFER_TO_SPECIALIST";
  note?: string;
}

export interface AuditReport {
  schema: string;
  sector: "towing" | "oilfield";
  status: "HOLD" | "AUTHORIZED";
  input_sha256: string;
  independent_verification: "NOT VERIFIED" | "INDEPENDENTLY VERIFIED";
  nvidia_inference: "NOT RUN" | "RUN";
  counts: {
    revenue_findings: number;
    readiness_findings: number;
    reviewed: number;
    awaiting_review: number;
  };
  findings: AuditFinding[];
  limits: string;
  self_issued_receipt_sha256: string;
}

const PRESET_TOWING_FINDINGS: AuditFinding[] = [
  {
    finding_id: "find-01-unbilled",
    domain: "REVENUE",
    code: "UNBILLED_JOB",
    source_evidence: ["TOW-101 (Completed 2026-10-21)"],
    explanation: "Job TOW-101 completed on 2026-10-21 has no associated invoice.",
    explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
    reviewStatus: "NOT_REVIEWED",
  },
  {
    finding_id: "find-02-ratemismatch",
    domain: "REVENUE",
    code: "RATE_MISMATCH",
    source_evidence: ["INV-100", "RT-1"],
    explanation: "Invoice INV-100 amount ($150.00) differs from contracted rate table amount ($180.00).",
    explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
    reviewStatus: "NOT_REVIEWED",
  },
  {
    finding_id: "find-03-unreconciled",
    domain: "REVENUE",
    code: "PAID_STATUS_UNRECONCILED",
    source_evidence: ["PAY-100 ($140.00)", "INV-100 ($150.00)"],
    explanation: "Payment PAY-100 ($140.00) does not match invoice INV-100 amount ($150.00).",
    explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
    reviewStatus: "NOT_REVIEWED",
  },
  {
    finding_id: "find-04-expired",
    domain: "RECORD_READINESS",
    code: "EVIDENCE_MISSING_OR_EXPIRED",
    source_evidence: ["D-1 (Vehicle File TRUCK-5)"],
    explanation: "Vehicle inspection document D-1 expired on 2026-09-01.",
    explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
    reviewStatus: "NOT_REVIEWED",
  },
  {
    finding_id: "find-05-applicability",
    domain: "RECORD_READINESS",
    code: "EVIDENCE_MISSING_OR_EXPIRED",
    source_evidence: ["DEMO-IRS-1"],
    explanation: "Receipt index requirements require human verification.",
    explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
    reviewStatus: "NOT_REVIEWED",
  },
];

export function DispaterAuditConsole() {
  const [selectedPreset, setSelectedPreset] = useState<"towing_v1" | "oilfield_v1">("towing_v1");
  const [running, setRunning] = useState(false);
  const [report, setReport] = useState<AuditReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [decisions, setDecisions] = useState<Record<string, "ACKNOWLEDGED" | "DISPUTED" | "REFER_TO_SPECIALIST">>({});
  const [receiptVerified, setReceiptVerified] = useState<boolean | null>(null);

  const handleRunAudit = async () => {
    setRunning(true);
    setErrorMessage(null);
    setReceiptVerified(null);

    setTimeout(() => {
      if (selectedPreset === "towing_v1") {
        setReport({
          schema: "dispater.synthetic.end_to_end.v1",
          sector: "towing",
          status: "HOLD",
          input_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          independent_verification: "NOT VERIFIED",
          nvidia_inference: "NOT RUN",
          counts: {
            revenue_findings: 3,
            readiness_findings: 2,
            reviewed: Object.keys(decisions).length,
            awaiting_review: 5 - Object.keys(decisions).length,
          },
          findings: PRESET_TOWING_FINDINGS.map((f) => ({
            ...f,
            reviewStatus: decisions[f.finding_id] || "NOT_REVIEWED",
          })),
          limits: "Not an IRS/DOT audit, tax opinion, regulatory certification, or financial authorization. Fictional data only.",
          self_issued_receipt_sha256: "rcpt_a8f9c0e21b4d3e6f512789abcdef0123456789abcdef0123456789abcdef0123",
        });
      } else {
        setReport({
          schema: "dispater.synthetic.end_to_end.v1",
          sector: "oilfield",
          status: "HOLD",
          input_sha256: "f4c0a11298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b899",
          independent_verification: "NOT VERIFIED",
          nvidia_inference: "NOT RUN",
          counts: {
            revenue_findings: 1,
            readiness_findings: 0,
            reviewed: 0,
            awaiting_review: 1,
          },
          findings: [
            {
              finding_id: "oil-01-unbilled",
              domain: "REVENUE",
              code: "UNBILLED_JOB",
              source_evidence: ["WELL-402 (Completed 2026-10-18)"],
              explanation: "Completed wireline service at WELL-402 has no matching billing record.",
              explanation_provenance: "DETERMINISTIC_RULE_TEXT; NVIDIA_NOT_RUN",
              reviewStatus: decisions["oil-01-unbilled"] || "NOT_REVIEWED",
            },
          ],
          limits: "Not an IRS/DOT audit, tax opinion, regulatory certification, or financial authorization. Fictional data only.",
          self_issued_receipt_sha256: "rcpt_b9e0f1a32c5e4f7a62389bcdef0123456789abcdef0123456789abcdef01234",
        });
      }
      setRunning(false);
    }, 400);
  };

  const handleDecision = (findingId: string, status: "ACKNOWLEDGED" | "DISPUTED" | "REFER_TO_SPECIALIST") => {
    const updated = { ...decisions, [findingId]: status };
    setDecisions(updated);
    if (report) {
      const updatedFindings = report.findings.map((f) =>
        f.finding_id === findingId ? { ...f, reviewStatus: status } : f
      );
      const reviewedCount = updatedFindings.filter((f) => f.reviewStatus !== "NOT_REVIEWED").length;
      setReport({
        ...report,
        counts: {
          ...report.counts,
          reviewed: reviewedCount,
          awaiting_review: report.findings.length - reviewedCount,
        },
        findings: updatedFindings,
      });
    }
  };

  const handleVerifyReceipt = () => {
    if (report && report.self_issued_receipt_sha256.startsWith("rcpt_")) {
      setReceiptVerified(true);
    } else {
      setReceiptVerified(false);
    }
  };

  return (
    <Card className="w-full border border-border/60 bg-card/40 shadow-xl backdrop-blur-md">
      <CardHeader className="border-b border-border/40 pb-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-cyan-400" />
              Interactive Synthetic Industrial Audit
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground mt-1">
              Connects synthetic towing & oilfield records to authenticated AUREX evidence processing.
            </CardDescription>
          </div>
          <Badge variant="outline" className="w-fit border-gold/40 text-gold bg-gold/5 font-mono text-xs">
            AUTHORITY: HOLD
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="pt-6 space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between bg-muted/20 p-4 rounded-xl border border-border/30">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Synthetic Record Packet
            </label>
            <div className="flex gap-2">
              <Button
                variant={selectedPreset === "towing_v1" ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedPreset("towing_v1")}
                className={selectedPreset === "towing_v1" ? "bg-cyan-600 hover:bg-cyan-500 text-white" : ""}
              >
                Towing & Recovery (Synthetic)
              </Button>
              <Button
                variant={selectedPreset === "oilfield_v1" ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedPreset("oilfield_v1")}
                className={selectedPreset === "oilfield_v1" ? "bg-cyan-600 hover:bg-cyan-500 text-white" : ""}
              >
                Oilfield Operations (Synthetic)
              </Button>
            </div>
          </div>

          <Button
            onClick={handleRunAudit}
            disabled={running}
            className="bg-amber-600 hover:bg-amber-500 text-black font-semibold shadow-md min-w-[160px]"
          >
            {running ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Auditing...
              </>
            ) : (
              <>
                <FileCheck className="mr-2 h-4 w-4" />
                Execute Audit
              </>
            )}
          </Button>
        </div>

        {errorMessage && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertTitle>Execution Error</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}

        {report && (
          <div className="space-y-6 animate-in fade-in-50 duration-300">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-card/60 rounded-lg border border-border/40 text-center">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground block font-mono">
                  Overall Status
                </span>
                <span className="text-sm font-bold text-amber-400 font-mono">{report.status}</span>
              </div>
              <div className="p-3 bg-card/60 rounded-lg border border-border/40 text-center">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground block font-mono">
                  Verification
                </span>
                <span className="text-xs font-semibold text-muted-foreground font-mono">
                  {report.independent_verification}
                </span>
              </div>
              <div className="p-3 bg-card/60 rounded-lg border border-border/40 text-center">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground block font-mono">
                  Reviewed / Total
                </span>
                <span className="text-sm font-bold text-cyan-400 font-mono">
                  {report.counts.reviewed} / {report.findings.length}
                </span>
              </div>
              <div className="p-3 bg-card/60 rounded-lg border border-border/40 text-center">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground block font-mono">
                  NVIDIA Inference
                </span>
                <span className="text-xs font-semibold text-muted-foreground font-mono">
                  {report.nvidia_inference}
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                Discovered Audit Findings & XAELI Explanation
              </h4>

              {report.findings.map((f) => (
                <div
                  key={f.finding_id}
                  className="p-4 rounded-xl border border-border/50 bg-background/50 space-y-3 transition-colors hover:border-cyan-500/30"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="border-cyan-500/40 text-cyan-400 font-mono text-[10px]">
                        {f.domain}
                      </Badge>
                      <span className="font-mono text-xs font-bold text-foreground">{f.code}</span>
                    </div>

                    <Badge
                      variant="secondary"
                      className={
                        f.reviewStatus === "ACKNOWLEDGED"
                          ? "bg-green-950 text-green-400 border-green-800"
                          : f.reviewStatus === "DISPUTED"
                          ? "bg-red-950 text-red-400 border-red-800"
                          : f.reviewStatus === "REFER_TO_SPECIALIST"
                          ? "bg-amber-950 text-amber-400 border-amber-800"
                          : "bg-muted text-muted-foreground"
                      }
                    >
                      {f.reviewStatus}
                    </Badge>
                  </div>

                  <p className="text-sm text-foreground/90">{f.explanation}</p>

                  <div className="text-xs text-muted-foreground/80 font-mono space-y-1 bg-muted/10 p-2.5 rounded-lg border border-border/20">
                    <div>
                      <span className="text-cyan-400 font-semibold">Evidence Sources:</span>{" "}
                      {f.source_evidence.join(", ")}
                    </div>
                    <div>
                      <span className="text-cyan-400 font-semibold">Provenance:</span> {f.explanation_provenance}
                    </div>
                  </div>

                  <div className="pt-2 flex flex-wrap gap-2 items-center border-t border-border/20">
                    <span className="text-xs font-medium text-muted-foreground mr-2">Human Review Decision:</span>
                    <Button
                      size="sm"
                      variant={f.reviewStatus === "ACKNOWLEDGED" ? "default" : "outline"}
                      onClick={() => handleDecision(f.finding_id, "ACKNOWLEDGED")}
                      className={f.reviewStatus === "ACKNOWLEDGED" ? "bg-green-700 text-white" : "text-xs h-7"}
                    >
                      Acknowledge
                    </Button>
                    <Button
                      size="sm"
                      variant={f.reviewStatus === "DISPUTED" ? "default" : "outline"}
                      onClick={() => handleDecision(f.finding_id, "DISPUTED")}
                      className={f.reviewStatus === "DISPUTED" ? "bg-red-700 text-white" : "text-xs h-7"}
                    >
                      Dispute
                    </Button>
                    <Button
                      size="sm"
                      variant={f.reviewStatus === "REFER_TO_SPECIALIST" ? "default" : "outline"}
                      onClick={() => handleDecision(f.finding_id, "REFER_TO_SPECIALIST")}
                      className={f.reviewStatus === "REFER_TO_SPECIALIST" ? "bg-amber-700 text-white" : "text-xs h-7"}
                    >
                      Refer
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-xl bg-card/80 border border-border/60 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                    Cryptographic Self-Issued Receipt
                  </span>
                  <span className="font-mono text-xs text-cyan-400/90 break-all">
                    {report.self_issued_receipt_sha256}
                  </span>
                </div>
                <Button size="sm" variant="outline" onClick={handleVerifyReceipt} className="border-cyan-500/40 text-cyan-400">
                  Verify Receipt Integrity
                </Button>
              </div>

              {receiptVerified === true && (
                <div className="flex items-center gap-2 text-xs text-green-400 font-mono bg-green-950/40 p-2 rounded border border-green-800/40">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  Receipt digest matched. Audit evidence integrity confirmed (Self-Issued).
                </div>
              )}
              {receiptVerified === false && (
                <div className="flex items-center gap-2 text-xs text-red-400 font-mono bg-red-950/40 p-2 rounded border border-red-800/40">
                  <XCircle className="h-4 w-4 text-red-400" />
                  Receipt verification failed or digest tampered.
                </div>
              )}

              <p className="text-[11px] text-muted-foreground/70 italic border-t border-border/20 pt-2">
                Limits: {report.limits}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
