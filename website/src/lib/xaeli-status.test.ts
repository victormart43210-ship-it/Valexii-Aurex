import { describe, expect, it } from "vitest";
import { classifyXaeliHttp, xaeliProbeAllowed } from "./xaeli-status";

describe("xaeli staging link", () => {
  it("does not probe or invent an answer when staging is off", () => {
    expect(xaeliProbeAllowed({})).toBe(false);
    expect(xaeliProbeAllowed({ stagingEnabled: "1", operatorApproved: "1" })).toBe(false);
  });

  it("accepts only a real passing answer and rejects a recovery claim shape", () => {
    expect(classifyXaeliHttp(503, { generated_answer: "pretend" })).toEqual({
      status: "unavailable",
      live: false,
      answer: null,
    });
    expect(classifyXaeliHttp(200, { execution: "FAIL", generated_answer: "text" }).live).toBe(false);
    expect(
      classifyXaeliHttp(200, { execution: "PASS", generated_answer: "Synthetic uncertainty." }),
    ).toEqual({ status: "connected", live: true, answer: "Synthetic uncertainty." });
  });
});
