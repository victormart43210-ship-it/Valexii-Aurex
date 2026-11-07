import { describe, expect, it } from "vitest";
import {
  XAELI_INFERENCE_TIMEOUT_MS,
  classifyXaeliHttp,
  xaeliProbeAllowed,
  xaeliStagingGate,
} from "./xaeli-status";

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
      errorCode: "MODEL_UNAVAILABLE",
    });
    expect(classifyXaeliHttp(200, { execution: "FAIL", generated_answer: "text" }).live).toBe(
      false,
    );
    expect(
      classifyXaeliHttp(200, { execution: "PASS", generated_answer: "Synthetic uncertainty." }),
    ).toEqual({
      status: "connected",
      live: true,
      answer: "Synthetic uncertainty.",
      errorCode: null,
    });
  });

  it("keeps a configured gate from looking connected before a model answers", () => {
    const env = {
      stagingEnabled: "1",
      operatorApproved: "1",
      qwenBaseUrl: "http://qwen-private-staging.railway.internal:8080/v1",
      serviceUrl: "https://staging.example",
      serviceToken: "a".repeat(32),
    };
    expect(xaeliProbeAllowed(env)).toBe(true);
    expect(xaeliStagingGate(env)).toEqual({ status: "ready", live: false, answer: null });
    expect(XAELI_INFERENCE_TIMEOUT_MS).toBeGreaterThanOrEqual(90_000);
    expect(XAELI_INFERENCE_TIMEOUT_MS).toBeLessThanOrEqual(120_000);
  });

  it("shows only an allowlisted failure code", () => {
    expect(
      classifyXaeliHttp(200, {
        execution: "FAIL",
        generated_answer: null,
        error_code: "MODEL_IDENTITY_MISMATCH",
      }).errorCode,
    ).toBe("MODEL_IDENTITY_MISMATCH");
    expect(
      classifyXaeliHttp(200, { execution: "FAIL", error_code: "Bearer secret" }).errorCode,
    ).toBeNull();
  });
});
