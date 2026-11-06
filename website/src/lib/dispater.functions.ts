// Server functions for DISPATER reconciliation.
import { createServerFn } from "@tanstack/react-start";
import { executeDispaterReconciliation, getFixture } from "./dispater.server";

export const runDispaterAudit = createServerFn({ method: "POST" })
  .validator((d: unknown) => {
    const fixture =
      typeof d === "object" && d !== null && "fixture" in d && typeof (d as { fixture: unknown }).fixture === "string"
        ? (d as { fixture: string }).fixture
        : "towing_recovery_v1";
    if (
      fixture !== "towing_recovery_v1" &&
      fixture !== "oilfield_demo_v1" &&
      fixture !== "clean_control_v1"
    ) {
      throw new Error("Invalid fixture requested");
    }
    return { fixture: fixture as "towing_recovery_v1" | "oilfield_demo_v1" | "clean_control_v1" };
  })
  .handler(async ({ data }) => {
    const config = {
      serviceUrl: process.env.AUREX_SERVICE_URL,
      serviceToken: process.env.AUREX_SERVICE_TOKEN,
      tenantId: process.env.AUREX_DISPATER_TENANT || "demo-towing-tenant",
      allowLocal: process.env.NODE_ENV !== "production",
    };
    const dataset = getFixture(data.fixture);
    return await executeDispaterReconciliation(config, dataset);
  });
