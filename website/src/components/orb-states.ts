export const orbStates = [
  "REST",
  "AWARE",
  "WATCH",
  "DEFEND",
  "CONTAIN",
  "RETURN",
  "UNKNOWN",
  "ERROR",
] as const;
export type OrbState = (typeof orbStates)[number];
export const orbDescriptions: Record<OrbState, string> = {
  REST: "Quiet presentation. No security verdict.",
  AWARE: "An illustrative observation is available for review.",
  WATCH: "Simulated uncertainty needs attention, not automatic action.",
  DEFEND: "Comet presentation only. No device defense is running.",
  CONTAIN: "Illustrative boundary. No app or network has been contained.",
  RETURN: "Presentation returning to rest. History is not erased.",
  UNKNOWN: "Evidence unavailable. Unknown ≠ Safe.",
  ERROR: "Illustrative error. No protection status can be established.",
};
