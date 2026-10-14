import { describe, expect, it } from "vitest";
import { aurexSampleRun, disabledAurexClient, displayState, type AurexRunRecord } from "@/lib/aurex-integration";

describe("AUREX fail-closed display", () => {
  it("shows the sample as NOT VERIFIED / HOLD / NONE / LOCAL_PRACTICE_ONLY", () => {
    expect(displayState(aurexSampleRun)).toEqual({
      verification: "NOT VERIFIED", authority: "HOLD", effect: "NONE", scope: "LOCAL_PRACTICE_ONLY",
    });
  });
  it("fails closed for missing records", () => {
    expect(displayState(null).authority).toBe("HOLD");
    expect(displayState(undefined).verification).toBe("NOT VERIFIED");
  });
  it("never promotes a synthetic sample even if it claims verification", () => {
    const forged: AurexRunRecord = { ...aurexSampleRun, verification: "INDEPENDENTLY_VERIFIED",
      authority: "AUTHORIZED", effect: "BOUNDED_EFFECT_RECORDED", scope: "INDEPENDENTLY_VERIFIED" };
    expect(displayState(forged).authority).toBe("HOLD");
    expect(displayState(forged).scope).toBe("LOCAL_PRACTICE_ONLY");
  });
  it("keeps unverified hosted records on HOLD", () => {
    expect(displayState({ ...aurexSampleRun, source: "HOSTED_API", authority: "AUTHORIZED" }).authority).toBe("HOLD");
  });
  it("default client is disabled and returns nothing", async () => {
    expect(disabledAurexClient.status).toBe("DISABLED_UNCONFIGURED");
    expect(await disabledAurexClient.getRun("x")).toBeNull();
  });
});
