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
    const { executeDispaterReconciliation } = await import("./dispater.server");

    let dataset: unknown = undefined;
    if (data.fixture === "clean_control_v1") {
      dataset = {
        tenant_id: "demo-oilfield-tenant",
        dataset_type: "SYNTHETIC_ONLY",
        jobs: [
          {
            job_id: "FT-CLEAN-01",
            customer_id: "PERMIAN-ALPHA-CORP",
            service_code: "PRESSURE_PUMPING",
            date: "2026-10-25",
          },
        ],
        rates: [
          {
            rate_id: "RATE-CLEAN-01",
            customer_id: "PERMIAN-ALPHA-CORP",
            service_code: "PRESSURE_PUMPING",
            start: "2026-01-01",
            end: "2026-12-31",
            amount: "3000.00",
          },
        ],
        invoices: [
          {
            invoice_id: "INV-CLEAN-01",
            job_id: "FT-CLEAN-01",
            amount: "3000.00",
            status: "open",
          },
        ],
        payments: [],
      };
    }

    const report: DispaterReconciliationReport = await executeDispaterReconciliation(
      {
        serviceUrl:
          process.env["AUREX_SERVICE_URL"] ??
          process.env["AUREX_STAGING_SERVICE_URL"] ??
          "http://127.0.0.1:8000",
        serviceToken:
          process.env["AUREX_SERVICE_TOKEN"] ??
          process.env["AUREX_STAGING_SERVICE_TOKEN"] ??
          "0".repeat(32),
      },
      dataset,
    );
    return report;
  });
