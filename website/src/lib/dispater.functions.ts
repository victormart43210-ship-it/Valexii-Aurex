import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { type DispaterReconciliationReport } from "./dispater-contract";

export const runDispaterDemoReconciliation = createServerFn({ method: "POST" })
  .validator((input: unknown) => {
    return z
      .object({
        fixture: z.enum(["oilfield_demo_v1", "clean_control_v1"]).default("oilfield_demo_v1"),
      })
      .parse(input);
  })
  .handler(async ({ data }) => {
    const { executeDispaterReconciliation, getFixture } = await import("./dispater.server");
    const report: DispaterReconciliationReport = await executeDispaterReconciliation(
      {
        serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
        serviceToken:
          process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
        tenantId: process.env["DISPATER_TENANT_ID"],
        allowLocal: process.env["NODE_ENV"] !== "production",
      },
      getFixture(data.fixture),
    );
    return report;
  });

export const admitSyntheticDispaterCsv = createServerFn({ method: "POST" })
  .validator((input: unknown) => z.object({}).parse(input ?? {}))
  .handler(async () => {
    const { executeDispaterDocument } = await import("./dispater.server");
    const admitted = await executeDispaterDocument({
      serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
      serviceToken: process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
      tenantId: process.env["DISPATER_TENANT_ID"],
      allowLocal: process.env["NODE_ENV"] !== "production",
    });
    return admitted.report;
  });

export const readDispaterStoredRun = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z.object({ runId: z.string().regex(/^run-[0-9a-f]{32}$/) }).parse(input),
  )
  .handler(async ({ data }) => {
    const { readDispaterRun } = await import("./dispater.server");
    return readDispaterRun(
      {
        serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
        serviceToken:
          process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
        tenantId: process.env["DISPATER_TENANT_ID"],
        allowLocal: process.env["NODE_ENV"] !== "production",
      },
      data.runId,
    );
  });
