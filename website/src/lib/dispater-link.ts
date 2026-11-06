import type { DispaterReconciliationReport } from "./dispater-contract";

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
