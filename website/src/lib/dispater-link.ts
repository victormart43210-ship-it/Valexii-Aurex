import type { DispaterReconciliationReport } from "./dispater-contract";

export interface DocumentSourceSummary {
  filename: string;
  source_sha256: string;
  rows: string[];
}

export function dispaterLinkState(
  busy: boolean,
  report: DispaterReconciliationReport | null,
  errorMsg: string | null,
): "LOADING" | "CONNECTED" | "DISCONNECTED" | "UNAVAILABLE" | "ERROR" {
  if (busy) return "LOADING";
  if (report && !errorMsg) return "CONNECTED";
  if (!errorMsg) return "DISCONNECTED";
  if (errorMsg.includes("not configured")) return "UNAVAILABLE";
  if (errorMsg.includes("unreachable")) return "DISCONNECTED";
  return "ERROR";
}

export function storedRunAgrees(
  live: DispaterReconciliationReport,
  stored: DispaterReconciliationReport,
): boolean {
  return (
    stored.run_id === live.run_id &&
    stored.receipt_sha256 === live.receipt_sha256 &&
    stored.financial_summary.confirmed_recovery_usd === "0.00" &&
    stored.financial_summary.identified_exposure_usd === live.financial_summary.identified_exposure_usd
  );
}

export function isCurrentRequest(requestId: number, latestId: number): boolean {
  return requestId === latestId;
}

export const INDUSTRIAL_CHAIN = [
  "company",
  "job",
  "equipment",
  "field_ticket",
  "invoice",
  "contract",
  "approval",
  "payment",
] as const;

export function chainCoverage(
  objects: { object_type: string }[],
): { type: (typeof INDUSTRIAL_CHAIN)[number]; count: number; status: "PRESENT" | "NOT_IN_SOURCE" }[] {
  return INDUSTRIAL_CHAIN.map((type) => {
    const count = objects.filter((item) => item.object_type === type).length;
    return { type, count, status: count > 0 ? "PRESENT" : "NOT_IN_SOURCE" };
  });
}

export function dataOrigin(
  state: "LOADING" | "CONNECTED" | "DISCONNECTED" | "UNAVAILABLE" | "ERROR",
): "LIVE DATA" | "UNAVAILABLE" | "LOADING" {
  if (state === "LOADING") return "LOADING";
  if (state === "CONNECTED") return "LIVE DATA";
  return "UNAVAILABLE";
}

export function documentSourceLine(source: DocumentSourceSummary): string {
  return `${source.filename} · ${source.source_sha256.slice(0, 16)} · rows ${source.rows.join(", ") || "none"}`;
}
