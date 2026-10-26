import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertCircle, CheckCircle2, HelpCircle, XCircle } from "lucide-react";

export interface WorkQueueItem {
  id: string;
  category: string;
  description: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  status: "ACKNOWLEDGED" | "DISPUTED" | "NEEDS_EVIDENCE" | "RESOLVED_BY_HUMAN_REVIEW";
  assignedTo: string;
  dueDate: string;
}

const DEFAULT_WORK_QUEUE: WorkQueueItem[] = [
  {
    id: "wq-001",
    category: "vehicle_inspection",
    description: "Annual Brake & Rigging Inspection expired on Unit #104 (Heavy Wrecker)",
    severity: "CRITICAL",
    status: "NEEDS_EVIDENCE",
    assignedTo: "Operations Manager (Jane Doe)",
    dueDate: "2026-10-28",
  },
  {
    id: "wq-002",
    category: "maintenance",
    description: "Conflicting Winch Pressure Test Log Digests (Winch A vs Winch B Log)",
    severity: "HIGH",
    status: "ACKNOWLEDGED",
    assignedTo: "Fleet Director (John Smith)",
    dueDate: "2026-10-29",
  },
  {
    id: "wq-003",
    category: "service_ticket",
    description: "Field Ticket #9042 source SHA256 unverified against evidence ledger",
    severity: "MEDIUM",
    status: "DISPUTED",
    assignedTo: "Audit Specialist (Alex Vance)",
    dueDate: "2026-10-30",
  },
];

export function OfficeWorkQueue() {
  const [items, setItems] = useState<WorkQueueItem[]>(DEFAULT_WORK_QUEUE);

  const updateStatus = (id: string, newStatus: WorkQueueItem["status"]) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: newStatus } : item))
    );
  };

  return (
    <Card className="border-cyan/30 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-cyan/20 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <Badge variant="outline" className="border-cyan text-cyan">
              OPERATIONAL WORK QUEUE
            </Badge>
            <CardTitle className="mt-1 text-xl font-bold text-white">Office Action Queue & Dispositions</CardTitle>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Unresolved Items: {items.filter((i) => i.status !== "RESOLVED_BY_HUMAN_REVIEW").length} / {items.length}
          </span>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-slate-400 text-xs font-mono">ID</TableHead>
              <TableHead className="text-slate-400 text-xs">Description</TableHead>
              <TableHead className="text-slate-400 text-xs">Severity</TableHead>
              <TableHead className="text-slate-400 text-xs">Review Disposition</TableHead>
              <TableHead className="text-slate-400 text-xs">Action Controls</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id} className="border-slate-800/60">
                <TableCell className="font-mono text-xs text-cyan">{item.id}</TableCell>
                <TableCell className="text-xs text-slate-200 space-y-1">
                  <p className="font-medium">{item.description}</p>
                  <p className="text-[10px] text-slate-500 font-mono">Assigned: {item.assignedTo} | Due: {item.dueDate}</p>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={
                      item.severity === "CRITICAL"
                        ? "border-rose-500 text-rose-400"
                        : item.severity === "HIGH"
                        ? "border-amber text-amber"
                        : "border-slate-600 text-slate-400"
                    }
                  >
                    {item.severity}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={
                      item.status === "RESOLVED_BY_HUMAN_REVIEW"
                        ? "border-emerald-500 text-emerald-400"
                        : item.status === "NEEDS_EVIDENCE"
                        ? "border-amber text-amber"
                        : "border-cyan text-cyan"
                    }
                  >
                    {item.status.replace(/_/g, " ")}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-1">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => updateStatus(item.id, "ACKNOWLEDGED")}
                      className="h-7 px-2 text-[10px] border-slate-700 text-slate-300"
                    >
                      Acknowledge
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => updateStatus(item.id, "NEEDS_EVIDENCE")}
                      className="h-7 px-2 text-[10px] border-amber/50 text-amber"
                    >
                      Request Evidence
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => updateStatus(item.id, "RESOLVED_BY_HUMAN_REVIEW")}
                      className="h-7 px-2 text-[10px] border-emerald-500/50 text-emerald-400"
                    >
                      Resolve
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
