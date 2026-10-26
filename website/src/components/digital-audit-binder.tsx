import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, FileCheck, ShieldCheck } from "lucide-react";

export function DigitalAuditBinder() {
  const [downloading, setDownloading] = useState(false);
  const [exportComplete, setExportComplete] = useState(false);

  const handleExportBinder = () => {
    setDownloading(true);
    setTimeout(() => {
      const syntheticBinderData = {
        audit_scope: "Commercial Towing Field Record & Readiness Audit",
        operator: "Permian Recovery Services (Fictional)",
        reporting_period: "Q3/Q4 2026",
        generated_at: new Date().toISOString(),
        evidence_inventory: [
          { record_id: "demo-driver-01", category: "driver_qualification", sha256: "a".repeat(64) },
          { record_id: "demo-vehicle-01", category: "vehicle_inspection", sha256: "b".repeat(64) },
          { record_id: "demo-maint-01", category: "maintenance", sha256: "c".repeat(64) },
          { record_id: "demo-maint-02", category: "maintenance", sha256: "d".repeat(64) },
          { record_id: "demo-ticket-01", category: "service_ticket", sha256: "unknown" },
        ],
        discrepancy_summary: {
          expired_records: 1,
          conflicting_digests: 1,
          unverified_records: 1,
          missing_records: 1,
        },
        integrity_manifest: {
          receipt_id: "rcpt-towing-20261026-binder",
          verifier: "AUREX-OX-CUSTOS-V1",
          evidence_digest: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          authority: "ADVISORY_ONLY_NO_CERTIFICATION",
        },
      };

      const blob = new Blob([JSON.stringify(syntheticBinderData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "DISPATER_Synthetic_Audit_Binder_20261026.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setDownloading(false);
      setExportComplete(true);
    }, 800);
  };

  return (
    <Card className="border-gold/30 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-gold/20 pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <Badge variant="outline" className="border-gold text-gold">
              DIGITAL AUDIT BINDER EXPORT
            </Badge>
            <CardTitle className="mt-1 text-xl font-bold text-white">Generate Complete Audit Package</CardTitle>
          </div>
          <Button
            onClick={handleExportBinder}
            disabled={downloading}
            className="bg-gold text-slate-950 hover:bg-gold/80 font-bold"
          >
            <Download className="mr-2 h-4 w-4" />
            {downloading ? "Packaging Binder..." : "Export Audit Binder (.json)"}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-3 font-mono text-xs">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="p-3 bg-slate-900 rounded border border-slate-800">
            <span className="text-slate-400">Reporting Scope</span>
            <p className="text-sm font-semibold text-white mt-1">Permian Towing Q4 Audit</p>
          </div>
          <div className="p-3 bg-slate-900 rounded border border-slate-800">
            <span className="text-slate-400">Evidence Records</span>
            <p className="text-sm font-semibold text-cyan mt-1">5 Synthetic Records</p>
          </div>
          <div className="p-3 bg-slate-900 rounded border border-slate-800">
            <span className="text-slate-400">Integrity Verifier</span>
            <p className="text-sm font-semibold text-gold mt-1">AUREX-OX-CUSTOS-V1</p>
          </div>
        </div>

        {exportComplete && (
          <div className="flex items-center justify-between p-3 rounded bg-emerald-950/30 border border-emerald-500/40 text-emerald-300">
            <div className="flex items-center space-x-2">
              <FileCheck className="h-4 w-4 text-emerald-400" />
              <span>Audit Binder exported successfully (DISPATER_Synthetic_Audit_Binder_20261026.json)</span>
            </div>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
